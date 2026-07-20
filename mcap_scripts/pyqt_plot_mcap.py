# quick, vibe coded visualization tool for comparing two 2D trajectories
# 


import sys
import json
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
from mcap_ros2.decoder import DecoderFactory
from mcap.reader import make_reader
from scipy.spatial import cKDTree

# --- Beolvasás ---
# file_name = '/mnt/c/bag/lokalizacio06_no_cam_lexus3_2026-03-26_17-06_0.mcap'
# file_name = '/mnt/c/bag/lokalizacio07_no_cam_lexus3_2026-03-26_17-17_0.mcap'
# file_name = '/mnt/bag/2026-07-20_localization/kiscsarnok02_lexus3_2026-07-20_13-01/kiscsarnok02_lexus3_2026-07-20_13-01_0.mcap'
file_name = '/mnt/bag/2026-07-20_localization/thome02_lexus3_2026-07-20_14-15/thome02_lexus3_2026-07-20_14-15_0.mcap'
with open(file_name, "rb") as f:
    reader = make_reader(f, decoder_factories=[DecoderFactory()])
    channels = reader.get_summary().channels.items()
    print("Available topics:")
    for index, (_, ch) in enumerate(channels):
        print("%2d. %s" % (index+1, ch.topic))
    print("")

    i = 0
    pose_nova = []  # list of (timestamp_ns, msg)
    pose_ndtp = []  # list of (timestamp_ns, msg)
    for schema, channel, message, ros_msg in reader.iter_decoded_messages():
        if channel.topic == "/lexus3/gps/nova/current_pose":
            ts = ros_msg.header.stamp.sec * 1_000_000_000 + ros_msg.header.stamp.nanosec
            pose_nova.append((ts, ros_msg))
        if channel.topic == "/localization/pose_twist_fusion_filter/pose":
            ts = ros_msg.header.stamp.sec * 1_000_000_000 + ros_msg.header.stamp.nanosec
            pose_ndtp.append((ts, ros_msg))
        if i % 1000 == 0:
            print(".", end="")
        i += 1

print(f"\nNova: {len(pose_nova)}, NDTP: {len(pose_ndtp)}")

t_nova_ns = np.array([p[0] for p in pose_nova], dtype=np.float64)
x_nova_c  = np.array([p[1].pose.position.x for p in pose_nova])
y_nova_c  = np.array([p[1].pose.position.y for p in pose_nova])
t_ndtp_ns = np.array([p[0] for p in pose_ndtp], dtype=np.float64)
x_ndtp_i  = np.array([p[1].pose.position.x for p in pose_ndtp])
y_ndtp_i  = np.array([p[1].pose.position.y for p in pose_ndtp])


# --- Segédfüggvények ---
def apply_transform(x, y, dx, dy, angle_deg):
    """SE(2) transzformáció a globális (0, 0) origó körül."""
    angle_rad = np.radians(angle_deg)
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)

    xr = x * c - y * s
    yr = x * s + y * c
    return xr + dx, yr + dy


def compute_stats(xn, yn, xd, yd):
    n = min(len(xn), len(xd))
    dx = xn[:n] - xd[:n]
    dy = yn[:n] - yd[:n]
    dist = np.sqrt(dx**2 + dy**2)
    return np.mean(dx), np.mean(dy), np.mean(dist), np.std(dist)


def umeyama_2d(src, dst):
    """Rigid 2-D alignment (no scale). Returns R (2×2) and t (2,) such that dst ≈ R @ src + t."""
    n = len(src)
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)
    src_c = src - src_mean
    dst_c = dst - dst_mean
    H = src_c.T @ dst_c / n
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1.0, d]) @ U.T
    t = dst_mean - R @ src_mean
    return R, t


