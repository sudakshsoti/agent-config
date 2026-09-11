# Local browser and image inspection

Prefer the project's already-working browser tooling. In this shared Codex/Pi setup, `pi-playwright` supplies Playwright and Chromium is already installed. No frontend framework is needed to render a plain HTML file.

## Existing CLI

Check the executable before using it. The package-local `pw.js` wrapper can fail when its dependencies are hoisted; the installed dependency's CLI is the working route in the validated environment. Do not patch the installed package or add a second browser stack to work around that layout.

```sh
artifact_browser_cli="$HOME/.pi/agent/npm/node_modules/.bin/playwright-cli"
test -x "$artifact_browser_cli"
"$artifact_browser_cli" --help
```

Run from the artifact directory. Start a local HTTP server for files requiring module loading or fetch, using the project's existing server or `python3 -m http.server 8765 --bind 127.0.0.1`. Use an available port and shut down only the server you started. A simple independent document may use a file URL if the browser supports it.

Choose a unique session name for this artifact so concurrent work cannot navigate the same browser tab. For example:

```sh
artifact_browser_session="frontend-artifact-$$"
"$artifact_browser_cli" -s="$artifact_browser_session" open --browser=chromium http://127.0.0.1:8765/
"$artifact_browser_cli" -s="$artifact_browser_session" resize 390 844
"$artifact_browser_cli" -s="$artifact_browser_session" screenshot --filename mobile.png
"$artifact_browser_cli" -s="$artifact_browser_session" resize 1440 1000
"$artifact_browser_cli" -s="$artifact_browser_session" screenshot --filename desktop.png
"$artifact_browser_cli" -s="$artifact_browser_session" screenshot --filename full-page.png --full-page
"$artifact_browser_cli" -s="$artifact_browser_session" console error
"$artifact_browser_cli" -s="$artifact_browser_session" close
```

Use `snapshot`, the documented interaction commands and `run-code` for requested controls, computed styles and layout measurements. Check `--help` for the installed version before assuming a flag exists. Keep screenshots inside the chosen artifact directory; a session's temporary directory is not a permanent deliverable. Close only your own session, not all browsers.

If this executable or Chromium is absent, inspect the available project tooling first. Report the missing prerequisite rather than claiming capture succeeded. Do not install a dependency or a browser just because a different package layout was assumed.

## Actually inspect the pixels

Codex: open each saved PNG using `view_image` with its absolute local path. For the selected language's reference, resolve `screenshots/<language>/reference.png` relative to this skill's root.

Pi: its file input supports local image attachments. Verify image support in `pi --list-models`, then attach the image to the active conversation or use the CLI's `@/absolute/path/image.png` file input. In a non-interactive child run, include the image paths with the review prompt and close stdin. A text-only model or a tool that merely saves PNGs cannot perform visual review.

The implementation model can remain unchanged when a separate image-capable reviewer is needed. Preserve the current user's model settings; use per-run overrides when testing. Keep the reviewer brief tied to the artifact's job and selected profile, and provide the actual screenshots rather than a description of how the page should look.
