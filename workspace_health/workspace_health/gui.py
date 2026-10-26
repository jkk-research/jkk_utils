"""
CustomTkinter GUI for workspace_health.

All git work runs in a ThreadPoolExecutor; worker threads never touch Tk widgets; they
post callables to a queue which the main thread drains with ``after()``.
"""

from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import platform
import queue
import shutil
import subprocess
import sys
import time
import tkinter
from tkinter import filedialog, font as tkfont, messagebox
import webbrowser

import customtkinter as ctk

from . import git_status as gs
from .git_status import NEEDS_ATTENTION, Status

MAX_WORKERS = 8
POLL_MS = 50
LEGEND_ORDER = (Status.OK, Status.BEHIND, Status.UNPUSHED, Status.MODIFIED,
                Status.DIVERGED, Status.STALE, Status.ERROR)
DARK_TEXT_BADGES = (Status.BEHIND, Status.STALE, Status.UNPUSHED, Status.MODIFIED)
FILTERS = (
    ('all', 'All', lambda r: True),
    ('attention', 'Needs attention', lambda r: r.label in NEEDS_ATTENTION),
    ('behind', 'Behind', lambda r: r.label == Status.BEHIND),
    ('ok', 'OK', lambda r: r.label == Status.OK),
)


def shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit - 1] + '…'


def display_path(path) -> str:
    """Show the home directory as ``~``."""
    path = str(path)
    home = str(Path.home())
    if path == home or path.startswith(home + os.sep):
        return '~' + path[len(home):]
    return path


def open_in_file_manager(path):
    path = str(path)
    if sys.platform.startswith('win'):
        os.startfile(path)  # noqa: S606
        return
    if sys.platform == 'darwin':
        cmd = ['open', path]
    elif 'microsoft' in platform.release().lower() and shutil.which('explorer.exe'):
        win_path = subprocess.run(['wslpath', '-w', path], capture_output=True,
                                  text=True).stdout.strip() or path
        cmd = ['explorer.exe', win_path]
    else:
        cmd = ['xdg-open', path]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


def open_in_vscode(path):
    code = shutil.which('code')
    if code is None:
        raise RuntimeError("VS Code command 'code' not found on PATH.")
    subprocess.Popen([code, str(path)], stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True)


def bind_tree(widget, sequence, func):
    """Bind an event on a widget and all its (CTk internal) descendants."""
    tkinter.Misc.bind(widget, sequence, func, '+')
    for child in widget.winfo_children():
        bind_tree(child, sequence, func)


