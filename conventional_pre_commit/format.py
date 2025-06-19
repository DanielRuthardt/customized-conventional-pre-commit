import re
from typing import List


class Commit:
    """
    Base class for inspecting commit message formatting.
    """

    AUTOSQUASH_PREFIXES = sorted(
        [
            "amend",
            "fixup",
            "squash",
        ]
    )

    def __init__(self, commit_msg: str = ""):
        self.message = str(commit_msg)
        self.message = self.clean()

    @property
    def r_autosquash_prefixes(self):
        """Regex str for autosquash prefixes."""
        return self._r_or(self.AUTOSQUASH_PREFIXES)

    @property
    def r_verbose_commit_ignored(self):
        """Regex str for the ignored part of a verbose commit message."""
        return r"^# -{24} >8 -{24}\r?\n.*\Z"

    @property
    def r_comment(self):
        """Regex str for comments."""
        return r"^#.*\r?\n?"

    def _r_or(self, items):
        """Join items with pipe "|" to form regex ORs."""
        return "|".join(items)

    def _strip_comments(self, commit_msg: str = ""):
        """Strip comments from a commit message."""
        commit_msg = commit_msg or self.message
        return re.sub(self.r_comment, "", commit_msg, flags=re.MULTILINE)

    def _strip_verbose_commit_ignored(self, commit_msg: str = ""):
        """Strip the ignored part of a verbose commit message."""
        commit_msg = commit_msg or self.message
        return re.sub(self.r_verbose_commit_ignored, "", commit_msg, flags=re.DOTALL | re.MULTILINE)

    def clean(self, commit_msg: str = ""):
        """
        Removes comments and ignored verbose commit segments from a commit message.
        """
        commit_msg = commit_msg or self.message
        commit_msg = self._strip_verbose_commit_ignored(commit_msg)
        commit_msg = self._strip_comments(commit_msg)
        return commit_msg

    def has_autosquash_prefix(self, commit_msg: str = ""):
        """
        Returns True if input starts with one of the autosquash prefixes used in git.
        See the documentation, please https://git-scm.com/docs/git-rebase.
        """
        commit_msg = self.clean(commit_msg)
        pattern = f"^(({self.r_autosquash_prefixes})! ).*$"
        regex = re.compile(pattern, re.DOTALL)

        return bool(regex.match(commit_msg))

    def is_merge(self, commit_msg: str = ""):
        """
        Returns True if the commit message indicates a merge commit.
        Matches messages that start with "Merge", including:
        - Merge branch ...
        - Merge pull request ...
        - Merge remote-tracking branch ...
        - Merge tag ...
        See https://git-scm.com/docs/git-merge.
        """
        commit_msg = self.clean(commit_msg)
        return bool(re.match(r"^merge\b", commit_msg.lower()))


