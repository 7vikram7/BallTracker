"""Live multi-phone capture: phones stream frames to a server on the Mac.

* Phones open a web page served by the Mac (no app install) and send JPEG
  frames with capture timestamps over a WebSocket.
* The server keeps a clock offset per phone (``clocksync``), runs the ball
  pipeline for each camera in its own process (``worker``), fuses bounces seen
  by several cameras (``fusion``) and announces OUT / FAULT on the dashboard.
"""
