#!/usr/bin/env python3
"""Consolidate a finished session into the memory vault, off the critical path.

Plan item D of plans/2026-07-26-memory-latency.md. `/remember` is a twelve-turn
read-modify-write run inline in a session whose context is already large. This
runs the same write path when nobody is waiting: at SessionEnd, in a detached
background process, so the session itself never blocks on it.

Two processes, one file:

  hook mode   (no argv)          -- what settings.json invokes on SessionEnd.
                                    Pure Python, no LLM, no network. Applies a
                                    deliberately dumb gate, takes a lock, spawns
                                    the worker, returns. Bounded by GATE_DEADLINE.
  worker mode (--run <transcript>) -- detached child. Shells out to `claude -p`
                                    to do the actual judging and writing, holds
                                    the lock for its lifetime, logs to LOG_PATH.

**The gate does not judge whether anything durable happened.** It cannot: that
is semantic work, and a keyword regex pretending otherwise would spam the vault
with junk from every session that happened to say "decided". The gate only asks
"was this session substantial enough to be worth one Sonnet call" -- enough
human turns, enough human characters. The real durable-or-not judgement is made
by the headless `claude -p` run, which is explicitly instructed to write nothing
and exit when the answer is no. False positives therefore cost one cheap model
call, not a junk vault commit.

Failure posture, per this repo's CLAUDE.md: never blocks, always exits 0, never
prints. SessionEnd cannot block a session in the first place (code.claude.com
/docs/en/hooks: "Can block? No"), but a traceback on stderr still surfaces as a
hook error in the transcript, so everything is wrapped.

Recursion is the sharp edge: the worker's own `claude -p` run fires SessionEnd
when it finishes. Guarded twice -- the GUARD_ENV marker in the child's
environment (inherited by that run's own hook subprocess) and the documented
`reason: "prompt_input_exit"` a completed headless run reports.

Env overrides exist so the tests can run hermetically, never touching the real
vault or the real `claude` binary:

  MEMORY_CONSOLIDATE_CLAUDE_BIN   binary the worker execs        (default: claude)
  MEMORY_CONSOLIDATE_VAULT        vault path                     (default: ~/dev/claude-memory)
  MEMORY_CONSOLIDATE_STATE_DIR    lock/stamp/log directory       (default: /tmp)
  MEMORY_CONSOLIDATE_DEADLINE     worker wall-clock seconds      (default: 900)
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

# realpath, not abspath: invoked through the ~/.claude/hooks symlink, and
# resolving it lands in the repo checkout next to context_size.py. Same reason
# context-budget.py does it.
_HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, _HERE)

# Guarded, unlike context-budget.py's bare import: that one is a UserPromptSubmit
# hook whose failure is loud and immediate, this one runs at session end where a
# traceback is both useless and unnoticed. A half-installed checkout (the module
# missing next to this file) must degrade to "never consolidate", not to exit 1.
# scripts/test-memory-consolidate.sh stages exactly that case.
try:
    from context_size import resolve_transcript
except Exception:       # pragma: no cover - exercised by the broken-install test
    resolve_transcript = None

# --- gate thresholds -------------------------------------------------------
# Deliberately blunt. Raising these makes the hook fire less often; it never
# makes it smarter. Smartness lives in the model call downstream.
MIN_HUMAN_TURNS = 4        # a real working session, not a one-question drive-by
MIN_HUMAN_CHARS = 500      # ...and one where the human actually said something
GATE_DEADLINE = 1.5        # seconds the hook may spend scanning before giving up
MAX_SCAN_BYTES = 32 << 20  # ...and the transcript bytes it may read doing so

# --- worker bounds ---------------------------------------------------------
DEFAULT_DEADLINE = 900     # hard wall clock on the headless run
LOCK_MAX_AGE = 3600        # a lock older than this is assumed abandoned
MAX_LOG_BYTES = 1 << 20    # truncate the log rather than grow it forever

GUARD_ENV = "CLAUDE_MEMORY_CONSOLIDATE"

# Reasons we act on. `resume` is a suspend rather than an end; `logout` and
# `bypass_permissions_disabled` are not natural stopping points for the work;
# `prompt_input_exit` is a completed headless run, i.e. very possibly our own
# worker. Anything unrecognised is treated as not-our-business.
ACT_ON_REASONS = {"clear", "other", "", None}


def _state_dir():
    return os.environ.get("MEMORY_CONSOLIDATE_STATE_DIR") or "/tmp"


def _vault():
    return os.environ.get("MEMORY_CONSOLIDATE_VAULT") or os.path.expanduser(
        "~/dev/claude-memory"
    )


def _lock_path():
    return os.path.join(_state_dir(), "claude-memory-consolidate.lock")


def _log_path():
    return os.path.join(_state_dir(), "claude-memory-consolidate.log")


def _stamp_path(transcript):
    key = hashlib.sha1(transcript.encode("utf-8", "replace")).hexdigest()[:16]
    return os.path.join(_state_dir(), f"claude-memory-consolidate-{key}.stamp")


def _log(message):
    """Append one timestamped line. Never raises, never touches stdout."""
    try:
        path = _log_path()
        try:
            if os.path.getsize(path) > MAX_LOG_BYTES:
                os.remove(path)
        except OSError:
            pass
        with open(path, "a") as fh:
            fh.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
    except Exception:
        pass


# --- transcript scanning ---------------------------------------------------

_NON_HUMAN_PREFIXES = (
    "<command-",
    "<local-command",
    "<system-reminder",
    "<user-prompt-submit",
    "<bash-",
)


def _human_text(entry):
    """The human's own words in one transcript entry, or "".

    Excludes tool results (which are also `type: user`), sidechain turns,
    meta/attachment entries, and the XML-ish envelopes slash commands and hooks
    inject as pseudo-user messages.
    """
    if not isinstance(entry, dict) or entry.get("type") != "user":
        return ""
    if entry.get("isMeta") or entry.get("isSidechain") or entry.get("isCompactSummary"):
        return ""
    message = entry.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        parts = [content]
    elif isinstance(content, list):
        parts = [
            block.get("text")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
    else:
        return ""
    text = "\n".join(p for p in parts if isinstance(p, str)).strip()
    if not text:
        return ""
    if text.lower().startswith(_NON_HUMAN_PREFIXES):
        return ""
    return text


def scan(path, deadline=GATE_DEADLINE):
    """(human turn count, human char count, remembered) for a transcript.

    `remembered` means the session already invoked `/remember` explicitly, in
    which case the vault has the material and consolidating again would just
    produce a near-duplicate page. Suppression only -- it can never cause a
    write, only prevent one.

    Bounded twice: MAX_SCAN_BYTES and a wall-clock deadline. Hitting either
    returns what was counted so far, which can only under-count, i.e. can only
    fail toward not firing.
    """
    turns = 0
    chars = 0
    remembered = False
    started = time.time()
    read = 0
    try:
        with open(path, errors="ignore") as fh:
            for line in fh:
                read += len(line)
                if read > MAX_SCAN_BYTES or time.time() - started > deadline:
                    break
                if "/remember" in line:
                    remembered = True
                if '"user"' not in line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                text = _human_text(entry)
                if text:
                    turns += 1
                    chars += len(text)
    except Exception:
        return 0, 0, False
    return turns, chars, remembered


# --- mutual exclusion ------------------------------------------------------

def _pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True     # exists, owned by someone else
    except Exception:
        return True     # unknowable: assume alive, i.e. do not steal
    return True


def _lock_is_stale(path):
    """True if an existing lock belongs to a dead process or is ancient."""
    try:
        age = time.time() - os.path.getmtime(path)
    except OSError:
        return True     # vanished under us
    if age > LOCK_MAX_AGE:
        return True
    try:
        with open(path) as fh:
            data = json.load(fh)
        pid = int(data.get("pid") or 0)
    except Exception:
        # Unparseable lock: only steal it once it is clearly old, so a lock
        # caught mid-write by a concurrent hook is not immediately stolen.
        return age > 60
    if pid <= 0:
        return age > 60
    return not _pid_alive(pid)


def acquire_lock():
    """Create the lock exclusively, or return None. One writer, machine-wide.

    O_EXCL is the exclusion; the PID inside is only for staleness. Written by
    the hook before the worker exists, then rewritten with the worker's PID --
    so the window where the lock names a not-yet-spawned process is measured in
    milliseconds and is covered by the 60s floor in _lock_is_stale.
    """
    path = _lock_path()
    for _ in range(2):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            if not _lock_is_stale(path):
                return None
            try:
                os.remove(path)
            except OSError:
                return None
            continue
        except Exception:
            return None
        try:
            os.write(fd, json.dumps({"pid": os.getpid(), "at": time.time()}).encode())
        except Exception:
            pass
        finally:
            os.close(fd)
        return path
    return None


def write_lock(path, pid, transcript):
    try:
        with open(path, "w") as fh:
            json.dump({"pid": pid, "at": time.time(), "transcript": transcript}, fh)
    except Exception:
        pass


def release_lock(path):
    try:
        os.remove(path)
    except OSError:
        pass


# --- the prompt the worker hands to the headless run -----------------------

PROMPT = """\
You are running unattended, after a Claude Code session ended. Nobody is
watching and nobody will answer a question, so do not ask one.

