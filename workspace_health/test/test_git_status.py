"""Tests for workspace_health.git_status using temporary git repos and a bare 'remote'."""

import os
from pathlib import Path
import subprocess
import time

import pytest
from workspace_health import git_status as gs
from workspace_health.git_status import Status


def git(cwd, *args):
    return subprocess.run(['git', '-C', str(cwd), *args], check=True,
                          capture_output=True, text=True).stdout


def commit(repo, name='file.txt', content=None):
    path = Path(repo) / name
    path.write_text(content if content is not None else f'{name} {time.time_ns()}\n')
    git(repo, 'add', name)
    git(repo, 'commit', '-q', '-m', f'change {name}')


@pytest.fixture(autouse=True)
def isolated_git(tmp_path, monkeypatch):
    """Do not let the user's git config influence the tests."""
    home = tmp_path / 'home'
    home.mkdir()
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', os.devnull)
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')
    for var in ('AUTHOR', 'COMMITTER'):
        monkeypatch.setenv(f'GIT_{var}_NAME', 'Test')
        monkeypatch.setenv(f'GIT_{var}_EMAIL', 'test@example.com')


@pytest.fixture
def remote(tmp_path):
    """Bare 'remote' with one commit on main."""
    bare = tmp_path / 'remote.git'
    git(tmp_path, 'init', '-q', '--bare', '-b', 'main', str(bare))
    seed = tmp_path / 'seed'
    git(tmp_path, 'clone', '-q', str(bare), str(seed))
    git(seed, 'checkout', '-q', '-b', 'main')
    commit(seed, 'README.md')
    git(seed, 'push', '-q', '-u', 'origin', 'main')
    return bare


@pytest.fixture
def clone(tmp_path, remote):
    """Fresh clone of the remote, freshly fetched (so not stale)."""
    path = tmp_path / 'ws' / 'src' / 'repo'
    git(tmp_path, 'clone', '-q', str(remote), str(path))
    git(path, 'fetch', '-q')
    return path


@pytest.fixture
def other(tmp_path, remote):
    """Second clone, used to push new commits to the remote."""
    path = tmp_path / 'other'
    git(tmp_path, 'clone', '-q', str(remote), str(path))
    return path


def push_remote_commits(other, n=1):
    for i in range(n):
        commit(other, f'remote{i}.txt')
    git(other, 'push', '-q')


def status(path, **kw):
    st = gs.get_repo_status(path, **kw)
    return st, gs.derive_status(st), gs.format_info(st)


# --------------------------------------------------------------------------- status cases

def test_ok(clone):
    st, label, info = status(clone)
    assert label == Status.OK
    assert info == 'Up to date'
    assert st.branch == 'main'
    assert st.has_upstream


def test_behind(clone, other):
    push_remote_commits(other, 2)
    gs.fetch_repo(clone)
    st, label, info = status(clone)
    assert (st.ahead, st.behind) == (0, 2)
    assert label == Status.BEHIND
    assert info == '2 behind'


def test_unpushed_ahead(clone):
    commit(clone, 'local.txt')
    st, label, info = status(clone)
    assert st.ahead == 1
    assert label == Status.UNPUSHED
    assert info == '1 ahead'


def test_modified(clone):
    (clone / 'README.md').write_text('changed\n')
    (clone / 'new.txt').write_text('staged\n')
    git(clone, 'add', 'new.txt')
    (clone / 'untracked.txt').write_text('x\n')
    st, label, info = status(clone)
    assert (st.modified, st.untracked) == (2, 1)
    assert label == Status.MODIFIED
    assert info == '2 files changed · 1 untracked'


def test_untracked_and_stash_do_not_change_badge(clone):
    (clone / 'README.md').write_text('to be stashed\n')
    git(clone, 'stash', '-q')
    (clone / 'untracked.txt').write_text('x\n')
    st, label, info = status(clone)
    assert st.stashes == 1
    assert label == Status.OK
    assert info == '1 untracked · stash'


def test_diverged_ahead_and_behind(clone, other):
    push_remote_commits(other)
    commit(clone, 'local.txt')
    gs.fetch_repo(clone)
    st, label, info = status(clone)
    assert label == Status.DIVERGED
    assert info == '1 behind · 1 ahead'


def test_diverged_modified_and_behind(clone, other):
    push_remote_commits(other, 2)
    gs.fetch_repo(clone)
    (clone / 'README.md').write_text('changed\n')
    (clone / 'u1').write_text('x')
    (clone / 'u2').write_text('x')
    _, label, info = status(clone)
    assert label == Status.DIVERGED
    assert info == '1 file changed · 2 untracked · 2 behind'


