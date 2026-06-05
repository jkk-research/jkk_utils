#!/usr/bin/env python3
import argparse
from typing import Dict, List

import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message

from rosidl_runtime_py.utilities import get_message

import rosbag2_py


class MultiTopicBagRecorder(Node):
    """
    Record a set of topics (listed in preset_autoware_zed.txt) into an MCAP bag.

    NOTE ABOUT INTRA-PROCESS:
      - This is a Python (rclpy) node. rclpy does NOT expose the
        `use_intra_process_comms` flag that exists in rclcpp::NodeOptions.
      - So this node always uses normal DDS-based transport.
      - If you need true intra-process zero-copy, implement this recorder
        as a C++ component node and set `use_intra_process_comms(true)` there.
    """

    def __init__(self, preset_file: str, bag_uri: str):
        super().__init__('autoware_zed_bag_recorder')

        self.get_logger().info(f"Opening MCAP bag at: {bag_uri}")

        # Set up rosbag2 writer with MCAP storage
        self._writer = rosbag2_py.SequentialWriter()
        storage_options = rosbag2_py.StorageOptions(
            uri=bag_uri,
            storage_id='mcap',  # requires ros-<distro>-rosbag2-storage-mcap
        )
        converter_options = rosbag2_py.ConverterOptions(
            input_serialization_format='cdr',
            output_serialization_format='cdr',
            
        )
        self._writer.open(storage_options, converter_options)

        # Read desired topics from preset file
        topics = self._load_topics(preset_file)
        if not topics:
            self.get_logger().warn(
                f"No topics found in preset file '{preset_file}'. "
                "Nothing will be recorded."
            )

        # Query ROS graph for topic types
        topic_types_map = self._get_topic_type_map()

        self._subs = []

        for topic in topics:
            if topic not in topic_types_map:
                self.get_logger().warn(
                    f"Topic '{topic}' is not currently visible in ROS graph; skipping."
                )
                continue

            # Take first type if multiple are advertised
            type_str = topic_types_map[topic][0]
            try:
                msg_type = get_message(type_str)
            except (AttributeError, ModuleNotFoundError, ValueError) as e:
                self.get_logger().error(
                    f"Could not resolve message type '{type_str}' for topic '{topic}': {e}"
                )
                continue

            # Register topic in bag
            topic_metadata = rosbag2_py.TopicMetadata(
                name=topic,
                type=type_str,
                serialization_format='cdr',
            )
            self._writer.create_topic(topic_metadata)

            # Create subscription that writes incoming messages into the bag
            sub = self.create_subscription(
                msg_type,
                topic,
                self._make_callback(topic),
                10  # QoS depth; adjust if needed
            )
            self._subs.append(sub)

            self.get_logger().info(f"Recording topic '{topic}' [{type_str}]")

        if self._subs:
            self.get_logger().info(
                f"Started recording {len(self._subs)} topics into '{bag_uri}'."
            )
        else:
            self.get_logger().warn(
                "No valid subscriptions created. "
                "Check that the topics in the preset file exist and are being published."
            )

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _load_topics(self, path: str) -> List[str]:
        """Load topic names from a text file.

        Expected format in preset_autoware_zed.txt:
            - one topic name per line
            - empty lines and lines starting with '#' are ignored
            - if a line contains extra tokens (e.g. type), only the first token is used

        Example:
            # Camera topics
            /sensing/camera/traffic_light/image_raw
            /sensing/camera/traffic_light/camera_info

        """
        topics: List[str] = []
        try:
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    tokens = line.split()
                    topics.append(tokens[0])
        except FileNotFoundError:
            self.get_logger().error(
                f"Preset file '{path}' not found. No topics will be recorded."
            )
        return topics

    def _get_topic_type_map(self) -> Dict[str, List[str]]:
        """Return a dict: topic_name -> [type1, type2, ...]."""
        # get_topic_names_and_types() returns List[Tuple[str, List[str]]]
        return dict(self.get_topic_names_and_types())

    def _make_callback(self, topic_name: str):
        """Create a per-topic callback that writes messages into the bag."""

        def callback(msg):
            # Timestamp in nanoseconds from node clock
            timestamp = self.get_clock().now().nanoseconds
            self._writer.write(
                topic_name,
                serialize_message(msg),
                timestamp
            )

        return callback


def main():
    parser = argparse.ArgumentParser(
        description="Record Autoware ZED topics listed in preset_autoware_zed.txt into an MCAP bag."
    )
    parser.add_argument(
        '--preset',
        '-p',
        default='~/ros2_ws/src/mcap_rec/etc/preset_autoware_zed.txt',
        help="Path to preset file listing topics to record (default: preset_autoware_zed.txt)",
    )
    parser.add_argument(
        '--output',
        '-o',
        default='/mnt/bag/autoware_zed_mcap',
        help="Bag URI / folder name for the output MCAP recording (default: autoware_zed_mcap)",
    )
    args = parser.parse_args()

    rclpy.init()
    node = MultiTopicBagRecorder(args.preset, args.output)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Recorder interrupted by user, shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
