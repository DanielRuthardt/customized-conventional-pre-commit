import os
import subprocess

import pytest

from conventional_pre_commit.hook import RESULT_FAIL, RESULT_SUCCESS, main
from conventional_pre_commit.output import Colors


@pytest.fixture
def cmd():
    return "conventional-pre-commit"


def test_main_fail__missing_args():
    result = main()

    assert result == RESULT_FAIL


def test_main_fail__bad(bad_commit_path):
    result = main([bad_commit_path])

    assert result == RESULT_FAIL


def test_main_fail__custom(bad_commit_path):
    result = main(["custom", bad_commit_path])

    assert result == RESULT_FAIL


def test_main_success__conventional(conventional_commit_path):
    result = main([conventional_commit_path])

    assert result == RESULT_SUCCESS


def test_main_success__custom(custom_commit_path):
    result = main(["custom", custom_commit_path])

    assert result == RESULT_SUCCESS


def test_main_success__custom_conventional(conventional_commit_path):
    result = main(["custom", conventional_commit_path])

    assert result == RESULT_SUCCESS


def test_main_success__conventional_utf8(conventional_utf8_commit_path):
    result = main([conventional_utf8_commit_path])

    assert result == RESULT_SUCCESS


def test_main_fail__conventional_gbk(conventional_gbk_commit_path):
    result = main([conventional_gbk_commit_path])

    assert result == RESULT_FAIL


def test_main_fail__conventional_with_scope(conventional_commit_path):
    result = main(["--force-scope", conventional_commit_path])

    assert result == RESULT_FAIL


def test_main_success__conventional_with_scope(cmd, conventional_commit_with_scope_path):
    result = main(["--force-scope", conventional_commit_with_scope_path])

    assert result == RESULT_SUCCESS


def test_main_success__fixup_commit(fixup_commit_path):
    result = main([fixup_commit_path])

    assert result == RESULT_SUCCESS


def test_main_fail__fixup_commit(fixup_commit_path):
    result = main(["--strict", fixup_commit_path])

    assert result == RESULT_FAIL


def test_main_fail__merge_commit(merge_commit_path):
    result = main(["--strict", merge_commit_path])

    assert result == RESULT_FAIL


def test_main_success__merge_commit(merge_commit_path):
    result = main([merge_commit_path])

    assert result == RESULT_SUCCESS


def test_main_success__conventional_commit_multi_line(conventional_commit_multi_line_path):
    result = main([conventional_commit_multi_line_path])

    assert result == RESULT_SUCCESS


def test_main_fail__conventional_commit_bad_multi_line(conventional_commit_bad_multi_line_path):
    result = main([conventional_commit_bad_multi_line_path])

    assert result == RESULT_FAIL


def test_main_fail__verbose(bad_commit_path, capsys):
    result = main(["--verbose", "--force-scope", bad_commit_path])

    assert result == RESULT_FAIL

    captured = capsys.readouterr()
    output = captured.out

    assert Colors.LBLUE in output
    assert Colors.LRED in output
    assert Colors.RESTORE in output
    assert Colors.YELLOW in output
    assert "Conventional Commit messages follow a pattern like" in output
    assert f"type(scope): subject{os.linesep}{os.linesep}    extended body" in output
    assert "git commit --edit --file=.git/COMMIT_EDITMSG" in output
    assert "edit the commit message and retry the commit" in output


def test_main_fail__no_color(bad_commit_path, capsys):
    result = main(["--verbose", "--no-color", bad_commit_path])

    assert result == RESULT_FAIL

    captured = capsys.readouterr()
    output = captured.out

    assert Colors.LBLUE not in output
    assert Colors.LRED not in output
    assert Colors.RESTORE not in output
    assert Colors.YELLOW not in output


def test_subprocess_fail__missing_args(cmd):
    result = subprocess.call(cmd)

    assert result == RESULT_FAIL


def test_subprocess_fail__bad(cmd, bad_commit_path):
    result = subprocess.call((cmd, bad_commit_path))

    assert result == RESULT_FAIL


def test_subprocess_fail__custom(cmd, bad_commit_path):
    result = subprocess.call((cmd, "custom", bad_commit_path))

    assert result == RESULT_FAIL


def test_subprocess_success__conventional(cmd, conventional_commit_path):
    result = subprocess.call((cmd, conventional_commit_path))

    assert result == RESULT_SUCCESS


def test_subprocess_success__custom(cmd, custom_commit_path):
    result = subprocess.call((cmd, "custom", custom_commit_path))

    assert result == RESULT_SUCCESS


def test_subprocess_success__custom_conventional(cmd, conventional_commit_path):
    result = subprocess.call((cmd, "custom", conventional_commit_path))

    assert result == RESULT_SUCCESS


def test_subprocess_fail__conventional_with_scope(cmd, conventional_commit_path):
    result = subprocess.call((cmd, "--force-scope", conventional_commit_path))

    assert result == RESULT_FAIL


def test_subprocess_success__conventional_with_scope(cmd, conventional_commit_with_scope_path):
    result = subprocess.call((cmd, "--force-scope", conventional_commit_with_scope_path))

    assert result == RESULT_SUCCESS


def test_subprocess_success__conventional_with_multiple_scopes(cmd, conventional_commit_with_multiple_scopes_path):
    result = subprocess.call((cmd, "--scopes", "api,client", conventional_commit_with_multiple_scopes_path))
    assert result == RESULT_SUCCESS


def test_subprocess_fail__conventional_with_multiple_scopes(cmd, conventional_commit_with_multiple_scopes_path):
    result = subprocess.call((cmd, "--scopes", "api", conventional_commit_with_multiple_scopes_path))
    assert result == RESULT_FAIL


