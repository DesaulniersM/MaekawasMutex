"""This module will contain multicasting utilities"""
from collections.abc import Callable
from socketserver import _AfInetAddress, BaseRequestHandler, BaseServer, ThreadingTCPServer, StreamRequestHandler
import socket
from typing import *


# NOTE: RH - We can probably create an abstract request handler that expects messages to be prepended with a fixed length MODE field like "VECTORS" or "MAEKAWA" instead
class VectorRequestHandler(StreamRequestHandler):
    """Handles TCP requests using Vector Clock message structure.
    """
    def __init__(self, request: socket.socket | _AfInetAddress[bytes | socket.socket], client_address: socket.Any, server: BaseServer) -> None:
        super().__init__(request, client_address, server)

class MaekawaRequestHandler(StreamRequestHandler):
    """Handles TCP requests using Maekawa message structure.
    """
    def __init__(self, request: socket.socket | _AfInetAddress[bytes | socket.socket], client_address: socket.Any, server: BaseServer) -> None:
        super().__init__(request, client_address, server)

class MulticastingP2PNode(ThreadingTCPServer):
    """Handles comms loop for sending and receiving requests.
        - Send multicast messages
        - Receive multicast messages
        - Parse/Handle messages per whatever mode is specified
        - Manage aquired distributed lock
        - Trigger execution of work in critical section (via injected function maybe?)
    """
    def __init__(self, server_address: tuple[str | bytes | bytearray, int], RequestHandlerClass: Callable[[Any, Any, Self], BaseRequestHandler], bind_and_activate: bool = True) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)