def test_no_upstream(clone):
    git(clone, 'checkout', '-q', '-b', 'feature')
    st, label, info = status(clone)
    assert not st.has_upstream
    assert label == Status.UNPUSHED
    assert info == 'no upstream'


def test_upstream_gone(clone, other):
    git(clone, 'checkout', '-q', '-b', 'feature')
    git(clone, 'push', '-q', '-u', 'origin', 'feature')
    git(other, 'push', '-q', 'origin', '--delete', 'feature')
    gs.fetch_repo(clone)  # --prune removes origin/feature
    st, label, info = status(clone)
    assert st.upstream_gone
    assert label == Status.UNPUSHED
    assert info == 'upstream gone'


def test_detached_head(clone):
    sha = git(clone, 'rev-parse', 'HEAD').strip()
    git(clone, 'checkout', '-q', '--detach')
    st, label, info = status(clone)
    assert st.detached
    assert st.branch == sha[:7]
    assert label == Status.UNPUSHED
    assert info == 'detached HEAD'


def test_stale_old_fetch(clone):
    fetch_head = clone / '.git' / 'FETCH_HEAD'
    old = time.time() - 3 * 86400
    os.utime(fetch_head, (old, old))
    st, label, info = status(clone)
    assert label == Status.STALE
    assert info == 'fetched 3 d ago'
    # A larger threshold makes it fresh again.
    assert gs.derive_status(st, stale_hours=24 * 7) == Status.OK


def test_stale_never_fetched(clone):
    (clone / '.git' / 'FETCH_HEAD').unlink()
    st, label, info = status(clone)
    assert st.last_fetch is None
    assert label == Status.STALE
    assert info == 'never fetched'


def test_stale_wins_over_behind(clone, other):
    push_remote_commits(other)
    gs.fetch_repo(clone)
    old = time.time() - 2 * 86400
    os.utime(clone / '.git' / 'FETCH_HEAD', (old, old))
    _, label, info = status(clone)
    assert label == Status.STALE
    assert info == '1 behind · fetched 2 d ago'


def test_error_invalid_repo(tmp_path):
    broken = tmp_path / 'broken'
    (broken / '.git').mkdir(parents=True)
    st, label, info = status(broken)
    assert label == Status.ERROR
    assert st.error
    assert info == st.error_summary


def test_error_fetch_failed(clone):
    git(clone, 'remote', 'set-url', 'origin', str(clone.parent / 'does-not-exist.git'))
    with pytest.raises(gs.GitError) as exc:
        gs.fetch_repo(clone)
    st, label, info = status(clone, op_error=str(exc.value), op_error_summary='Fetch failed')
    assert label == Status.ERROR
    assert info == 'Fetch failed'
    assert 'does-not-exist' in st.error
    # Local information is still available for display.
    assert st.branch == 'main'


def test_error_wins_over_everything(clone, other):
    push_remote_commits(other)
    commit(clone, 'local.txt')
    gs.fetch_repo(clone)
    _, label, _ = status(clone, op_error='boom')
    assert label == Status.ERROR


def test_git_timeout_is_error(clone):
    with pytest.raises(gs.GitError, match='timed out'):
        gs.run_git(clone, 'status', timeout=0.000001)


def test_no_credential_prompt(clone):
    """A remote needing credentials fails instead of hanging (GIT_TERMINAL_PROMPT=0)."""
    assert gs.git_env()['GIT_TERMINAL_PROMPT'] == '0'


# --------------------------------------------------------------------------- pull

def test_pull_ff_only(clone, other):
    push_remote_commits(other, 3)
    gs.fetch_repo(clone)
    gs.pull_ff_only(clone)
    _, label, _ = status(clone)
    assert label == Status.OK


def test_pull_refuses_modified(clone, other):
    push_remote_commits(other)
    gs.fetch_repo(clone)
    (clone / 'README.md').write_text('local edit\n')
    with pytest.raises(gs.GitError, match='modified'):
        gs.pull_ff_only(clone)
    assert (clone / 'README.md').read_text() == 'local edit\n'


def test_pull_refuses_diverged(clone, other):
    push_remote_commits(other)
    commit(clone, 'local.txt')
    gs.fetch_repo(clone)
    head = git(clone, 'rev-parse', 'HEAD')
    with pytest.raises(gs.GitError, match='unpushed'):
        gs.pull_ff_only(clone)
    assert git(clone, 'rev-parse', 'HEAD') == head


# --------------------------------------------------------------------------- discovery

