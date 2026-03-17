# quick, vibe coded visualization tool for comparing two 2D trajectories
 
import sys
import json
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
from mcap_ros2.decoder import DecoderFactory
from mcap.reader import make_reader

# --- Beolvasás ---
file_name = '/mnt/c/bag/lokalizacio02_no_cam_lexus3_2026-03-06_09-37_0.mcap'
with open(file_name, "rb") as f:
    reader = make_reader(f, decoder_factories=[DecoderFactory()])
    channels = reader.get_summary().channels.items()
    print("Available topics:")
    for index, (_, ch) in enumerate(channels):
        print("%2d. %s" % (index+1, ch.topic))
    print("")

    i = 0
    pose_nova = []
    pose_ndtp = []
    for schema, channel, message, ros_msg in reader.iter_decoded_messages():
        if channel.topic == "/lexus3/gps/nova/current_pose":
            pose_nova.append(ros_msg)
        if channel.topic == "/localization/pose_estimator/pose":
            pose_ndtp.append(ros_msg)
        if i % 1000 == 0:
            print(".", end="")
        i += 1

print(f"\nNova: {len(pose_nova)}, NDTP: {len(pose_ndtp)}")

x_nova_c = np.array([p.pose.position.x for p in pose_nova])
y_nova_c = np.array([p.pose.position.y for p in pose_nova])
x_ndtp_i = np.array([p.pose.position.x for p in pose_ndtp])
y_ndtp_i = np.array([p.pose.position.y for p in pose_ndtp])


# --- Segédfüggvények ---
def apply_transform(x, y, dx, dy, angle_deg):
    angle_rad = np.radians(angle_deg)
    cx, cy = np.mean(x), np.mean(y)
    xc = x - cx
    yc = y - cy
    xr = xc * np.cos(angle_rad) - yc * np.sin(angle_rad)
    yr = xc * np.sin(angle_rad) + yc * np.cos(angle_rad)
    return xr + cx + dx, yr + cy + dy


def compute_stats(xn, yn, xd, yd):
    n = min(len(xn), len(xd))
    dx = xn[:n] - xd[:n]
    dy = yn[:n] - yd[:n]
    dist = np.sqrt(dx**2 + dy**2)
    return np.mean(dx), np.mean(dy), np.mean(dist), np.std(dist)


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
win.setWindowTitle("NDTP trajektória igazítás")
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

ctrl_layout.addWidget(QtWidgets.QLabel("<b>Eltolás és forgatás</b>"))

# --- Csúszkák ---
# X eltolás: ±500 m, 0.1 m felbontás -> *10
row_x, slider_x, lbl_x = make_slider("Δx [m]", -5000, 5000, 0)
ctrl_layout.addLayout(row_x)

# Y eltolás
row_y, slider_y, lbl_y = make_slider("Δy [m]", -5000, 5000, 0)
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
for label, delta in [("−1", -10), ("−0.1", -1), ("+0.1", 1), ("+1", 10)]:
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
for label, delta in [("−1", -10), ("−0.1", -1), ("+0.1", 1), ("+1", 10)]:
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
ctrl_layout.addWidget(stats_label)

ctrl_layout.addStretch()

# Reset + Mentés
btn_row = QtWidgets.QHBoxLayout()
reset_btn = QtWidgets.QPushButton("↺  Reset")
save_btn  = QtWidgets.QPushButton("💾  Mentés (JSON)")
for b in [reset_btn, save_btn]:
    b.setStyleSheet("font-size: 13px; padding: 6px;")
    btn_row.addWidget(b)
ctrl_layout.addLayout(btn_row)


# --- Refresh ---
def refresh():
    dx    = slider_x.value() / 10.0
    dy    = slider_y.value() / 10.0
    angle = slider_r.value() / 100.0

    lbl_x.setText(f"{dx:+.1f} m")
    lbl_y.setText(f"{dy:+.1f} m")
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
        'translation_x_m': round(slider_x.value() / 10.0, 4),
        'translation_y_m': round(slider_y.value() / 10.0, 4),
        'rotation_deg':    round(slider_r.value() / 100.0, 4),
    }
    fname, _ = QtWidgets.QFileDialog.getSaveFileName(
        win, "Paraméterek mentése", "ndtp_transform.json", "JSON (*.json)"
    )
    if fname:
        with open(fname, 'w') as f:
            json.dump(params, f, indent=2)
        print(f"Mentve: {fname}\n{json.dumps(params, indent=2)}")

save_btn.clicked.connect(on_save)


# --- Indítás ---
refresh()
win.show()
app.exec_()