class ConventionalCommit(Commit):
    """
    Implements checks for Conventional Commits formatting.

    https://www.conventionalcommits.org
    """

    CONVENTIONAL_TYPES = sorted(["feat", "fix"])
    DEFAULT_TYPES = sorted(
        CONVENTIONAL_TYPES
        + [
            "build",
            "chore",
            "ci",
            "docs",
            "perf",
            "refactor",
            "revert",
            "style",
            "test",
        ]
    )

    def __init__(
        self, commit_msg: str = "", types: List[str] = DEFAULT_TYPES, scope_optional: bool = True, scopes: List[str] = []
    ):
        super().__init__(commit_msg)

        if set(types) & set(self.CONVENTIONAL_TYPES) == set():
            self.types = self.CONVENTIONAL_TYPES + types
        else:
            self.types = types
        self.types = sorted(self.types) if self.types else self.DEFAULT_TYPES
        self.scope_optional = scope_optional
        self.scopes = sorted(scopes) if scopes else []

    @property
    def r_types(self):
        """Regex str for valid types."""
        return f"(?i:{self._r_or(self.types)})"

    @property
    def r_scope(self):
        """Regex str for an optional (scope)."""
        if self.scopes:
            scopes = self._r_or(self.scopes)
            escaped_delimiters = list(map(re.escape, [":", ",", "-", "/"]))  # type: ignore
            delimiters_pattern = self._r_or(escaped_delimiters)
            scope_pattern = rf"\(\s*(?:(?i:{scopes}))(?:\s*(?:{delimiters_pattern})\s*(?:(?i:{scopes})))*\s*\)"

            if self.scope_optional:
                return f"(?:{scope_pattern})?"
            else:
                return scope_pattern

        if self.scope_optional:
            return r"(\([\w \/:,-]+\))?"
        else:
            return r"(\([\w \/:,-]+\))"

    @property
    def r_delim(self):
        """Regex str for optional breaking change indicator and colon delimiter."""
        return r"!?:"

    @property
    def r_subject(self):
        """Regex str for subject line."""
        return r" .+$"

    @property
    def r_body(self):
        """Regex str for the body, with multiline support."""
        return r"(?P<multi>\r?\n(?P<sep>^$\r?\n)?.+)?"

    @property
    def regex(self):
        """`re.Pattern` for ConventionalCommits formatting."""
        types_pattern = f"^(?P<type>{self.r_types})?"
        scope_pattern = f"(?P<scope>{self.r_scope})?"
        delim_pattern = f"(?P<delim>{self.r_delim})?"
        subject_pattern = f"(?P<subject>{self.r_subject})?"
        body_pattern = f"(?P<body>{self.r_body})?"
        pattern = types_pattern + scope_pattern + delim_pattern + subject_pattern + body_pattern

        return re.compile(pattern, re.MULTILINE)

    def errors(self, commit_msg: str = "") -> List[str]:
        """
        Return a list of missing Conventional Commit components from a commit message.
        """
        match = self.match(commit_msg)
        groups = match.groupdict() if match else {}

        # With a type error, the rest of the components will be unmatched
        # even if the overall structure of the commit is correct,
        # since a correct type must come first.
        #
        # E.g. with an invalid type:
        #
        #    invalid: this is a commit
        #
        # The delim, subject, and body components would all be missing from the match
        # there's no need to notify on the other components when the type is invalid
        if not groups.get("type"):
            groups.pop("delim", None)
            groups.pop("subject", None)
            groups.pop("body", None)

        if self.scope_optional:
            groups.pop("scope", None)

        if not groups.get("body"):
            groups.pop("multi", None)
            groups.pop("sep", None)

        return [g for g, v in groups.items() if not v]

    def is_valid(self, commit_msg: str = "") -> bool:
        """
        Returns True if commit_msg matches Conventional Commits formatting.
        https://www.conventionalcommits.org
        """
        match = self.match(commit_msg)

        # match all the required components
        #
        #    type(scope): subject
        #
        #    extended body
        #
        return bool(match) and all(
            [
                match.group("type"),
                self.scope_optional or match.group("scope"),
                match.group("delim"),
                match.group("subject"),
                any(
                    [
                        # no extra body; OR
                        not match.group("body"),
                        # a multiline body with proper separator
                        match.group("multi") and match.group("sep"),
                    ]
                ),
            ]
        )

    def match(self, commit_msg: str = ""):
        """
        Returns an `re.Match` object for the input against the Conventional Commits format.
        """
        commit_msg = self.clean(commit_msg) or self.message
        return self.regex.match(commit_msg)


