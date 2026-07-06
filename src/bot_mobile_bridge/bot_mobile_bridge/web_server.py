"""Serves the touch-joystick web UI to phones on the robot's network.

A plain ThreadingHTTPServer is enough here: the UI is a single static page
and all realtime traffic goes over the rosbridge websocket, not this server.
Wrapped in a ROS node so it shows up in the graph, obeys ROS logging, and can
be parameterised from launch files.
"""
import http.server
import os
import threading
from functools import partial

import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Static file handler that routes access logs to ROS debug logging."""

    def __init__(self, *args, logger=None, **kwargs):
        self._logger = logger
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):  # noqa: A002 - stdlib signature
        if self._logger:
            self._logger.debug('http: ' + format % args)


class WebServerNode(Node):

    def __init__(self):
        super().__init__('mobile_web_server')
        self.declare_parameter('port', 8080)
        self.declare_parameter('web_root', '')

        port = self.get_parameter('port').value
        web_root = self.get_parameter('web_root').value or os.path.join(
            get_package_share_directory('bot_mobile_bridge'), 'web')

        handler = partial(QuietHandler, directory=web_root,
                          logger=self.get_logger())
        self._server = http.server.ThreadingHTTPServer(('0.0.0.0', port), handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self.get_logger().info(
            f'Serving mobile UI from {web_root} on http://0.0.0.0:{port}')

    def destroy_node(self):
        self._server.shutdown()
        self._server.server_close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WebServerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
