"""
Entry point: ``ros2 run workspace_health workspace_health [--ws PATH] [--stale-hours H]``.

The workspace can also be given as ROS parameter ``ws_path`` (and ``stale_hours``):
``ros2 run workspace_health workspace_health --ros-args -p ws_path:=~/other_ws``.
Priority: command line argument > ROS parameter > default (``~/ros2_ws``).
"""

import argparse
import sys

from .git_status import DEFAULT_STALE_HOURS

DEFAULT_WS = '~/ros2_ws'


def strip_ros_args(argv):
    """Remove ``--ros-args ... [--]`` sections (works without rclpy)."""
    result = []
    in_ros = False
    for arg in argv:
        if arg == '--ros-args':
            in_ros = True
        elif in_ros and arg == '--':
            in_ros = False
        elif not in_ros:
            result.append(arg)
    return result


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog='workspace_health',
        description='Overview of the GitHub repositories cloned into a ROS 2 workspace.')
    parser.add_argument('--ws',
                        help=f'workspace path (default: ROS param ws_path or {DEFAULT_WS})')
    parser.add_argument('--stale-hours', type=float,
                        help=f'mark repos Stale if not fetched for this many hours '
                             f'(default: ROS param stale_hours or {DEFAULT_STALE_HOURS:g})')
    return parser.parse_args(strip_ros_args(argv))


def read_ros_params(argv):
    """Read ``ws_path`` / ``stale_hours`` ROS parameters; empty dict if ROS is unavailable."""
    if '--ros-args' not in argv:
        return {}
    try:
        import rclpy
        from rcl_interfaces.msg import ParameterDescriptor
    except ImportError:
        return {}
    params = {}
    rclpy.init(args=argv)
    try:
        node = rclpy.create_node('workspace_health')
        dynamic = ParameterDescriptor(dynamic_typing=True)
        node.declare_parameter('ws_path', '')
        node.declare_parameter('stale_hours', DEFAULT_STALE_HOURS, dynamic)
        ws = node.get_parameter('ws_path').value
        if ws:
            params['ws_path'] = str(ws)
        params['stale_hours'] = float(node.get_parameter('stale_hours').value)
        node.destroy_node()
    finally:
        rclpy.shutdown()
    return params


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv)
    params = read_ros_params(argv)
    ws = args.ws or params.get('ws_path') or DEFAULT_WS
    stale_hours = args.stale_hours or params.get('stale_hours') or DEFAULT_STALE_HOURS
    try:
        from .gui import run
    except ImportError as exc:
        print(f'workspace_health: cannot start GUI ({exc}).\n'
              'Install CustomTkinter with:  pip install customtkinter', file=sys.stderr)
        return 1
    run(ws, stale_hours)
    return 0


if __name__ == '__main__':
    sys.exit(main())
