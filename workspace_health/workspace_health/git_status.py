"""
Git logic for workspace_health: repo discovery, status model and safe git operations.

This module has no GUI dependencies so it can be unit tested on its own.
Only read-only commands, ``git fetch --prune`` and ``git pull --ff-only`` are run;
nothing destructive (reset, checkout, clean, stash drop) is ever executed.
"""

from dataclasses import dataclass
import enum
import os
from pathlib import Path
import re
import subprocess
import time
from typing import List, Optional, Tuple

SKIP_DIRS = frozenset({'build', 'install', 'log'})
DEFAULT_STALE_HOURS = 24.0
LOCAL_TIMEOUT = 10.0
FETCH_TIMEOUT = 20.0
PULL_TIMEOUT = 60.0


class Status(enum.Enum):
    """Badge label of a repository; lower severity value = more important."""

    ERROR = ('Error', 0, '#e04848')
    DIVERGED = ('Diverged', 1, '#c0392b')
    MODIFIED = ('Modified', 2, '#e8913a')
    UNPUSHED = ('Unpushed', 3, '#f0a95e')
    STALE = ('Stale', 4, '#c9b458')
    BEHIND = ('Behind', 5, '#e6c229')
    OK = ('OK', 6, '#2fa572')

    def __init__(self, label, severity, color):
        self.label = label
        self.severity = severity
        self.color = color


NEEDS_ATTENTION = frozenset({Status.MODIFIED, Status.UNPUSHED, Status.DIVERGED, Status.ERROR})


class GitError(Exception):
    """A git command failed, timed out or a git operation was refused."""


# --------------------------------------------------------------------------- running git

def git_env() -> dict:
    """Environment for git: never prompt for credentials, stable (C locale) output."""
    env = dict(os.environ)
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['LC_ALL'] = 'C'
    env.setdefault('GIT_SSH_COMMAND', 'ssh -o BatchMode=yes -o ConnectTimeout=10')
    for var in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'):
        env.pop(var, None)
    return env


def run_git(repo, *args, timeout: float = LOCAL_TIMEOUT) -> str:
    """Run ``git -C repo args...`` and return stdout, raising GitError on any failure."""
    cmd = ['git', '-C', str(repo), *args]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=timeout, env=git_env(), stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise GitError(f'git {args[0]} timed out after {timeout:g} s') from None
    except OSError as exc:
        raise GitError(f'cannot run git: {exc}') from None
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout).strip() or f'exit code {proc.returncode}'
        raise GitError(f'git {" ".join(args)} failed:\n{msg}')
    return proc.stdout


# --------------------------------------------------------------------------- discovery

_GITHUB_RE = re.compile(
    r'^(?:'
    r'(?:https?|git|ssh|git\+ssh)://(?:[^@/]+@)?(?:www\.)?github\.com(?::\d+)?/'  # URL form
    r'|(?:[^@/]+@)?github\.com:'                                                 # scp-like ssh
    r')(?P<owner>[^/]+)/(?P<name>[^/]+?)(?:\.git)?/?$',
    re.IGNORECASE)


def parse_github_url(url: Optional[str]) -> Optional[Tuple[str, str]]:
    """Return ``(owner, name)`` for a github.com remote URL (https or ssh), else None."""
    if not url:
        return None
    m = _GITHUB_RE.match(url.strip())
    if not m:
        return None
    return m.group('owner'), m.group('name')


def find_repos(ws) -> List[Path]:
    """
    Find git repositories under ``<ws>/src`` (or ``ws`` if it has no src folder).

    Descending stops at a repository; build/, install/, log/ and hidden dirs are skipped.
    """
    ws = Path(ws).expanduser()
    root = ws / 'src' if (ws / 'src').is_dir() else ws
    if not root.is_dir():
        return []
    if (root / '.git').exists():
        return [root]
    repos = []
    seen = set()
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            real = current.resolve()
            if real in seen:
                continue
            seen.add(real)
            entries = sorted(os.scandir(current), key=lambda e: e.name, reverse=True)
        except OSError:
            continue
        for entry in entries:
            if entry.name in SKIP_DIRS or entry.name.startswith('.'):
                continue
            try:
                if not entry.is_dir():
                    continue
            except OSError:
                continue
            path = Path(entry.path)
            if (path / '.git').exists():
                repos.append(path)
            else:
                stack.append(path)
    return sorted(repos)


def get_origin_url(repo) -> Optional[str]:
    """Return the ``origin`` remote URL, also for repos too broken for normal git commands."""
    repo = Path(repo)
    try:
        return run_git(repo, 'config', '--get', 'remote.origin.url').strip() or None
    except GitError:
        pass
    config = repo / '.git' / 'config'
    if config.is_file():
        try:
            return run_git(repo, 'config', '--file', str(config),
                           '--get', 'remote.origin.url').strip() or None
        except GitError:
            pass
    return None