def resample_polyline_2d(x, y, step_m=0.01):
    """Lineáris újramintavételezés ívhossz mentén, fix méteres lépéssel."""
    pts = np.column_stack([x, y]).astype(np.float64)
    pts = pts[np.isfinite(pts).all(axis=1)]
    if len(pts) < 2:
        raise ValueError("A trajektóriában nincs legalább 2 érvényes pont.")

    seg_len = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    keep = np.r_[True, seg_len > 1e-9]
    pts = pts[keep]
    if len(pts) < 2:
        raise ValueError("A trajektória minden pontja azonos.")

    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    total_len = s[-1]
    sample_s = np.arange(0.0, total_len, step_m, dtype=np.float64)
    if len(sample_s) == 0 or sample_s[-1] < total_len:
        sample_s = np.r_[sample_s, total_len]

    xr = np.interp(sample_s, s, pts[:, 0])
    yr = np.interp(sample_s, s, pts[:, 1])
    return np.column_stack([xr, yr])


def initial_transform_from_time(max_samples=5000):
    """Kezdő SE(2) becslés az egymást átfedő időbélyegek alapján."""
    t0 = max(t_nova_ns[0], t_ndtp_ns[0])
    t1 = min(t_nova_ns[-1], t_ndtp_ns[-1])
    if t1 <= t0:
        return None

    n = min(max_samples, max(100, min(len(t_nova_ns), len(t_ndtp_ns))))
    ts = np.linspace(t0, t1, n)

    dst = np.column_stack([
        np.interp(ts, t_nova_ns, x_nova_c),
        np.interp(ts, t_nova_ns, y_nova_c),
    ])
    src = np.column_stack([
        np.interp(ts, t_ndtp_ns, x_ndtp_i),
        np.interp(ts, t_ndtp_ns, y_ndtp_i),
    ])

    R, t = umeyama_2d(src, dst)

    # Egyszeri robusztus újraillesztés: a legrosszabb 10% időpár kihagyása.
    residual = np.linalg.norm((R @ src.T).T + t - dst, axis=1)
    limit = np.quantile(residual, 0.90)
    mask = residual <= limit
    if mask.sum() >= 3:
        R, t = umeyama_2d(src[mask], dst[mask])
    return R, t


def initial_transform_from_progress(src, dst, n_samples=3000):
    """Fallback kezdőbecslés normalizált pályapozíció alapján."""
    n = min(n_samples, len(src), len(dst))
    u = np.linspace(0.0, 1.0, n)
    src_idx = u * (len(src) - 1)
    dst_idx = u * (len(dst) - 1)

    src_s = np.column_stack([
        np.interp(src_idx, np.arange(len(src)), src[:, 0]),
        np.interp(src_idx, np.arange(len(src)), src[:, 1]),
    ])
    dst_s = np.column_stack([
        np.interp(dst_idx, np.arange(len(dst)), dst[:, 0]),
        np.interp(dst_idx, np.arange(len(dst)), dst[:, 1]),
    ])
    return umeyama_2d(src_s, dst_s)


def icp_2d(src, dst, R_init, t_init, max_iterations=60,
           trim_fraction=0.85, max_corr_dist_m=1.5):
    """Trimmed point-to-point 2D ICP. dst ≈ R @ src + t."""
    tree = cKDTree(dst)
    R = R_init.copy()
    t = t_init.copy()
    previous_rmse = np.inf

    for iteration in range(max_iterations):
        transformed = (R @ src.T).T + t
        distances, indices = tree.query(transformed, k=1, workers=-1)

        quantile_limit = np.quantile(distances, trim_fraction)
        distance_limit = min(max_corr_dist_m, quantile_limit)
        mask = distances <= distance_limit

        if mask.sum() < 20:
            raise RuntimeError(
                f"Túl kevés ICP pontpár: {mask.sum()} "
                f"(küszöb: {distance_limit:.3f} m)."
            )

        dR, dt = umeyama_2d(transformed[mask], dst[indices[mask]])
        R = dR @ R
        t = dR @ t + dt

        angle_step = abs(np.arctan2(dR[1, 0], dR[0, 0]))
        translation_step = np.linalg.norm(dt)
        rmse = np.sqrt(np.mean(distances[mask] ** 2))

        if abs(previous_rmse - rmse) < 1e-7 and translation_step < 1e-6 and angle_step < 1e-7:
            break
        previous_rmse = rmse

    transformed = (R @ src.T).T + t
    distances, _ = tree.query(transformed, k=1, workers=-1)
    inlier_limit = min(max_corr_dist_m, np.quantile(distances, trim_fraction))
    inliers = distances <= inlier_limit

    return R, t, {
        "iterations": iteration + 1,
        "pairs": int(inliers.sum()),
        "mean_m": float(np.mean(distances[inliers])),
        "rmse_m": float(np.sqrt(np.mean(distances[inliers] ** 2))),
        "p95_m": float(np.quantile(distances[inliers], 0.95)),
    }