@pytest.mark.parametrize('url,expected', [
    ('https://github.com/jkk-research/jkk_utils', ('jkk-research', 'jkk_utils')),
    ('https://github.com/jkk-research/jkk_utils.git', ('jkk-research', 'jkk_utils')),
    ('https://github.com/jkk-research/jkk_utils/', ('jkk-research', 'jkk_utils')),
    ('https://user:tok@github.com/szenergy/formula.git', ('szenergy', 'formula')),
    ('git@github.com:dottantgal/ros2_pid_library.git', ('dottantgal', 'ros2_pid_library')),
    ('ssh://git@github.com/owner/repo.name.git', ('owner', 'repo.name')),
    ('ssh://git@github.com:22/owner/repo', ('owner', 'repo')),
    ('https://gitlab.com/owner/repo.git', None),
    ('git@bitbucket.org:owner/repo.git', None),
    ('https://github.com.evil.com/owner/repo', None),
    ('/home/user/remote.git', None),
    ('', None),
    (None, None),
])
def test_parse_github_url(url, expected):
    assert gs.parse_github_url(url) == expected


def test_discovery(tmp_path, remote):
    ws = tmp_path / 'myws'
    src = ws / 'src'

    def make(rel, url):
        path = src / rel
        git(tmp_path, 'clone', '-q', str(remote), str(path))
        git(path, 'remote', 'set-url', 'origin', url)
        return path

    make('a_repo', 'https://github.com/owner/a_repo.git')
    make('group/b_repo', 'git@github.com:owner/b_repo.git')
    make('gitlab_repo', 'https://gitlab.com/owner/gitlab_repo.git')
    outer = make('outer', 'https://github.com/owner/outer')
    # Nested repo inside a repo is not listed (descending stops at a repo).
    git(tmp_path, 'clone', '-q', str(remote), str(outer / 'nested'))
    # Repos inside build/install/log are skipped.
    for skip in ('build', 'install', 'log'):
        make(f'{skip}/x', 'https://github.com/owner/x')
    # A local-only repo (no origin) is skipped.
    (src / 'local').mkdir()
    git(src / 'local', 'init', '-q')

    repos = gs.discover_github_repos(ws)
    assert [(r.rel_path, r.owner, r.name) for r in repos] == [
        ('src/a_repo', 'owner', 'a_repo'),
        ('src/group/b_repo', 'owner', 'b_repo'),
        ('src/outer', 'owner', 'outer'),
    ]
    assert repos[0].web_url == 'https://github.com/owner/a_repo'
    assert len(gs.find_repos(ws)) == 5


def test_discovery_includes_broken_repo(tmp_path, remote):
    """A repo too broken for git status still shows up (as Error) if origin is GitHub."""
    path = tmp_path / 'ws' / 'src' / 'broken'
    git(tmp_path, 'clone', '-q', str(remote), str(path))
    git(path, 'remote', 'set-url', 'origin', 'https://github.com/o/broken')
    (path / '.git' / 'HEAD').write_text('garbage\n')
    repos = gs.discover_github_repos(tmp_path / 'ws')
    assert [r.name for r in repos] == ['broken']
    report = gs.make_report(repos[0])
    assert report.label == Status.ERROR


def test_missing_workspace(tmp_path):
    assert gs.discover_github_repos(tmp_path / 'nope') == []


# --------------------------------------------------------------------------- pure helpers

def test_sort_by_severity_then_name(tmp_path):
    def rep(name, label):
        info = gs.RepoInfo(tmp_path / name, f'src/{name}', 'o', name, '')
        return gs.RepoReport(info, gs.RepoStatus(tmp_path / name), label, '')

    reports = [rep('b', Status.OK), rep('a', Status.OK), rep('z', Status.ERROR),
               rep('c', Status.BEHIND), rep('d', Status.DIVERGED)]
    assert [r.info.name for r in sorted(reports, key=gs.sort_key)] == ['z', 'd', 'c', 'a', 'b']


def test_format_info_full():
    st = gs.RepoStatus(Path('.'), branch='main', upstream='origin/main', modified=3,
                       untracked=2, behind=2, ahead=1, stashes=1, last_fetch=0.0)
    now = 3 * 86400 + 100
    assert gs.format_info(st, now=now) == \
        '3 files changed · 2 untracked · 2 behind · 1 ahead · stash · fetched 3 d ago'
    assert gs.derive_status(st, now=now) == Status.DIVERGED


def test_can_pull_only_clean_behind(tmp_path):
    info = gs.RepoInfo(tmp_path, 'src/r', 'o', 'r', '')
    behind = gs.RepoStatus(tmp_path, upstream='origin/main', behind=2, last_fetch=time.time())
    assert gs.RepoReport(info, behind, gs.derive_status(behind), '').can_pull
    dirty = gs.RepoStatus(tmp_path, upstream='origin/main', behind=2, modified=1,
                          last_fetch=time.time())
    assert not gs.RepoReport(info, dirty, gs.derive_status(dirty), '').can_pull