@dataclass
class RepoInfo:
    """A discovered GitHub repository."""

    path: Path
    rel_path: str
    owner: str
    name: str
    url: str

    @property
    def web_url(self) -> str:
        return f'https://github.com/{self.owner}/{self.name}'


def discover_github_repos(ws) -> List[RepoInfo]:
    """Return the repositories under the workspace whose origin points to github.com."""
    ws = Path(ws).expanduser()
    result = []
    for path in find_repos(ws):
        url = get_origin_url(path)
        parsed = parse_github_url(url)
        if parsed is None:
            continue
        try:
            rel = str(path.relative_to(ws))
        except ValueError:
            rel = str(path)
        result.append(RepoInfo(path=path, rel_path=rel, owner=parsed[0], name=parsed[1],
                               url=url))
    return result


# --------------------------------------------------------------------------- status

@dataclass
class RepoStatus:
    """Raw state of one repository, on two axes: working tree and remote relation."""

    path: Path
    # local
    branch: str = ''
    detached: bool = False
    modified: int = 0
    untracked: int = 0
    stashes: int = 0
    # remote relation
    upstream: Optional[str] = None
    upstream_gone: bool = False
    ahead: int = 0
    behind: int = 0
    last_fetch: Optional[float] = None
    # failure
    error: Optional[str] = None
    error_summary: str = ''

    @property
    def has_upstream(self) -> bool:
        return self.upstream is not None and not self.upstream_gone


def summarize_error(message: str, prefix: str = '') -> str:
    """Make a short one-line description of a git error message."""
    low = message.lower()
    if 'timed out' in low:
        reason = 'timed out'
    elif 'could not resolve host' in low or 'could not read from remote' in low \
            or 'connection' in low or 'does not appear to be a git repository' in low:
        reason = 'remote unreachable'
    elif 'authentication' in low or 'permission denied' in low or 'username' in low \
            or 'terminal prompts disabled' in low:
        reason = 'authentication'
    elif 'not a git repository' in low:
        reason = 'not a valid repo'
    elif 'dubious ownership' in low:
        reason = 'unsafe repo (safe.directory)'
    elif 'refusing' in low:
        reason = message.split('\n')[-1].split(':', 1)[-1].strip()
    elif 'not possible to fast-forward' in low:
        reason = 'not fast-forward'
    else:
        reason = ''
    if prefix:
        return f'{prefix}: {reason}' if reason else prefix
    return (reason[:1].upper() + reason[1:]) if reason else 'Git error'


def _read_local(st: RepoStatus):
    out = run_git(st.path, 'status', '--porcelain=v2', '--branch')
    oid = ''
    has_ab = False
    for line in out.splitlines():
        if line.startswith('# branch.oid '):
            oid = line[len('# branch.oid '):]
        elif line.startswith('# branch.head '):
            head = line[len('# branch.head '):]
            if head == '(detached)':
                st.detached = True
            else:
                st.branch = head
        elif line.startswith('# branch.upstream '):
            st.upstream = line[len('# branch.upstream '):]
        elif line.startswith('# branch.ab '):
            has_ab = True
        elif line[:2] in ('1 ', '2 ', 'u '):
            st.modified += 1
        elif line.startswith('? '):
            st.untracked += 1
    if st.detached:
        st.branch = oid[:7] if oid and oid != '(initial)' else 'HEAD'
        st.upstream = None
    elif st.upstream is not None and not has_ab:
        # Upstream configured but the remote branch no longer exists (or no commits yet).
        st.upstream_gone = True
    stash = run_git(st.path, 'stash', 'list')
    st.stashes = len([ln for ln in stash.splitlines() if ln.strip()])


def _read_remote(st: RepoStatus):
    if st.has_upstream:
        out = run_git(st.path, 'rev-list', '--left-right', '--count', 'HEAD...@{u}')
        ahead, behind = out.split()
        st.ahead, st.behind = int(ahead), int(behind)
    out = run_git(st.path, 'rev-parse', '--absolute-git-dir', '--git-common-dir').splitlines()
    mtimes = []
    for d in out:
        fetch_head = (Path(st.path) / d.strip()) / 'FETCH_HEAD'
        try:
            mtimes.append(fetch_head.stat().st_mtime)
        except OSError:
            pass
    st.last_fetch = max(mtimes) if mtimes else None


def get_repo_status(path, op_error: Optional[str] = None,
                    op_error_summary: str = '') -> RepoStatus:
    """
    Compute the raw status of a repository (local only, no network).

    ``op_error`` is an error from a previous network operation (fetch/pull) which is
    kept on the repo until that operation succeeds again.
    """
    st = RepoStatus(path=Path(path))
    try:
        _read_local(st)
        _read_remote(st)
    except GitError as exc:
        st.error = str(exc)
        st.error_summary = summarize_error(st.error)
        return st
    except ValueError as exc:
        st.error = f'unexpected git output: {exc}'
        st.error_summary = 'Git error'
        return st
    if op_error:
        st.error = op_error
        st.error_summary = op_error_summary or summarize_error(op_error)
    return st