def test_main_success__custom_scopes_optional_scope(conventional_commit_path):
    result = main(["--scopes", "api,client", conventional_commit_path])
    assert result == RESULT_SUCCESS


def test_main_success__custom_scopes_with_allowed_scope(conventional_commit_with_multiple_scopes_path):
    result = main(["--scopes", "chore,api,client", conventional_commit_with_multiple_scopes_path])
    assert result == RESULT_SUCCESS


def test_main_fail__custom_scopes_with_disallowed_scope(conventional_commit_with_scope_path):
    result = main(["--scopes", "api,client", conventional_commit_with_scope_path])
    assert result == RESULT_FAIL


def test_main_fail__custom_scopes_require_scope_no_scope(conventional_commit_path):
    result = main(["--scopes", "chore,feat,fix,custom", "--force-scope", conventional_commit_path])
    assert result == RESULT_FAIL


def test_main_success__custom_scopes_require_scope_with_allowed_scope(conventional_commit_with_scope_path):
    result = main(["--scopes", "api,client,scope", "--force-scope", conventional_commit_with_scope_path])
    assert result == RESULT_SUCCESS


def test_main_fail__custom_scopes_require_scope_with_disallowed_scope(conventional_commit_with_scope_path):
    result = main(["--scopes", "api,client", "--force-scope", conventional_commit_with_scope_path])
    assert result == RESULT_FAIL


def test_subprocess_success__fixup_commit(cmd, fixup_commit_path):
    result = subprocess.call((cmd, fixup_commit_path))

    assert result == RESULT_SUCCESS


def test_subprocess_fail__fixup_commit(cmd, fixup_commit_path):
    result = subprocess.call((cmd, "--strict", fixup_commit_path))

    assert result == RESULT_FAIL


def test_subprocess_success__conventional_commit_multi_line(cmd, conventional_commit_multi_line_path):
    result = subprocess.call((cmd, conventional_commit_multi_line_path))

    assert result == RESULT_SUCCESS


def test_subprocess_fail__conventional_commit_bad_multi_line(cmd, conventional_commit_bad_multi_line_path):
    result = subprocess.call((cmd, conventional_commit_bad_multi_line_path))

    assert result == RESULT_FAIL


# Tests for GitMoji format

def test_main_success__gitmoji_commit(gitmoji_commit_path):
    result = main([gitmoji_commit_path])

    assert result == RESULT_SUCCESS


def test_main_success__gitmoji_commit_multiline(gitmoji_commit_multiline_path):
    result = main([gitmoji_commit_multiline_path])

    assert result == RESULT_SUCCESS


def test_main_success__gitmoji_config_commit(gitmoji_commit_config_path):
    result = main([gitmoji_commit_config_path])

    assert result == RESULT_SUCCESS


def test_main_fail__bad_gitmoji_commit(bad_gitmoji_commit_path):
    result = main([bad_gitmoji_commit_path])

    assert result == RESULT_FAIL


def test_main_fail__gitmoji_verbose(bad_gitmoji_commit_path, capsys):
    result = main(["--verbose", bad_gitmoji_commit_path])

    assert result == RESULT_FAIL

    captured = capsys.readouterr()
    output = captured.out

    assert Colors.LBLUE in output
    assert Colors.LRED in output
    assert Colors.RESTORE in output
    assert Colors.YELLOW in output
    assert "Customized Conventional Commit messages follow a pattern like" in output
    assert "<emoji> <description>" in output
    assert "🔖 Use latest versions of all items" in output
    assert "⚡️ Slightly upsize build storage" in output
    assert "🔧 Update enabled items directory" in output
    assert "https://gitmoji.dev/" in output
    assert "git commit --edit --file=.git/COMMIT_EDITMSG" in output


def test_main_fail__gitmoji_no_color(bad_gitmoji_commit_path, capsys):
    result = main(["--verbose", "--no-color", bad_gitmoji_commit_path])

    assert result == RESULT_FAIL

    captured = capsys.readouterr()
    output = captured.out

    assert Colors.LBLUE not in output
    assert Colors.LRED not in output
    assert Colors.RESTORE not in output
    assert Colors.YELLOW not in output


def test_main_success__gitmoji_with_custom_emojis(gitmoji_commit_path):
    result = main(["🔖", "⚡️", "🔧", gitmoji_commit_path])

    assert result == RESULT_SUCCESS


def test_main_fail__gitmoji_with_limited_emojis(gitmoji_commit_multiline_path):
    # The multiline commit uses ⚡️ but we only allow 🔖
    result = main(["🔖", gitmoji_commit_multiline_path])

    assert result == RESULT_FAIL


def test_subprocess_success__gitmoji_commit(cmd, gitmoji_commit_path):
    result = subprocess.call((cmd, gitmoji_commit_path))

    assert result == RESULT_SUCCESS


def test_subprocess_success__gitmoji_commit_multiline(cmd, gitmoji_commit_multiline_path):
    result = subprocess.call((cmd, gitmoji_commit_multiline_path))

    assert result == RESULT_SUCCESS


def test_subprocess_fail__bad_gitmoji_commit(cmd, bad_gitmoji_commit_path):
    result = subprocess.call((cmd, bad_gitmoji_commit_path))

    assert result == RESULT_FAIL


def test_subprocess_success__gitmoji_with_custom_emojis(cmd, gitmoji_commit_path):
    result = subprocess.call((cmd, "🔖", "⚡️", "🔧", gitmoji_commit_path))

    assert result == RESULT_SUCCESS