class Tooltip:
    """Small delayed tooltip shown while the pointer is over the given widgets."""

    def __init__(self, widgets, text):
        self.text = text
        self.root = widgets[0].winfo_toplevel()
        self.tip = None
        self.job = None
        for w in widgets:
            bind_tree(w, '<Enter>', self._enter)
            bind_tree(w, '<Leave>', self._leave)

    def _cancel(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None

    def _enter(self, _event):
        self._cancel()
        if self.tip is None:
            self.job = self.root.after(400, self._show)

    def _leave(self, _event):
        self._cancel()
        self.job = self.root.after(80, self._hide)

    def _show(self):
        self.job = None
        x, y = self.root.winfo_pointerxy()
        self.tip = tkinter.Toplevel(self.root)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f'+{x + 14}+{y + 14}')
        tkinter.Label(self.tip, text=self.text, justify='left', wraplength=640,
                      background='#2b2b2b', foreground='#f0f0f0', relief='solid',
                      borderwidth=1, padx=8, pady=6).pack()

    def _hide(self):
        self.job = None
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class RepoRow(ctk.CTkFrame):
    """One repository: dot, name/owner, branch, info text, badge, menu button."""

    def __init__(self, master, report: gs.RepoReport, fonts, on_menu):
        super().__init__(master, fg_color=('gray86', 'gray20'), corner_radius=6)
        self.report = report
        info, st, label = report.info, report.status, report.label
        self.grid_columnconfigure(1, minsize=300)
        self.grid_columnconfigure(2, minsize=130)
        self.grid_columnconfigure(3, weight=1)

        dot = ctk.CTkFrame(self, width=12, height=12, corner_radius=3, fg_color=label.color)
        dot.grid(row=0, column=0, padx=(12, 10), pady=12)

        names = ctk.CTkFrame(self, fg_color='transparent')
        names.grid(row=0, column=1, sticky='w', pady=4)
        ctk.CTkLabel(names, text=shorten(info.name, 34), font=fonts['bold'], anchor='w',
                     height=18).pack(anchor='w')
        ctk.CTkLabel(names, text=shorten(f'{info.owner} · {info.rel_path}', 48),
                     font=fonts['small'], text_color=('gray40', 'gray60'), anchor='w',
                     height=14).pack(anchor='w')

        branch = st.branch or '—'
        if st.detached:
            branch = f'({branch})'
        ctk.CTkLabel(self, text=shorten(branch, 16), font=fonts['mono'],
                     text_color=('gray30', 'gray70'), anchor='w').grid(
            row=0, column=2, sticky='w', padx=(0, 10))

        info_label = ctk.CTkLabel(self, text=report.text, anchor='w',
                                  text_color=('gray20', 'gray80'))
        info_label.grid(row=0, column=3, sticky='w', padx=(0, 10))

        badge = ctk.CTkLabel(self, text=label.label, fg_color=label.color, corner_radius=6,
                             width=86, height=24, font=fonts['badge'],
                             text_color='#1a1a1a' if label in DARK_TEXT_BADGES else 'white')
        badge.grid(row=0, column=4, padx=(0, 4))

        menu_btn = ctk.CTkButton(self, text='⋮', width=26, height=26, fg_color='transparent',
                                 hover_color=('gray75', 'gray30'),
                                 text_color=('gray20', 'gray80'),
                                 command=lambda: on_menu(self, None))
        menu_btn.grid(row=0, column=5, padx=(0, 8))

        tip = st.error if st.error else None
        if tip:
            Tooltip([info_label, badge], tip)
        else:
            text = [f'{info.url}', str(info.path)]
            if st.upstream:
                text.append(f'upstream: {st.upstream}' + (' (gone)' if st.upstream_gone else ''))
            Tooltip([info_label], '\n'.join(text))

        handler = (lambda e: on_menu(self, e))
        bind_tree(self, '<Button-3>', handler)
        if sys.platform == 'darwin':
            bind_tree(self, '<Button-2>', handler)


