// similar functionality to plot_and_compare_pose.py python script but in typescript for foxglove studio
// https://github.com/jkk-research/jkk_utils/blob/ros2/mcap_scripts/plot_and_compare_pose.py

import { Input } from "./types";

// --- Input / Output setup ---
export const inputs = [
  "/localization/pose_estimator/pose", // NDT
  "/lexus3/gps/nova/current_pose", // GPS
];
export const output = "/studio_script/pose_delta";

// Output type must be fixed (no unions/optional)
const MAX_BUFFER = 200; // keep last N messages per topic
const TOL_SEC = 0.24; // max allowed time diff for pairing

type Output = {
  dx: number; // GPS minus NDT in NDT local frame (x)
  dy: number; // GPS minus NDT in NDT local frame (y)
  d: number; // sqrt(dx^2 + dy^2)
  dt: number; // |t_gps - t_ndt| [s]
  paired: boolean; // true if within tolerance
};

type InputEvent =
  | Input<"/localization/pose_estimator/pose">
  | Input<"/lexus3/gps/nova/current_pose">;

type Timed<T> = { t: number; msg: T };

type Globals = {
  ndtBuf: Timed<any>[];
  gpsBuf: Timed<any>[];
};

// ---- Helpers ----
function timeFromHeaderOrEvent(msg: any, event: any): number {
  const hs = msg?.header?.stamp;
  if (typeof hs?.sec === "number" && typeof hs?.nsec === "number") {
    return hs.sec + hs.nsec * 1e-9;
  }
  const rt = event?.receiveTime;
  if (typeof rt?.sec === "number" && typeof rt?.nsec === "number") {
    return rt.sec + rt.nsec * 1e-9;
  }
  return 0; // fallback
}

function yawFromQuat(
  q: { x: number; y: number; z: number; w: number } | undefined,
): number {
  if (!q) return 0;
  const siny_cosp = 2 * (q.w * q.z + q.x * q.y);
  const cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z);
  return Math.atan2(siny_cosp, cosy_cosp);
}

function pushBuf<T>(buf: Timed<T>[], item: Timed<T>) {
  buf.push(item);
  if (buf.length > MAX_BUFFER) buf.shift();
}

function findNearest<T>(buf: Timed<T>[], t: number): Timed<T> | undefined {
  if (buf.length === 0) return;
  // linear scan is fine for small buffers; replace with binary search if needed
  let best: Timed<T> | undefined = undefined;
  let bestDt = Infinity;
  for (const x of buf) {
    const dt = Math.abs(x.t - t);
    if (dt < bestDt) {
      bestDt = dt;
      best = x;
    }
  }
  if (best && bestDt <= TOL_SEC) return best;
  return;
}


export default function script(
  event: InputEvent,
  globals: Globals,
): Output | undefined {
  globals.ndtBuf ??= [];
  globals.gpsBuf ??= [];

  const t = timeFromHeaderOrEvent(event.message, event);

  if (event.topic === "/localization/pose_estimator/pose") {
    pushBuf(globals.ndtBuf, { t, msg: event.message });
    // Only compute on GPS arrivals to avoid oversampling noise
    return;
  }

  if (event.topic === "/lexus3/gps/nova/current_pose") {
    pushBuf(globals.gpsBuf, { t, msg: event.message });

    const gps = { t, msg: event.message };
    const ndt = findNearest(globals.ndtBuf, gps.t);
    if (!ndt) {
      // Emit a deterministic “unpaired” sample (fixed schema)
      return { dx: 0, dy: 0, d: 0, dt: Infinity, paired: false };
    }

    // World-frame delta
    const dxW = gps.msg.pose.position.x - ndt.msg.pose.position.x;
    const dyW = gps.msg.pose.position.y - ndt.msg.pose.position.y;

    // Rotate into NDT local frame (z-yaw)
    const yaw = yawFromQuat(ndt.msg.pose.orientation);
    const c = Math.cos(-yaw),
      s = Math.sin(-yaw);
    const dx = c * dxW - s * dyW;
    const dy = s * dxW + c * dyW;

    const d = Math.hypot(dx, dy);
    const dt = Math.abs(gps.t - ndt.t);

    return { 
      dx, 
      dy, 
      d, 
      dt, 
      paired: true 
    };
  }

  return;
}
