import os

from conventional_pre_commit.format import CustomizedConventionalCommit


class Colors:
    LBLUE = "\033[00;34m"
    LRED = "\033[01;31m"
    RESTORE = "\033[0m"
    YELLOW = "\033[00;33m"

    def __init__(self, enabled=True):
        self.enabled = enabled

    @property
    def blue(self):
        return self.LBLUE if self.enabled else ""

    @property
    def red(self):
        return self.LRED if self.enabled else ""

    @property
    def restore(self):
        return self.RESTORE if self.enabled else ""

    @property
    def yellow(self):
        return self.YELLOW if self.enabled else ""


def fail(commit: CustomizedConventionalCommit, use_color=True):
    c = Colors(use_color)
    lines = [
        f"{c.red}[Bad commit message] >>{c.restore} {commit.message}",
        f"{c.yellow}Your commit message does not follow Customized Conventional Commits formatting{c.restore}",
        f"{c.blue}https://gitmoji.dev/{c.restore}",
    ]
    return os.linesep.join(lines)


def verbose_arg(use_color=True):
    c = Colors(use_color)
    lines = [
        "",
        f"{c.yellow}Use the {c.restore}--verbose{c.yellow} arg for more information{c.restore}",
    ]
    return os.linesep.join(lines)


def fail_verbose(commit: CustomizedConventionalCommit, use_color=True):
    c = Colors(use_color)
    lines = [
        "",
        f"{c.yellow}Customized Conventional Commit messages follow a pattern like:",
        "",
        f"{c.restore}    <emoji> <description>",
        "",
        "    optional extended body",
        "",
        f"{c.yellow}Examples:",
        f"{c.restore}    🔖 Use latest versions of all items",
        f"{c.restore}    ⚡️ Slightly upsize build storage",
        f"{c.restore}    🔧 Update enabled items directory",
        "",
    ]

    def _format_emojis(emojis):
        # Show a sample of available emojis
        sample_emojis = emojis[:10]  # Show first 10 emojis
        formatted_emojis = f"{c.blue}".join(sample_emojis)
        return f"{c.blue}{formatted_emojis}"

    errors = commit.errors()
    if errors:
        lines.append(f"{c.yellow}Please correct the following errors:{c.restore}")
        lines.append("")
        for group in errors:
            if group == "emoji":
                emoji_sample = _format_emojis(commit.emojis)
                lines.append(f"{c.yellow}  - Expected GitMoji emoji at the start. Examples: {emoji_sample}...")
            elif group == "description":
                lines.append(f"{c.yellow}  - Expected description after the emoji (e.g., 'Fix authentication bug'){c.restore}")
            else:
                lines.append(f"{c.yellow}  - Expected value for {c.restore}{group}{c.yellow} but found none.{c.restore}")

    lines.extend(
        [
            "",
            f"{c.yellow}Run:{c.restore}",
            "",
            "    git commit --edit --file=.git/COMMIT_EDITMSG",
            "",
            f"{c.yellow}to edit the commit message and retry the commit.{c.restore}",
            "",
            f"{c.yellow}For a complete list of GitMoji emojis, visit: {c.blue}https://gitmoji.dev/{c.restore}",
        ]
    )
    return os.linesep.join(lines)


def unicode_decode_error(use_color=True):
    c = Colors(use_color)
    return f"""
{c.red}[Bad commit message encoding]{c.restore}

{c.yellow}conventional-pre-commit couldn't decode your commit message.
UTF-8 encoding is assumed, please configure git to write commit messages in UTF-8.
See {c.blue}https://git-scm.com/docs/git-commit/#_discussion{c.yellow} for more.{c.restore}
"""