class CustomizedConventionalCommit(Commit):
    """
    Implements checks for Customized Conventional Commits formatting using GitMoji.

    Format: <emoji> <description>

    The format omits scope and uses GitMoji emojis instead of traditional types.
    https://gitmoji.dev/
    """

    # GitMoji emojis - comprehensive list from https://gitmoji.dev/
    DEFAULT_EMOJIS = [
        "🎨",  # Improve structure / format of the code
        "⚡️",  # Improve performance
        "🔥",  # Remove code or files
        "🐛",  # Fix a bug
        "🚑️",  # Critical hotfix
        "✨",  # Introduce new features
        "📝",  # Add or update documentation
        "🚀",  # Deploy stuff
        "💄",  # Add or update the UI and style files
        "🎉",  # Begin a project
        "✅",  # Add, update, or pass tests
        "🔒️",  # Fix security or privacy issues
        "🔐",  # Add or update secrets
        "🔖",  # Release / Version tags
        "🚨",  # Fix compiler / linter warnings
        "🚧",  # Work in progress
        "💚",  # Fix CI Build
        "⬇️",  # Downgrade dependencies
        "⬆️",  # Upgrade dependencies
        "📌",  # Pin dependencies to specific versions
        "👷",  # Add or update CI build system
        "📈",  # Add or update analytics or track code
        "♻️",  # Refactor code
        "➕",  # Add a dependency
        "➖",  # Remove a dependency
        "🔧",  # Add or update configuration files
        "🔨",  # Add or update development scripts
        "🌐",  # Internationalization and localization
        "✏️",  # Fix typos
        "💩",  # Write bad code that needs to be improved
        "⏪️",  # Revert changes
        "🔀",  # Merge branches
        "📦️",  # Add or update compiled files or packages
        "👽️",  # Update code due to external API changes
        "🚚",  # Move or rename resources
        "📄",  # Add or update license
        "💥",  # Introduce breaking changes
        "🍱",  # Add or update assets
        "♿️",  # Improve accessibility
        "💡",  # Add or update comments in source code
        "🍻",  # Write code drunkenly
        "💬",  # Add or update text and literals
        "🗃️",  # Perform database related changes
        "🔊",  # Add or update logs
        "🔇",  # Remove logs
        "👥",  # Add or update contributor(s)
        "🚸",  # Improve user experience / usability
        "🏗️",  # Make architectural changes
        "📱",  # Work on responsive design
        "🤡",  # Mock things
        "🥚",  # Add or update an easter egg
        "🙈",  # Add or update a .gitignore file
        "📸",  # Add or update snapshots
        "⚗️",  # Perform experiments
        "🔍️",  # Improve SEO
        "🏷️",  # Add or update types
        "🌱",  # Add or update seed files
        "🚩",  # Add, update, or remove feature flags
        "🥅",  # Catch errors
        "💫",  # Add or update animations and transitions
        "🗑️",  # Deprecate code that needs to be cleaned up
        "🛂",  # Work on code related to authorization, roles and permissions
        "🩹",  # Simple fix for a non-critical issue
        "🧐",  # Data exploration/inspection
        "⚰️",  # Remove dead code
        "🧪",  # Add a failing test
        "👔",  # Add or update business logic
        "🩺",  # Add or update healthcheck
        "🧱",  # Infrastructure related changes
        "🧑‍💻",  # Improve developer experience
        "💸",  # Add sponsorships or money related infrastructure
        "🧵",  # Add or update code related to multithreading or concurrency
        "🦺",  # Add or update code related to validation
        "✈️",  # Improve offline support
    ]

    def __init__(self, commit_msg: str = "", emojis: List[str] = None):
        super().__init__(commit_msg)
        self.emojis = emojis if emojis is not None else self.DEFAULT_EMOJIS

    @property
    def r_emoji(self):
        """Regex str for valid GitMoji emojis."""
        # Escape emojis for regex pattern
        escaped_emojis = [re.escape(emoji) for emoji in self.emojis]
        return f"({'|'.join(escaped_emojis)})"

    @property
    def r_description(self):
        """Regex str for description line."""
        return r" .+$"

    @property
    def r_body(self):
        """Regex str for the body, with multiline support."""
        return r"(?P<multi>\r?\n(?P<sep>^$\r?\n)?.+)?"

    @property
    def regex(self):
        """`re.Pattern` for Customized Conventional Commits formatting."""
        emoji_pattern = f"^(?P<emoji>{self.r_emoji})?"
        description_pattern = f"(?P<description>{self.r_description})?"
        body_pattern = f"(?P<body>{self.r_body})?"
        pattern = emoji_pattern + description_pattern + body_pattern

        return re.compile(pattern, re.MULTILINE | re.DOTALL)

    def errors(self, commit_msg: str = "") -> List[str]:
        """
        Return a list of missing Customized Conventional Commit components.
        """
        match = self.match(commit_msg)
        groups = match.groupdict() if match else {}

        # If no emoji is found, the rest might not be matched properly
        if not groups.get("emoji"):
            groups.pop("description", None)
            groups.pop("body", None)

        if not groups.get("body"):
            groups.pop("multi", None)
            groups.pop("sep", None)

        return [g for g, v in groups.items() if not v]

    def is_valid(self, commit_msg: str = "") -> bool:
        """
        Returns True if commit_msg matches Customized Conventional Commits formatting.
        Format: <emoji> <description>
        """
        match = self.match(commit_msg)

        # Match all the required components:
        # <emoji> <description>
        #
        # optional body with proper separator
        return bool(match) and all(
            [
                match.group("emoji"),
                match.group("description"),
                any(
                    [
                        # no extra body; OR
                        not match.group("body"),
                        # a multiline body with proper separator
                        match.group("multi") and match.group("sep"),
                    ]
                ),
            ]
        )

    def match(self, commit_msg: str = ""):
        """
        Returns an `re.Match` object for the input against the Customized Conventional Commits format.
        """
        commit_msg = self.clean(commit_msg) or self.message
        return self.regex.match(commit_msg)


def is_conventional(
    input: str, types: List[str] = ConventionalCommit.DEFAULT_TYPES, optional_scope: bool = True, scopes: List[str] = []
) -> bool:
    """
    Returns True if input matches Conventional Commits formatting
    https://www.conventionalcommits.org

    Optionally provide a list of additional custom types.
    """
    commit = ConventionalCommit(commit_msg=input, types=types, scope_optional=optional_scope, scopes=scopes)

    return commit.is_valid()


def is_customized_conventional(input: str, emojis: List[str] = None) -> bool:
    """
    Returns True if input matches Customized Conventional Commits formatting
    using GitMoji emojis.

    Format: <emoji> <description>
    """
    commit = CustomizedConventionalCommit(commit_msg=input, emojis=emojis)

    return commit.is_valid()
