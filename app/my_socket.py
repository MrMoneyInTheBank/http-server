import socket


class MySocket:
    """
    A class to represent a TCP socket bound to a host and port

    Attributes:
        host (str): The host address of the socket
        port (int): The port of the socket
        server_socket (Union[socket, socket.SocketType]): A socket bound to a host and port
    """

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.create_server((host, port), reuse_port=True)
