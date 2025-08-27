// similar functionality to plot_and_compare_pose.py python script but in typescript for foxglove studio
// https://github.com/jkk-research/jkk_utils/blob/ros2/mcap_scripts/plot_and_compare_pose.py

import { Input } from "./types";

// --- Input / Output setup ---
export const inputs = [
  "/localization/pose_estimator/pose",
  "/lexus3/gps/nova/current_pose",
];
export const output = "/studio_script/pose_delta";

// Output type must be fixed (no unions/optional)
type Output = {
  dx: number;
  dy: number;
  d: number;
};

// Enumerate the inputs (like sample does)
type InputEvent = Input<"/localization/pose_estimator/pose">;
// | Input<"/lexus3/gps/nova/current_pose">;

// Global state to store last messages
type Globals = {
  a?: any;
  b?: any;
};

export default function script(
  event: InputEvent,
  globals: Globals,
): Output | undefined {
  if (event.topic === "/localization/pose_estimator/pose") {
    globals.a = event.message;
  } else if (event.topic === "/lexus3/gps/nova/current_pose") {
    globals.b = event.message;
  }

  if (!globals.a || !globals.b) return;

  const a = globals.a;
  const b = globals.b;

  const dx = b.pose.position.x - a.pose.position.x; // pose_diff x
  const dy = b.pose.position.y - a.pose.position.y; // pose_diff y
  const d = Math.hypot(dx, dy);

  return {
    dx,
    dy,
    d,
  };
}