def make_slider(label_text, range_min, range_max, initial=0):
    """Felirat + csúszka + érték kijelző egy sorban."""
    row = QtWidgets.QHBoxLayout()
    lbl = QtWidgets.QLabel(label_text)
    lbl.setFixedWidth(60)
    slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    slider.setRange(range_min, range_max)
    slider.setValue(initial)
    val_lbl = QtWidgets.QLabel("0")
    val_lbl.setFixedWidth(70)
    val_lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    row.addWidget(lbl)
    row.addWidget(slider)
    row.addWidget(val_lbl)
    return row, slider, val_lbl


# --- App ---
app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

win = QtWidgets.QWidget()
win.setWindowTitle("NDTP trajektória igazítás – globális origó")
win.resize(1400, 800)
main_layout = QtWidgets.QHBoxLayout(win)

# Plot
plot_widget = pg.PlotWidget()
plot_widget.setAspectLocked(True)
plot_widget.showGrid(x=True, y=True, alpha=0.4)
plot_widget.setLabel('left', 'y [m]')
plot_widget.setLabel('bottom', 'x [m]')
plot_widget.setTitle("Nova vs NDTP")
plot_widget.addLegend()
main_layout.addWidget(plot_widget, stretch=3)

curve_nova = plot_widget.plot(x_nova_c, y_nova_c,
                               pen=pg.mkPen('#4a90d9', width=1.5),
                               name='Nova (baseline)')
curve_ndtp = plot_widget.plot(x_ndtp_i, y_ndtp_i,
                               pen=pg.mkPen('#e05c5c', width=1.2),
                               name='NDTP')

# Jobb panel
ctrl_widget = QtWidgets.QWidget()
ctrl_widget.setFixedWidth(380)
ctrl_layout = QtWidgets.QVBoxLayout(ctrl_widget)
ctrl_layout.setSpacing(10)
main_layout.addWidget(ctrl_widget)

ctrl_layout.addWidget(QtWidgets.QLabel("<b>Eltolás és forgatás a (0,0) origó körül</b>"))

# --- Csúszkák ---
# X eltolás: ±500 m, 0.01 m felbontás -> *100
row_x, slider_x, lbl_x = make_slider("Δx [m]", -50000, 50000, 0)
ctrl_layout.addLayout(row_x)

# Y eltolás
row_y, slider_y, lbl_y = make_slider("Δy [m]", -50000, 50000, 0)
ctrl_layout.addLayout(row_y)

# Forgatás: ±180 fok, 0.01 fok felbontás -> *100
row_r, slider_r, lbl_r = make_slider("Szög [°]", -18000, 18000, 0)
ctrl_layout.addLayout(row_r)

# Finom gombok (forgatás)
fine_layout = QtWidgets.QHBoxLayout()
for label, delta in [("−1°", -100), ("−0.1°", -10), ("−0.01°", -1),
                      ("+0.01°", 1), ("+0.1°", 10), ("+1°", 100)]:
    btn = QtWidgets.QPushButton(label)
    btn.setFixedHeight(24)
    btn.clicked.connect(lambda _, d=delta: slider_r.setValue(slider_r.value() + d))
    fine_layout.addWidget(btn)
ctrl_layout.addLayout(fine_layout)

# Finom gombok (X)
fine_x = QtWidgets.QHBoxLayout()
lbl_fx = QtWidgets.QLabel("X finom:")
lbl_fx.setFixedWidth(60)
fine_x.addWidget(lbl_fx)
for label, delta in [("−1", -100), ("−0.1", -10), ("−0.01", -1),
                      ("+0.01", 1), ("+0.1", 10), ("+1", 100)]:
    btn = QtWidgets.QPushButton(label)
    btn.setFixedHeight(24)
    btn.clicked.connect(lambda _, d=delta: slider_x.setValue(slider_x.value() + d))
    fine_x.addWidget(btn)
