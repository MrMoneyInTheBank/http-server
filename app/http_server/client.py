from app.http_server.my_socket import MySocket
from app.http_server.http_request import Request
from app.http_server.http_response import Response


class Client:
    """
    A class to represent a client connected to the TCP socket.

    Attributes:
        socket (socket) : TCP server socket.
        connection (socket) : client socket.
        address (_RetAddress) : client ip address.
    """

    def __init__(self, my_socket: MySocket) -> None:
        self.socket = my_socket
        self.connection, self.address = self.socket.server_socket.accept()

    def listen(self) -> Request:
        incoming_request = self.connection.recv(1024)
        parsed_request = Request.construct_request(incoming_request)
        return parsed_request

    def send_response(self, response: Response) -> None:
        self.connection.send(response.response)

    @staticmethod
    def handle_client(client: "Client") -> None:
        request = client.listen()
        response = Response.construct_response(request)
        client.send_response(response)
