// this foxglove typescript converts a ROS2 message timestamp to 
// an absolute time string relative to a fixed offset with a format hh:mm:ss

// --- Input / Output setup ---
export const inputs = ["/zed/zed_node/left/camera_info"];
export const output = "/abs_time";

// --- Output message type ---
type Output = {
  sec: number;
  nsec: number;
  abs_time: string; // formatted relative time, e.g. "00:00:05"
};

// --- Reference offset (baseline in seconds) ---
const OFFSET_SEC = 1761141895;

// --- Helper: format seconds to hh:mm:ss ---
function formatTime(seconds: number): string {
  if (seconds < 0) seconds = 0; // no negative time
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  return `${hrs.toString().padStart(2, "0")}:${mins
    .toString()
    .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

// --- Helper: extract timestamp and convert to relative time ---
function extractTimestamp(msg: any): Output {
  const stamp = msg?.header?.stamp;
  const sec = typeof stamp?.sec === "number" ? stamp.sec : 0;
  const nsec = typeof stamp?.nsec === "number" ? stamp.nsec : 0;

  // relative time in seconds
  const relSec = sec + nsec * 1e-9 - OFFSET_SEC;

  return {
    sec,
    nsec,
    abs_time: formatTime(relSec),
  };
}

// --- Main script ---
export default function script(event: { topic: string; message: any }): Output | undefined {
  if (event.topic === "/zed/zed_node/left/camera_info") {
    return extractTimestamp(event.message);
  }
  return;
}