ctrl_layout.addLayout(fine_x)

# Finom gombok (Y)
fine_y = QtWidgets.QHBoxLayout()
lbl_fy = QtWidgets.QLabel("Y finom:")
lbl_fy.setFixedWidth(60)
fine_y.addWidget(lbl_fy)
for label, delta in [("−1", -100), ("−0.1", -10), ("−0.01", -1),
                      ("+0.01", 1), ("+0.1", 10), ("+1", 100)]:
    btn = QtWidgets.QPushButton(label)
    btn.setFixedHeight(24)
    btn.clicked.connect(lambda _, d=delta: slider_y.setValue(slider_y.value() + d))
    fine_y.addWidget(btn)
ctrl_layout.addLayout(fine_y)

# Elválasztó
sep = QtWidgets.QFrame()
sep.setFrameShape(QtWidgets.QFrame.HLine)
sep.setFrameShadow(QtWidgets.QFrame.Sunken)
ctrl_layout.addWidget(sep)

# Stat kijelző
stats_label = QtWidgets.QLabel()
stats_label.setStyleSheet(
    "font-family: monospace; font-size: 12px; "
    "background: #1e1e1e; color: #ddd; padding: 10px; border-radius: 4px;"
)
stats_label.setWordWrap(True)
stats_label.setTextInteractionFlags(
    QtCore.Qt.TextSelectableByMouse |
    QtCore.Qt.TextSelectableByKeyboard
)
stats_label.setFocusPolicy(QtCore.Qt.StrongFocus)

ctrl_layout.addWidget(stats_label)

ctrl_layout.addStretch()

# Reset + Mentés + Auto align
btn_row = QtWidgets.QHBoxLayout()
reset_btn  = QtWidgets.QPushButton("↺  Reset")
save_btn   = QtWidgets.QPushButton("💾  Mentés (JSON)")
align_btn  = QtWidgets.QPushButton("⚙  Auto-calib (1 cm ICP)")
for b in [reset_btn, save_btn, align_btn]:
    b.setStyleSheet("font-size: 13px; padding: 6px;")
    btn_row.addWidget(b)
ctrl_layout.addLayout(btn_row)


# --- Refresh ---
def refresh():
    dx    = slider_x.value() / 100.0
    dy    = slider_y.value() / 100.0
    angle = slider_r.value() / 100.0

    lbl_x.setText(f"{dx:+.2f} m")
    lbl_y.setText(f"{dy:+.2f} m")
    lbl_r.setText(f"{angle:+.2f} °")

    x_t, y_t = apply_transform(x_ndtp_i, y_ndtp_i, dx, dy, angle)
    curve_ndtp.setData(x_t, y_t)

    mdx, mdy, mdist, sdist = compute_stats(x_nova_c, y_nova_c, x_t, y_t)
    stats_label.setText(
        f"Δx  átlag : {mdx:+.3f} m\n"
        f"Δy  átlag : {mdy:+.3f} m\n"
        f"2D  átlag : {mdist:.3f} m\n"
        f"2D  std   : {sdist:.3f} m\n"
        f"─────────────────────\n"
        f"t_x  : {dx:+.3f} m\n"
        f"t_y  : {dy:+.3f} m\n"
        f"szög : {angle:+.4f}°"
    )


slider_x.valueChanged.connect(lambda _: refresh())
slider_y.valueChanged.connect(lambda _: refresh())
slider_r.valueChanged.connect(lambda _: refresh())


# --- Reset ---
def on_reset():
    for s in [slider_x, slider_y, slider_r]:
        s.blockSignals(True)
        s.setValue(0)
        s.blockSignals(False)
    refresh()

reset_btn.clicked.connect(on_reset)


# --- Mentés ---
def on_save():
    params = {
        'translation_x_m': round(slider_x.value() / 100.0, 4),
        'translation_y_m': round(slider_y.value() / 100.0, 4),
        'rotation_deg':    round(slider_r.value() / 100.0, 4),
        'rotation_center': [0.0, 0.0],
        'transform': "p_out = R_z(rotation_deg) @ p_in + translation",
    }
    fname, _ = QtWidgets.QFileDialog.getSaveFileName(
        win, "Paraméterek mentése", "ndtp_transform.json", "JSON (*.json)"
    )
    if fname:
        with open(fname, 'w') as f:
            json.dump(params, f, indent=2)
        print(f"Mentve: {fname}\n{json.dumps(params, indent=2)}")

