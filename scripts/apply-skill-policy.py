#!/usr/bin/env python3
"""Validate and apply the tracked skill exposure policy."""

import argparse
import os
import sys

# Permit direct execution from scripts/ without making scripts a package.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skill_policy import (  # noqa: E402
    PolicyError,
    apply_omp_local,
    load_policy,
    materialise_external_skill,
    validate_inventory,
)


def _parser():
    parser = argparse.ArgumentParser(prog="apply-skill-policy.py")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-source")
    validate.add_argument("--policy", required=True)
    validate.add_argument("--name", required=True)
    validate.add_argument("--source", required=True)

    materialise = sub.add_parser("materialise")
    materialise.add_argument("--policy", required=True)
    materialise.add_argument("--name", required=True)
    materialise.add_argument("--source", required=True)
    materialise.add_argument("--output", required=True)

    local = sub.add_parser("apply-omp-local")
    local.add_argument("--policy", required=True)
    local.add_argument("--omp-root", required=True)

    all_sources = sub.add_parser("validate-all")
    all_sources.add_argument("--policy", required=True)
    all_sources.add_argument("--repo-root", required=True)
    all_sources.add_argument("--vendor-root", required=True)
    all_sources.add_argument("--omp-root", required=True)
    return parser


def _entry(policy, name):
    try:
        entry = dict(policy["skills"][name])
    except KeyError as exc:
        raise PolicyError("unknown shared skill: %s" % name) from exc
    entry["name"] = name
    return entry


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        policy = load_policy(args.policy)
        if args.command == "validate-source":
            # materialise performs all source validation; use an impossible
            # output only after validation would be unsafe, so call the small
            # public operation directly through the library helper.
            from skill_policy import _validate_source

            _validate_source(args.source, _entry(policy, args.name))
            return 0
        if args.command == "materialise":
            materialise_external_skill(args.source, args.output, _entry(policy, args.name))
            return 0
        if args.command == "apply-omp-local":
            apply_omp_local(args.omp_root, policy["ompLocalSkills"])
            return 0
        errors = validate_inventory(policy, args.repo_root, args.vendor_root, args.omp_root)
        if errors:
            for error in errors:
                print("error: %s" % error, file=sys.stderr)
            return 1
        return 0
    except (PolicyError, OSError, UnicodeError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
