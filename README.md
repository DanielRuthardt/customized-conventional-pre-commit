# conventional-pre-commit

A [`pre-commit`](https://pre-commit.com) hook to check commit messages for
**Customized Conventional Commits** formatting using [GitMoji](https://gitmoji.dev/).

This tool enforces a standardized format for commit messages using GitMoji emojis instead of traditional types, ensuring clear and concise release notes.

**Format:** `<emoji> <description>`

In contrast to the original [Conventional Commits](https://www.conventionalcommits.org/) standard, we use [GitMoji](https://gitmoji.dev/) to represent the type of the commit, and we omit the optional scope.

Works with Python >= 3.8.

## Usage

Make sure `pre-commit` is [installed](https://pre-commit.com#install).

Create a blank configuration file at the root of your repo, if needed:

```console
touch .pre-commit-config.yaml
```

Add/update `default_install_hook_types` and add a new repo entry in your configuration file:

```yaml
default_install_hook_types:
  - pre-commit
  - commit-msg

repos:
  # - repo: ...

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: <git sha or tag>
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: []
```

Install the `pre-commit` script:

```console
pre-commit install --install-hooks
```

Make a (normal) commit :x::

```console
$ git commit -m "add a new feature"

[INFO] Initializing environment for ....
Conventional Commit......................................................Failed
- hook id: conventional-pre-commit
- duration: 0.07s
- exit code: 1

[Bad commit message] >> add a new feature
Your commit message does not follow Customized Conventional Commits formatting
https://gitmoji.dev/
```

And with the `--verbose` arg:

```console
$ git commit -m "add a new feature"

[INFO] Initializing environment for ....
Conventional Commit......................................................Failed
- hook id: conventional-pre-commit
- duration: 0.07s
- exit code: 1

[Bad commit message] >> add a new feature
Your commit message does not follow Customized Conventional Commits formatting
https://gitmoji.dev/

Customized Conventional Commit messages follow a pattern like:

    <emoji> <description>

    optional extended body

Examples:
    🔖 Use latest versions of all items
    ⚡️ Slightly upsize build storage
    🔧 Update enabled items directory

Please correct the following errors:

  - Expected GitMoji emoji at the start. Examples: 🎨⚡️🔥🐛🚑️✨📝🚀💄🎉...

Run:

    git commit --edit --file=.git/COMMIT_EDITMSG

to edit the commit message and retry the commit.

For a complete list of GitMoji emojis, visit: https://gitmoji.dev/
```

Make a (customized conventional) commit :heavy_check_mark::

```console
$ git commit -m "✨ Add a new feature"

[INFO] Initializing environment for ....
Conventional Commit......................................................Passed
- hook id: conventional-pre-commit
- duration: 0.05s
```

## Install with pip

`conventional-pre-commit` can also be installed and used from the command line:

```shell
pip install conventional-pre-commit
```

Then run the command line script:

```shell
conventional-pre-commit [emojis] input
```

- `[emojis]` is an optional list of GitMoji emojis to allow (e.g. `🔖 ⚡️ 🔧`)

- `input` is a file containing the commit message to check:

```shell
conventional-pre-commit 🔖 ⚡️ 🔧 🐛 ✨ .git/COMMIT_MSG
```

Or from a Python program:

```python
from conventional_pre_commit.format import is_customized_conventional

# prints True
print(is_customized_conventional("🔖 Use latest versions of all items"))

# prints False
print(is_customized_conventional("nope: this is not a customized conventional commit"))

# prints True with custom emojis
print(is_customized_conventional("🔖 Use latest versions", emojis=["🔖", "⚡️"]))
```

## Passing `args`

`conventional-pre-commit` supports a number of arguments to configure behavior:

```shell
$ conventional-pre-commit -h
usage: conventional-pre-commit [-h] [--no-color] [--strict] [--verbose] [emojis ...] input

Check a git commit message for Customized Conventional Commits formatting using GitMoji.

positional arguments:
  emojis       Optional list of additional GitMoji emojis to support
  input        A file containing a git commit message

options:
  -h, --help   show this help message and exit
  --no-color   Disable color in output.
  --strict     Force commit to strictly follow Customized Conventional Commits formatting. Disallows fixup! and merge commits.
  --verbose    Print more verbose error output.
```

Supply arguments on the command-line, or via the pre-commit `hooks.args` property:

```yaml
repos:
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: <git sha or tag>
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [--strict, 🔖, ⚡️, 🔧, 🐛, ✨]
```

**NOTE:** when using as a pre-commit hook, `input` is supplied automatically (with the current commit's message).

## Common GitMoji Examples

Here are some commonly used GitMoji emojis and their meanings:

| Emoji | Code                 | Description                            |
| ----- | -------------------- | -------------------------------------- |
| 🎨    | `:art:`              | Improve structure / format of the code |
| ⚡️   | `:zap:`              | Improve performance                    |
| 🔥    | `:fire:`             | Remove code or files                   |
| 🐛    | `:bug:`              | Fix a bug                              |
| ✨    | `:sparkles:`         | Introduce new features                 |
| 📝    | `:memo:`             | Add or update documentation            |
| 🔖    | `:bookmark:`         | Release / Version tags                 |
| 🔧    | `:wrench:`           | Add or update configuration files      |
| ✅    | `:white_check_mark:` | Add, update, or pass tests             |
| 🚀    | `:rocket:`           | Deploy stuff                           |

For a complete list of available emojis, visit [GitMoji](https://gitmoji.dev/).

## Development

`conventional-pre-commit` comes with a [VS Code devcontainer](https://code.visualstudio.com/learn/develop-cloud/containers)
configuration to provide a consistent development environment.

With the `Remote - Containers` extension enabled, open the folder containing this repository inside Visual Studio Code.

You should receive a prompt in the Visual Studio Code window; click `Reopen in Container` to run the development environment
inside the devcontainer.

If you do not receive a prompt, or when you feel like starting from a fresh environment:

1. `Ctrl/Cmd+Shift+P` to bring up the command palette in Visual Studio Code
1. Type `Remote-Containers` to filter the commands
1. Select `Rebuild and Reopen in Container` to completely rebuild the devcontainer
1. Select `Reopen in Container` to reopen the most recent devcontainer build

## Versioning

Versioning generally follows [Semantic Versioning](https://semver.org/).

## Making a release

Releases to PyPI and GitHub are triggered by pushing a tag.

1. Ensure all changes for the release are present in the `main` branch
1. Tag with the new version: `git tag vX.Y.Z` for regular release, `git tag vX.Y.Z-preN` for pre-release
1. Push the new version tag: `git push origin vX.Y.Z`

## License

[Apache 2.0](LICENSE)

Inspired by matthorgan's [`pre-commit-conventional-commits`](https://github.com/matthorgan/pre-commit-conventional-commits).
