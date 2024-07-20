import threading
import signal
import os
from typing import Any
from app.http_server.my_socket import MySocket
from app.http_server.client import Client
from app.utils.logging import setup_logger

logger = setup_logger(os.path.basename(__file__))


class MyServer:
    """
    A simple HTTP server that handles client connections in separate threads.

    This server can be gracefully shut down using SIGINT or SIGTERM signals.

    Attributes:
        host (str): The hostname or IP address the server binds to.
        port (int): The port number the server listens on.
        server_socket (MySocket): The socket object used for accepting connections.
        running (bool): Flag indicating whether the server is running.
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = MySocket(host, port)
        self.running = False

    def start(self) -> None:
        """
        Start the server and begin accepting client connections.

        This method sets up signal handlers for graceful shutdown and
        enters a loop to accept and handle client connections until
        the server is stopped.
        """
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        self.running = True
        while self.running:
            try:
                client_thread = threading.Thread(
                    target=Client.handle_client,
                    args=(Client(self.server_socket),),
                    daemon=True,
                )
                client_thread.start()
            except Exception as e:
                logger.error(f"Error: {e}")
                break
        self.server_socket.server_socket.close()
        logger.info("Server shut down suhccessfully")

    def shutdown(self, *_: Any) -> None:
        """
        Gracefully shut down the server.

        This method is designed to be used as a signal handler for
        SIGINT and SIGTERM signals. It ignores any arguments passed
        by the signal mechanism.

        Args:
            *_ (Any): Captures any arguments passed by the signal handler (ignored).
        """
        logger.info("Shutting down gracefully...")
        self.running = False
