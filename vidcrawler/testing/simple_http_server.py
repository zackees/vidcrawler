"""
Simple Http Server useful for testing
"""

# pylint: disable=line-too-long,missing-function-docstring,missing-class-docstring,super-with-arguments

import atexit
import http.server
import socketserver
import threading
from contextlib import contextmanager
from http import HTTPStatus
from typing import Any, Callable, Generator, List, Optional

import requests

StringFunctor = Callable[[], str]

_TIMEOUT = 10


def make_handler_class(response_text_fcn: StringFunctor) -> Any:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(HTTPStatus.OK)
            self.end_headers()
            data = response_text_fcn().encode("utf-8")
            self.wfile.write(data)

    return Handler


class ServerThread(threading.Thread):
    def __init__(self, tcp_server: socketserver.TCPServer):
        threading.Thread.__init__(self)
        self.tcp_server: socketserver.TCPServer = tcp_server
        _alive_servers.append(self)

    def run(self):
        self.tcp_server.serve_forever(poll_interval=0.001)

    def join(self, timeout: Optional[float] = 2) -> None:
        _alive_servers.remove(self)
        self.tcp_server.shutdown()
        self.tcp_server.server_close()
        super(ServerThread, self).join(timeout=timeout)


_alive_servers: List[ServerThread] = []


@atexit.register
def _exit_dead_servers():
    """Just incase the unit tests misbehave, this will clean up threads."""
    for server in _alive_servers:
        server.join()


@contextmanager
def simple_response_server_thread(
    port: int,
    response_text_fcn: StringFunctor = lambda: "Hello World!",
) -> Generator[ServerThread, None, None]:
    """
    Example:
        with simple_response_server_thread(port=53925, response_text_fcn=lambda: "this should match!!!!"):
            resp = requests.get("http://localhost:53925")
            resp.raise_for_status()
            assert resp.text == "this should match!!!!"
    """
    handler_class = make_handler_class(response_text_fcn=response_text_fcn)
    tcp_server: socketserver.TCPServer = socketserver.TCPServer(
        ("", port), handler_class
    )
    tcp_server.allow_reuse_address = True

    try:
        server_thread = ServerThread(tcp_server)
        server_thread.start()
        yield server_thread
    finally:
        server_thread.join()


def unit_test() -> None:
    with simple_response_server_thread(
        port=53925, response_text_fcn=lambda: "this should match!!!!"
    ):
        resp = requests.get("http://localhost:53925", timeout=_TIMEOUT)
        resp.raise_for_status()
        assert resp.text == "this should match!!!!"


if __name__ == "__main__":
    unit_test()