save_btn.clicked.connect(on_save)


# --- 1 cm-es auto-calib ---
def auto_calib_1cm():
    """
    1. Mindkét trajektóriát ívhossz mentén 1 cm-re lineárisan újramintázza.
    2. Időbélyeg-alapú Umeyama kezdőbecslést készít.
    3. Trimmed 2D ICP-vel finomítja az SE(2) transzformációt.
    4. Az eredményt visszaírja a GUI csúszkáira.
    """
    align_btn.setEnabled(False)
    align_btn.setText("Kalibrálás...")
    QtWidgets.QApplication.processEvents()

    try:
        step_m = 0.01
        nova_1cm = resample_polyline_2d(x_nova_c, y_nova_c, step_m)
        ndtp_1cm = resample_polyline_2d(x_ndtp_i, y_ndtp_i, step_m)

        print(
            f"1 cm resampling: Nova={len(nova_1cm)} pont, "
            f"NDTP={len(ndtp_1cm)} pont"
        )

        initial = initial_transform_from_time()
        if initial is None:
            print("Nincs időbeli átfedés, normalizált ívhossz szerinti kezdőbecslés.")
            R0, t0 = initial_transform_from_progress(ndtp_1cm, nova_1cm)
        else:
            R0, t0 = initial

        R, t_global, quality = icp_2d(
            src=ndtp_1cm,
            dst=nova_1cm,
            R_init=R0,
            t_init=t0,
            max_iterations=60,
            trim_fraction=0.85,
            max_corr_dist_m=1.5,
        )

        # A GUI és az ICP ugyanazt a globális transzformációt használja:
        # p' = R @ p + t, a (0, 0) origó körüli forgatással.
        t_slider = t_global.copy()
        angle_deg = np.degrees(np.arctan2(R[1, 0], R[0, 0]))

        if not (-500.0 <= t_slider[0] <= 500.0 and -500.0 <= t_slider[1] <= 500.0):
            raise RuntimeError(
                f"A kapott eltolás kívül esik a csúszka tartományán: "
                f"dx={t_slider[0]:.3f}, dy={t_slider[1]:.3f}"
            )

        for slider in (slider_x, slider_y, slider_r):
            slider.blockSignals(True)

        slider_x.setValue(int(round(t_slider[0] * 100.0)))
        slider_y.setValue(int(round(t_slider[1] * 100.0)))
        slider_r.setValue(int(round(angle_deg * 100.0)))

        for slider in (slider_x, slider_y, slider_r):
            slider.blockSignals(False)

        refresh()

        print(
            "Auto-calib kész:\n"
            f"  dx         = {t_slider[0]:+.4f} m\n"
            f"  dy         = {t_slider[1]:+.4f} m\n"
            f"  yaw        = {angle_deg:+.5f} deg\n"
            f"  ICP iter   = {quality['iterations']}\n"
            f"  ICP párok  = {quality['pairs']}\n"
            f"  mean       = {quality['mean_m']:.4f} m\n"
            f"  RMSE       = {quality['rmse_m']:.4f} m\n"
            f"  p95        = {quality['p95_m']:.4f} m"
        )

        stats_label.setText(
            stats_label.text()
            + "\n─────────────────────"
            + f"\nICP RMSE: {quality['rmse_m']:.3f} m"
            + f"\nICP p95 : {quality['p95_m']:.3f} m"
            + f"\nPontpár  : {quality['pairs']}"
        )

    except Exception as exc:
        print(f"Auto-calib hiba: {exc}")
        QtWidgets.QMessageBox.critical(win, "Auto-calib hiba", str(exc))
    finally:
        align_btn.setEnabled(True)
        align_btn.setText("⚙  Auto-calib (1 cm ICP)")


align_btn.clicked.connect(auto_calib_1cm)


# --- Indítás ---
refresh()
win.show()
app.exec_()