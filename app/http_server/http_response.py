from typing import Dict, Type, Optional, Union
import sys
import os
import gzip
from app.http_server.http_request import Request


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
        headers: Optional[Dict[str, str]] = None,
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
            except FileNotFoundError:
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
            except IOError:
                return Response(500, None)
        else:
            return Response(404, None)

    def _build_response(self) -> bytes:
        response = b""

        response_body: bytes
        if self.headers.get("Content-Encoding", None) == "gzip":
            encoded_body: bytes = self.body.encode(encoding="utf-8")
            compressed_body = gzip.compress(encoded_body)
            response_body = compressed_body
        else:
            response_body = self.body.encode(encoding="utf-8")

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
        if len(response_body) > 0:
            self.headers["Content-Length"] = str(len(response_body))

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

        return response + b"\r\n" + response_body

    def __str__(self):
        return f"status: {self.status_code}\nheaders:{self.headers}\nbody:{self.body}"