def is_stale(st: RepoStatus, stale_hours: float = DEFAULT_STALE_HOURS,
             now: Optional[float] = None) -> bool:
    """Return True if the repo was never fetched or the last fetch is older than the limit."""
    if st.last_fetch is None:
        return True
    now = time.time() if now is None else now
    return now - st.last_fetch > stale_hours * 3600.0


def derive_status(st: RepoStatus, stale_hours: float = DEFAULT_STALE_HOURS,
                  now: Optional[float] = None) -> Status:
    """Derive the single badge label, highest severity wins."""
    if st.error:
        return Status.ERROR
    if (st.ahead > 0 and st.behind > 0) or (st.modified > 0 and st.behind > 0):
        return Status.DIVERGED
    if st.modified > 0:
        return Status.MODIFIED
    if st.ahead > 0 or st.detached or not st.has_upstream:
        return Status.UNPUSHED
    if is_stale(st, stale_hours, now):
        return Status.STALE
    if st.behind > 0:
        return Status.BEHIND
    return Status.OK


def format_age(seconds: float) -> str:
    """Human readable age: '5 min', '3 h', '4 d'."""
    seconds = max(0.0, seconds)
    if seconds < 3600:
        return f'{int(seconds // 60)} min'
    if seconds < 48 * 3600:
        return f'{int(seconds // 3600)} h'
    return f'{int(seconds // 86400)} d'


def _plural(n: int, word: str) -> str:
    return f'{n} {word}' if n == 1 else f'{n} {word}s'


def format_info(st: RepoStatus, stale_hours: float = DEFAULT_STALE_HOURS,
                now: Optional[float] = None) -> str:
    """Info text: only the non-zero parts joined by ' · ', or 'Up to date'."""
    if st.error:
        return st.error_summary or 'Error'
    parts = []
    if st.modified:
        parts.append(_plural(st.modified, 'file') + ' changed')
    if st.untracked:
        parts.append(f'{st.untracked} untracked')
    if st.behind:
        parts.append(f'{st.behind} behind')
    if st.ahead:
        parts.append(f'{st.ahead} ahead')
    if st.detached:
        parts.append('detached HEAD')
    elif st.upstream_gone:
        parts.append('upstream gone')
    elif not st.has_upstream:
        parts.append('no upstream')
    if st.stashes:
        parts.append('stash' if st.stashes == 1 else f'{st.stashes} stashes')
    if is_stale(st, stale_hours, now):
        if st.last_fetch is None:
            parts.append('never fetched')
        else:
            now = time.time() if now is None else now
            parts.append(f'fetched {format_age(now - st.last_fetch)} ago')
    return ' · '.join(parts) or 'Up to date'


@dataclass
class RepoReport:
    """Everything the GUI shows for one repository."""

    info: RepoInfo
    status: RepoStatus
    label: Status
    text: str

    @property
    def can_pull(self) -> bool:
        """Safe to fast-forward: behind, clean, nothing local, upstream set, no error."""
        st = self.status
        return (self.label in (Status.BEHIND, Status.STALE) and st.behind > 0
                and st.modified == 0 and st.ahead == 0 and st.has_upstream
                and not st.detached and not st.error)


def make_report(info: RepoInfo, stale_hours: float = DEFAULT_STALE_HOURS,
                op_error: Optional[str] = None, op_error_summary: str = '',
                now: Optional[float] = None) -> RepoReport:
    """Compute status, label and info text for a discovered repository."""
    st = get_repo_status(info.path, op_error, op_error_summary)
    return RepoReport(info=info, status=st, label=derive_status(st, stale_hours, now),
                      text=format_info(st, stale_hours, now))


def sort_key(report: RepoReport):
    """Sort by severity, then alphabetically."""
    return (report.label.severity, report.info.name.lower(), report.info.rel_path)


# --------------------------------------------------------------------------- network ops

def fetch_repo(path, timeout: float = FETCH_TIMEOUT):
    """Run ``git fetch --prune``; raises GitError on failure."""
    run_git(path, 'fetch', '--prune', timeout=timeout)


def pull_ff_only(path, timeout: float = PULL_TIMEOUT):
    """Fast-forward pull, refusing if the working tree is dirty or the branch has local commits."""
    st = get_repo_status(path)
    if st.error:
        raise GitError(f'refusing to pull: {st.error}')
    if st.modified:
        raise GitError('refusing to pull: working tree has modified files')
    if st.detached or not st.has_upstream:
        raise GitError('refusing to pull: no upstream branch (or detached HEAD)')
    if st.ahead:
        raise GitError('refusing to pull: branch has unpushed commits')
    run_git(path, 'pull', '--ff-only', '--no-rebase', timeout=timeout)