The session transcript is at:
  {transcript}
It was working in: {cwd}

It is JSONL, one entry per line, and can be large. Do NOT read it whole. Pull
out the human turns and your own summarising replies first, e.g.:

  jq -r 'select(.type=="user" and (.isMeta|not) and (.isSidechain|not))
         | .message.content
         | if type=="string" then . else (.[]?|select(.type=="text").text) end' \\
    {transcript} | head -c 40000

Then decide ONE thing: did this session produce material that is durable and
worth keeping in the memory vault at {vault}?

Durable means: a decision with its reasoning, a stated preference, a project
status change, non-obvious configuration, a fact that was expensive to
establish. NOT durable: transient session state, anything git history already
records, routine code edits, debugging that ended in the obvious answer, or a
session that was mostly you reading files.

Be strict. The default answer is no. A junk page costs more than a missed one,
because a vault nobody trusts is a vault nobody reads.

If the answer is no: print exactly NOTHING_DURABLE and stop. Write nothing,
commit nothing.

If the answer is yes, do the same five steps `/remember` does, yourself, inline
-- you are already a background process, so do not dispatch a subagent:

1. `date +%Y-%m-%d-%H%M` for the real timestamp, never guessed.
2. Write the distilled material to a NEW file
   {vault}/raw/YYYY-MM-DD-HHMM-short-slug.md, slug lowercase-kebab-case. `raw/`
   is immutable: add a file, never edit one. Include a `sources:` line naming
   this session's transcript path so the provenance survives.
