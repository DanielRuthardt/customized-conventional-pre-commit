import argparse
import sys

from conventional_pre_commit import output
from conventional_pre_commit.format import CustomizedConventionalCommit

RESULT_SUCCESS = 0
RESULT_FAIL = 1


def main(argv=[]):
    parser = argparse.ArgumentParser(
        prog="conventional-pre-commit", description="Check a git commit message for Customized Conventional Commits formatting using GitMoji."
    )
    parser.add_argument(
        "emojis", type=str, nargs="*", default=None, help="Optional list of additional GitMoji emojis to support"
    )
    parser.add_argument("input", type=str, help="A file containing a git commit message")
    parser.add_argument("--no-color", action="store_false", default=True, dest="color", help="Disable color in output.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Force commit to strictly follow Customized Conventional Commits formatting. Disallows fixup! and merge commits.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="Print more verbose error output.",
    )

    if len(argv) < 1:
        argv = sys.argv[1:]

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return RESULT_FAIL

    try:
        with open(args.input, encoding="utf-8") as f:
            commit_msg = f.read()
    except UnicodeDecodeError:
        print(output.unicode_decode_error(args.color))
        return RESULT_FAIL

    # Use custom emojis if provided, otherwise use default
    emojis = args.emojis if args.emojis else None

    commit = CustomizedConventionalCommit(commit_msg, emojis)

    if not args.strict:
        if commit.has_autosquash_prefix():
            return RESULT_SUCCESS
        if commit.is_merge():
            return RESULT_SUCCESS

    if commit.is_valid():
        return RESULT_SUCCESS

    print(output.fail(commit, use_color=args.color))

    if not args.verbose:
        print(output.verbose_arg(use_color=args.color))
    else:
        print(output.fail_verbose(commit, use_color=args.color))

    return RESULT_FAIL


if __name__ == "__main__":
    raise SystemExit(main())
