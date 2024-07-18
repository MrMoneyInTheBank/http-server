from typing import Dict, Type
import threading
import sys
import os
import gzip

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


class Request:
    """
    A class to represent an HTTP request.

    Attributes:
        method (str): HTTP method (e.g., 'GET').
        path (str): The path of the HTTP request.
        headers (Dict[str, str]): HTTP headers.
        body (str): The body of the HTTP request.
    """

    def __init__(
        self, method: str, path: str, headers: Dict[str, str], body: str
    ) -> None:
        """
        Constructs all the necessary attributes for the Request object.

        Args:
            method (str): HTTP method (e.g., 'GET').
            path (str): The path of the HTTP request.
            headers (Dict[str, str]): HTTP headers.
            body (str): The body of the HTTP request.
        """
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body

    @classmethod
    def construct_request(cls: Type["Request"], request: bytes) -> "Request":
        """
        Constructs a Request object from a raw HTTP request in bytes.

        Args:
            request (bytes): The raw HTTP request in bytes.

        Returns:
            Request: An instance of the Request class.

        Raises:
            ValueError: If the request cannot be parsed due to an invalid format.
        """
        lines = request.decode("utf-8").split("\r\n")
        if len(lines) < 3:
            raise ValueError("Request too short to construct Request object")

        request_line = lines[0].split()
        request_verb = request_line[0]

        if not request_verb or request_verb not in {"GET", "POST"}:
            raise ValueError("Unsupported request method")
        if not request_line[1] or request_line[1][0] != "/":
            raise ValueError("Invalid request path")

        method = request_verb
        path = request_line[1]
        headers = {}
        lines = lines[1:]
        idx = 0
        for line in lines:
            if line == "":
                break
            head_line = line.split(":")
            if len(head_line) < 2:
                raise ValueError(f"Invalid header line: {line}")
            headers[head_line[0]] = head_line[1].lstrip()
            idx += 1
        body = lines[idx + 1] if len(lines) > idx + 1 else ""

        return Request(method, path, headers, body)

    def __str__(self):
        return f"path: {self.path}\nmethod: {self.method}\nheaders: {self.headers}\nbody: {self.body}"


class Response:
    """
    A class to represent an HTTP response.

    Attributes:
        status_code (int): HTTP method (e.g., 'GET').
        headers (Dict[str, str]): HTTP headers.
        body (str): The body of the HTTP response.
    """

    def __init__(
        self,
        status_code: int,
        headers: None | Dict[str, str] = None,
        body: str = "",
    ) -> None:
        self.status_code = status_code
        self.headers = headers if headers is not None else {}
        self.body = body
        self.response = self._build_response()

    @classmethod
    def construct_response(cls: Type["Response"], request: Request) -> "Response":
        """
        Constructs a Response object.

        Args:
            request (Request): The request object.

        Returns:
            Request: An instance of the Response class.

        Raises:
            ValueError: If the request cannot be parsed due to an invalid format.
        """
        if request.path == "/":
            return Response(200, request.headers, request.body)
        elif request.path.startswith("/echo/"):
            response_headers = {
                "Content-Type": "text/plain",
                "Content-Length": str(len(request.path[6:])),
            }
            encodings = request.headers.get("Accept-Encoding", "")
            encodings_list = encodings.split(", ")

            if "gzip" in encodings_list:
                response_headers["Content-Encoding"] = "gzip"

            return Response(200, response_headers, request.path[6:])
        elif request.path == "/user-agent":
            user_agent = request.headers.get("User-Agent") or ""
            response_headers = {
                "Content-Type": "text/plain",
                "Content-Length": str(len(user_agent)),
            }
            return Response(200, response_headers, user_agent)
        elif request.method == "GET" and request.path.startswith("/files/"):
            directory = sys.argv[2]
            filename = request.path[7:]

            try:
                with open(f"/{directory}/{filename}", "r", encoding="utf-8") as file:
                    file_content = file.read()
                    response_headers = {
                        "Content-Type": "application/octet-stream",
                        "Content-Length": str(len(file_content)),
                    }
                    return Response(
                        200,
                        response_headers,
                        file_content,
                    )
            except:
                return Response(404, None)
        elif request.method == "POST" and request.path.startswith("/files/"):
            directory = sys.argv[2]
            filename = request.path[7:]

            if not os.path.exists(directory):
                os.makedirs(directory)
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(request.body)
                    return Response(201, None)
            except:
                return Response(500, None)
        else:
            return Response(404, None)

    def _build_response(self) -> bytes:
        response = b""
        body = self.body

        if self.status_code == 200:
            response += b"HTTP/1.1 200 OK\r\n"
        elif self.status_code == 201:
            response += b"HTTP/1.1 201 Created\r\n\r\n"
        elif self.status_code == 404:
            response += b"HTTP/1.1 404 Not Found\r\n"
        elif self.status_code == 500:
            response += b"HTTP/1.1 500 Internal Server Error"

        if self.headers and "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "text/plain"
        if self.body != "" and "Content-Length" not in self.headers:
            self.headers["Content-Length"] = str(len(self.body))

        for key, val in self.headers.items():
            if (key == "Content-Type" or key == "Content-Length") and len(
                self.body
            ) == 0:
                continue
            elif key == "Content-Encoding":
                if (
                    "Accept-Encoding" in self.headers
                    and self.headers["Accept-Encoding"] != "gzip"
                ):
                    continue
            elif key == "Host":
                continue
            response += (
                bytes(key, encoding="utf-8")
                + b": "
                + bytes(val, encoding="utf-8")
                + b"\r\n"
            )

        if (
            "Accept-Encoding" in self.headers
            and self.headers["Accept-Encoding"] != "gzip"
        ):
            encoded_body = body.encode(encoding="utf-8")
            compressed_body = gzip.compress(encoded_body)
            response += b"\r\n" + compressed_body
        else:
            response += b"\r\n" + bytes(body, encoding="utf-8")
        return response

    def __str__(self):
        return f"status: {self.status_code}\nheaders:{self.headers}\nbody:{self.body}"


class Client:
    """
    A class to represent a client connected to the TCP socket.

    Attributes:
        socket (socket) : TCP server socket.
        connection (socket) : client socket.
        address (_RetAddress) : client ip address.
    """

    def __init__(self, socket: MySocket) -> None:
        self.socket = socket
        self.connection, self.address = self.socket.server_socket.accept()

    def listen(self) -> Request:
        incoming_request = self.connection.recv(1024)
        parsed_request = Request.construct_request(incoming_request)
        return parsed_request

    def send_response(self, response: Response) -> None:
        self.connection.send(response.response)


def handle_client(client: Client) -> None:
    request = client.listen()
    response = Response.construct_response(request)
    client.send_response(response)


def main():
    server_socket = MySocket("localhost", 4221)

    while True:
        client_thread = threading.Thread(
            target=handle_client, args=(Client(server_socket),)
        )
        client_thread.start()


if __name__ == "__main__":
    main()