3. Run INGEST on it: read {vault}/CLAUDE.md and the full procedure in
   {vault}/.claude/commands/ingest.md and follow them exactly -- create or
   update the relevant wiki/ pages, add backlinks, update wiki/index.md, append
   to wiki/log.md. Prefer updating an existing page over a near-duplicate, and
   respect the supersession rules.
4. Commit in {vault} ONE dedicated commit containing only this consolidation,
   with a subject beginning `memory: consolidate` so the diff is reviewable on
   its own. Do not amend, do not fold in unrelated working-tree changes, and if
   the vault has pre-existing uncommitted changes, stage only your own paths.
5. Print one line: the raw file written and the wiki pages touched.

Absolute bounds:
- Touch nothing outside {vault}. Never commit, stage, or modify anything in
  {cwd} or any other repository.
- Never run `git push`.
- Step 2 is the step that must not fail. If INGEST or the commit fails, leave
  the raw/ file on disk and say so. A half-ingested vault is recoverable; a
  lost raw file is not.
"""


def run_worker(transcript, cwd, lock_path):
    """Detached child: run the headless consolidation, then drop the lock."""
    vault = _vault()
    binary = os.environ.get("MEMORY_CONSOLIDATE_CLAUDE_BIN") or "claude"
    resolved = shutil.which(binary) or (binary if os.path.isabs(binary) else None)
    if not resolved:
        _log(f"worker: no such binary {binary!r}, giving up")
        return
    try:
        deadline = int(os.environ.get("MEMORY_CONSOLIDATE_DEADLINE") or DEFAULT_DEADLINE)
    except ValueError:
        deadline = DEFAULT_DEADLINE

    prompt = PROMPT.format(transcript=transcript, cwd=cwd or "(unknown)", vault=vault)
    argv = [
        resolved,
        "-p", prompt,
        "--model", "sonnet",
        "--max-turns", "40",
        "--add-dir", vault,
        "--allowedTools",
        "Read,Write,Edit,Glob,Grep,Bash(date:*),Bash(jq:*),Bash(git add:*),"
        "Bash(git commit:*),Bash(git status:*),Bash(git diff:*),Bash(git log:*)",
    ]
    env = dict(os.environ)
    env[GUARD_ENV] = "1"      # so this run's own SessionEnd hook stands down

    _log(f"worker: start pid={os.getpid()} transcript={transcript}")
    started = time.time()
    try:
        done = subprocess.run(
            argv,
            cwd=vault if os.path.isdir(vault) else None,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=deadline,
        )
        tail = (done.stdout or "").strip().replace("\n", " ")[-500:]
        _log(
            f"worker: exit={done.returncode} in {time.time() - started:.1f}s :: {tail}"
        )
        if done.returncode != 0:
            _log(f"worker: stderr :: {(done.stderr or '').strip()[-500:]}")
    except subprocess.TimeoutExpired:
        _log(f"worker: TIMEOUT after {deadline}s, killed")
    except Exception as exc:
        _log(f"worker: failed {type(exc).__name__}: {exc}")
    finally:
        release_lock(lock_path)


# --- hook mode -------------------------------------------------------------

def main():
    # 1. Recursion guard. Our own worker's `claude -p` run ends in a SessionEnd
    #    of its own, and its hook subprocess inherits this marker.
    if os.environ.get(GUARD_ENV):
        return

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(payload, dict):
        return

    # 2. Second recursion guard, documented rather than inferred:
    #    prompt_input_exit is what a finished headless run reports.
    if payload.get("reason") not in ACT_ON_REASONS:
        return

    if resolve_transcript is None:
        _log("hook: context_size.py not importable, standing down")
        return
    transcript = resolve_transcript(payload)
    if not transcript:
        return

    vault = _vault()
    if not os.path.isdir(os.path.join(vault, ".git")):
        return      # no vault on this machine: nothing to consolidate into

    turns, chars, remembered = scan(transcript)
    if remembered:
        return      # the session already wrote deliberately; do not duplicate
    if turns < MIN_HUMAN_TURNS or chars < MIN_HUMAN_CHARS:
        return

    # 3. Do not re-consolidate the same material. SessionEnd fires again on
    #    quit after a /clear, on the same transcript. Only the growth since
    #    last time counts, and it must clear the gate on its own.
    stamp = _stamp_path(transcript)
    previous = 0
    try:
        with open(stamp) as fh:
            previous = int((json.load(fh) or {}).get("turns") or 0)
    except Exception:
        previous = 0
    if turns - previous < MIN_HUMAN_TURNS:
        return

    lock = acquire_lock()
    if lock is None:
        return      # another session is consolidating; one writer at a time

    try:
        child = subprocess.Popen(
            [sys.executable, os.path.realpath(__file__), "--run",
             transcript, payload.get("cwd") or ""],
            start_new_session=True,     # survives the dying session's process group
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
    except Exception as exc:
        _log(f"hook: spawn failed {type(exc).__name__}: {exc}")
        release_lock(lock)
        return

    write_lock(lock, child.pid, transcript)
    try:
        with open(stamp, "w") as fh:
            json.dump({"turns": turns, "at": time.time()}, fh)
    except Exception:
        pass
    _log(f"hook: spawned pid={child.pid} turns={turns} chars={chars}")
    # Return immediately. The child is detached and unwaited by design.


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--run":
            run_worker(
                sys.argv[2] if len(sys.argv) > 2 else "",
                sys.argv[3] if len(sys.argv) > 3 else "",
                _lock_path(),
            )
        else:
            main()
    except Exception:
        pass    # consolidation is never worth a hook error at the end of a session