class App(ctk.CTk):
    """Main window."""

    def __init__(self, ws_path, stale_hours=gs.DEFAULT_STALE_HOURS):
        super().__init__()
        self.stale_hours = stale_hours
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS,
                                           thread_name_prefix='git')
        self.queue = queue.Queue()
        self.reports = []
        self.rows = []
        self.op_errors = {}   # repo path -> (message, summary), kept until the op succeeds
        self.scanned_ws = None
        self.busy = False
        self.filter_key = 'all'
        self.filter_values = []

        self.title('Workspace Health')
        self.geometry('1180x700')
        self.minsize(1100, 480)
        self.protocol('WM_DELETE_WINDOW', self._on_close)

        mono = tkfont.nametofont('TkFixedFont').actual()['family']
        self.fonts = {
            'title': ctk.CTkFont(size=24, weight='bold'),
            'bold': ctk.CTkFont(size=14, weight='bold'),
            'small': ctk.CTkFont(size=11),
            'mono': ctk.CTkFont(family=mono, size=12),
            'badge': ctk.CTkFont(size=12, weight='bold'),
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()

        self.ws_var.set(display_path(Path(ws_path).expanduser()))
        self.after(POLL_MS, self._poll)
        self.after(100, self.scan)

    # ------------------------------------------------------------------ layout

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=200, corner_radius=0)
        side.grid(row=0, column=0, sticky='nsew')
        side.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(side, text='Workspace\nHealth', font=self.fonts['title']).grid(
            row=0, column=0, padx=20, pady=(20, 16))
        self.scan_btn = ctk.CTkButton(side, text='Scan workspace', command=self.scan)
        self.scan_btn.grid(row=1, column=0, padx=20, pady=6)
        self.fetch_btn = ctk.CTkButton(side, text='Fetch all', command=self.fetch_all)
        self.fetch_btn.grid(row=2, column=0, padx=20, pady=6)
        self.pull_btn = ctk.CTkButton(side, text='Pull all (ff-only)', command=self.pull_all)
        self.pull_btn.grid(row=3, column=0, padx=20, pady=6)

        legend = ctk.CTkFrame(side, fg_color='transparent')
        legend.grid(row=4, column=0, padx=20, pady=(20, 0), sticky='ew')
        legend.grid_columnconfigure(1, weight=1)
        self.legend_counts = {}
        for i, status in enumerate(LEGEND_ORDER):
            ctk.CTkFrame(legend, width=10, height=10, corner_radius=3,
                         fg_color=status.color).grid(row=i, column=0, padx=(0, 8))
            ctk.CTkLabel(legend, text=status.label, anchor='w', height=24).grid(
                row=i, column=1, sticky='w')
            count = ctk.CTkLabel(legend, text='0', anchor='e', height=24,
                                 text_color=('gray40', 'gray60'))
            count.grid(row=i, column=2, sticky='e')
            self.legend_counts[status] = count

        ctk.CTkLabel(side, text='Appearance Mode:').grid(row=6, column=0, padx=20, pady=(10, 0))
        mode = ctk.CTkOptionMenu(side, values=['Dark', 'Light', 'System'],
                                 command=self._set_appearance)
        mode.set('Dark')
        mode.grid(row=7, column=0, padx=20, pady=(4, 10))
        ctk.CTkLabel(side, text='UI Scaling:').grid(row=8, column=0, padx=20, pady=(10, 0))
        scaling = ctk.CTkOptionMenu(side, values=['80%', '90%', '100%', '110%', '120%', '150%'],
                                    command=self._set_scaling)
        scaling.set('100%')
        scaling.grid(row=9, column=0, padx=20, pady=(4, 20))

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color='transparent')
        main.grid(row=0, column=1, sticky='nsew', padx=20, pady=(14, 14))
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(main, fg_color='transparent')
        top.grid(row=0, column=0, sticky='ew')
        top.grid_columnconfigure(0, weight=1)
        self.ws_var = tkinter.StringVar()
        entry = ctk.CTkEntry(top, textvariable=self.ws_var, height=30)
        entry.grid(row=0, column=0, sticky='ew', padx=(0, 12))
        entry.bind('<Return>', lambda _e: self.scan())
        ctk.CTkButton(top, text='Browse…', width=120, height=30, fg_color='transparent',
                      border_width=2, text_color=('gray10', 'gray90'),
                      command=self._browse).grid(row=0, column=1)

        self.filter_btn = ctk.CTkSegmentedButton(main, command=self._on_filter)
        self.filter_btn.grid(row=1, column=0, sticky='w', pady=(12, 12))
        self._update_filter_values()

        self.list_frame = ctk.CTkScrollableFrame(main, label_text='')
        self.list_frame.grid(row=2, column=0, sticky='nsew')
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.empty_label = ctk.CTkLabel(self.list_frame, text='', text_color=('gray40', 'gray60'))

        bottom = ctk.CTkFrame(main, fg_color='transparent')
        bottom.grid(row=3, column=0, sticky='ew', pady=(10, 0))
        bottom.grid_columnconfigure(0, weight=1)
        self.progress = ctk.CTkProgressBar(bottom)
        self.progress.grid(row=0, column=0, sticky='ew', padx=(0, 12))
        self.progress.set(0)
        self.status_label = ctk.CTkLabel(bottom, text='Not scanned yet', width=140, anchor='e')
        self.status_label.grid(row=0, column=1)

    # ------------------------------------------------------------------ thread plumbing

    def _call_main(self, func, *args):
        """Thread-safe: run ``func(*args)`` on the Tk main thread."""
        self.queue.put((func, args))

    def _poll(self):
        try:
            while True:
                func, args = self.queue.get_nowait()
                func(*args)
        except queue.Empty:
            pass
        self.after(POLL_MS, self._poll)

    def _run_parallel(self, verb, items, worker, on_done):
        """Run ``worker(item)`` for every item in the pool, then ``on_done([(item, future)])``."""
        total = len(items)
        results = []
        if total == 0:
            on_done(results)
            return
        self.status_label.configure(text=f'{verb}… 0/{total}')

        def step(item, future):
            results.append((item, future))
            self.progress.set(len(results) / total)
            self.status_label.configure(text=f'{verb}… {len(results)}/{total}')
            if len(results) == total:
                on_done(results)

        for item in items:
            future = self.executor.submit(worker, item)
            future.add_done_callback(lambda f, item=item: self._call_main(step, item, f))

    def _set_busy(self, busy):
        self.busy = busy
        state = 'disabled' if busy else 'normal'
        self.scan_btn.configure(state=state)
        self.fetch_btn.configure(state='disabled' if busy or not self.reports else 'normal')
        has_behind = any(r.label == Status.BEHIND for r in self.reports)
        self.pull_btn.configure(state='disabled' if busy or not has_behind else 'normal')
        if busy:
            self.progress.set(0)

    # ------------------------------------------------------------------ scan

    def _workspace(self):
        return Path(self.ws_var.get().strip() or '~/ros2_ws').expanduser().resolve()

    def scan(self):
        if self.busy:
            return
        ws = self._workspace()
        if not ws.is_dir():
            messagebox.showerror('Workspace Health', f'Workspace not found:\n{ws}', parent=self)
            return
        self._set_busy(True)
        self.status_label.configure(text='Discovering…')
        errors = dict(self.op_errors)
        stale_hours = self.stale_hours

        def worker(info):
            msg, summary = errors.get(info.path, (None, ''))
            return gs.make_report(info, stale_hours, msg, summary)

        def discovered(future):
            try:
                repos = future.result()
            except Exception as exc:  # noqa: BLE001
                self._set_busy(False)
                self.status_label.configure(text='Scan failed')
                messagebox.showerror('Workspace Health', f'Scan failed:\n{exc}', parent=self)
                return
            self._run_parallel('Scanning', repos, worker, lambda res: self._scanned(ws, res))

        self.executor.submit(gs.discover_github_repos, ws).add_done_callback(
            lambda f: self._call_main(discovered, f))

    def _scanned(self, ws, results):
        reports = []
        for info, future in results:
            try:
                reports.append(future.result())
            except Exception as exc:  # noqa: BLE001
                st = gs.RepoStatus(info.path, error=str(exc), error_summary='Internal error')
                reports.append(gs.RepoReport(info, st, Status.ERROR, st.error_summary))
        self.reports = sorted(reports, key=gs.sort_key)
        self.scanned_ws = ws
        self._rebuild_rows()
        self._set_busy(False)
        self.progress.set(1)
        self.status_label.configure(text=time.strftime('Last scan %H:%M'))

    # ------------------------------------------------------------------ network operations

    def _network_op(self, verb, label, func, reports):
        """Fetch or pull the given repos, record errors, then re-scan."""
        if self.busy or not reports:
            return
        self._set_busy(True)

        def worker(report):
            func(report.info.path)

        def done(results):
            for report, future in results:
                exc = future.exception()
                if exc is None:
                    self.op_errors.pop(report.info.path, None)
                else:
                    msg = str(exc)
                    self.op_errors[report.info.path] = (msg, gs.summarize_error(msg, label))
            self._set_busy(False)
            self.scan()

        self._run_parallel(verb, list(reports), worker, done)

    def fetch_all(self):
        self._network_op('Fetching', 'Fetch failed', gs.fetch_repo, self.reports)

    def pull_all(self):
        targets = [r for r in self.reports if r.label == Status.BEHIND]
        if not targets:
            return
        names = '\n'.join(f'  • {r.info.name}  ({r.status.branch}, {r.status.behind} behind)'
                          for r in targets)
        if not messagebox.askyesno(
                'Pull all (ff-only)',
                f'Run "git pull --ff-only" in these {len(targets)} repositories?\n\n{names}',
                parent=self):
            return
        self._network_op('Pulling', 'Pull failed', gs.pull_ff_only, targets)

    # ------------------------------------------------------------------ list

    def _counts(self):
        counts = {s: 0 for s in Status}
        for r in self.reports:
            counts[r.label] += 1
        return counts

    def _update_filter_values(self):
        self.filter_values = [f'{name} ({sum(1 for r in self.reports if pred(r))})'
                              for _, name, pred in FILTERS]
        self.filter_btn.configure(values=self.filter_values)
        keys = [key for key, _, _ in FILTERS]
        self.filter_btn.set(self.filter_values[keys.index(self.filter_key)])

    def _on_filter(self, value):
        if value in self.filter_values:
            self.filter_key = FILTERS[self.filter_values.index(value)][0]
        self._layout_rows()

    def _rebuild_rows(self):
        for row in self.rows:
            row.destroy()
        self.rows = [RepoRow(self.list_frame, r, self.fonts, self._show_menu)
                     for r in self.reports]
        counts = self._counts()
        for status, label in self.legend_counts.items():
            label.configure(text=str(counts[status]))
        self._update_filter_values()
        self._layout_rows()

    def _layout_rows(self):
        pred = next(p for key, _, p in FILTERS if key == self.filter_key)
        shown = 0
        for row in self.rows:
            row.grid_forget()
        for row in self.rows:
            if pred(row.report):
                row.grid(row=shown, column=0, sticky='ew', padx=4, pady=3)
                shown += 1
        ws = self.scanned_ws or self._workspace()
        root = ws / 'src' if (ws / 'src').is_dir() else ws
        n = len(self.reports)
        header = f'{display_path(root)} — {n} repositor{"y" if n == 1 else "ies"}'
        if shown != n:
            header += f' ({shown} shown)'
        self.list_frame.configure(label_text=header)
        if shown == 0:
            text = ('No GitHub repositories found.' if n == 0
                    else 'No repositories match this filter.')
            self.empty_label.configure(text=text)
            self.empty_label.grid(row=0, column=0, pady=30)
        else:
            self.empty_label.grid_forget()

    # ------------------------------------------------------------------ context menu

    def _show_menu(self, row, event):
        report = row.report
        dark = ctk.get_appearance_mode() == 'Dark'
        menu = tkinter.Menu(self, tearoff=0,
                            background='#2b2b2b' if dark else '#f2f2f2',
                            foreground='#f0f0f0' if dark else '#1a1a1a',
                            activebackground='#1f6aa5', activeforeground='white',
                            disabledforeground='gray50')
        path = report.info.path
        menu.add_command(label='Open folder', command=lambda: self._safe(
            open_in_file_manager, path))
        menu.add_command(label='Open on GitHub', command=lambda: self._safe(
            webbrowser.open, report.info.web_url))
        menu.add_command(label='Copy path', command=lambda: self._copy(str(path)))
        menu.add_command(label='Open in VS Code', command=lambda: self._safe(
            open_in_vscode, path))
        menu.add_separator()
        menu.add_command(label='Fetch this repo',
                         state='disabled' if self.busy else 'normal',
                         command=lambda: self._network_op('Fetching', 'Fetch failed',
                                                          gs.fetch_repo, [report]))
        menu.add_command(label='Pull (ff-only) this repo',
                         state='normal' if report.can_pull and not self.busy else 'disabled',
                         command=lambda: self._network_op('Pulling', 'Pull failed',
                                                          gs.pull_ff_only, [report]))
        if event is not None:
            x, y = event.x_root, event.y_root
        else:
            x, y = self.winfo_pointerxy()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _safe(self, func, *args):
        try:
            func(*args)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror('Workspace Health', str(exc), parent=self)

    # ------------------------------------------------------------------ misc

    def _browse(self):
        initial = self._workspace()
        path = filedialog.askdirectory(parent=self, title='Select ROS 2 workspace',
                                       initialdir=str(initial if initial.is_dir() else
                                                      Path.home()))
        if path:
            self.ws_var.set(display_path(path))
            self.scan()

    @staticmethod
    def _set_appearance(mode):
        ctk.set_appearance_mode(mode)

    @staticmethod
    def _set_scaling(value):
        ctk.set_widget_scaling(int(value.rstrip('%')) / 100)

    def _on_close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()


def run(ws_path, stale_hours=gs.DEFAULT_STALE_HOURS):
    """Create and run the GUI (blocks until the window is closed)."""
    ctk.set_appearance_mode('Dark')
    ctk.set_default_color_theme('blue')
    app = App(ws_path, stale_hours)
    app.mainloop()
