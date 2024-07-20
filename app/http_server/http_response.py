from typing import Dict, Type, Optional
import http
import sys
import os
import gzip
from app.http_server.http_request import Request
from app.http_server.constants import HTTPRoutes, HTTPStatusLine


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
        status_code: http.HTTPStatus,
        headers: Optional[Dict[str, str]] = None,
        body: str = "",
        encoding: str = "utf-8",
    ) -> None:
        self.status_code = status_code
        self.headers = headers if headers is not None else {}
        self.body = body
        self.encoding = encoding
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
        if request.path == HTTPRoutes.INDEX.value:
            return Response(http.HTTPStatus.OK, request.headers, request.body)
        elif request.path.startswith(HTTPRoutes.ECHO.value):
            response_headers = {
                "Content-Type": "text/plain",
                "Content-Length": str(len(request.path[6:])),
            }
            encodings = request.headers.get("Accept-Encoding", "")
            encodings_list = encodings.split(", ")

            if "gzip" in encodings_list:
                response_headers["Content-Encoding"] = "gzip"
            return Response(http.HTTPStatus.OK, response_headers, request.path[6:])
        elif request.path == HTTPRoutes.USER_AGENT.value:
            user_agent = request.headers.get("User-Agent", "")
            response_headers = {
                "Content-Type": "text/plain",
                "Content-Length": str(len(user_agent)),
            }
            return Response(http.HTTPStatus.OK, response_headers, user_agent)
        elif request.method == "GET" and request.path.startswith(
            HTTPRoutes.FILES.value
        ):
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
                        http.HTTPStatus.OK,
                        response_headers,
                        file_content,
                    )
            except FileNotFoundError:
                return Response(http.HTTPStatus.NOT_FOUND, None)
        elif request.method == "POST" and request.path.startswith(
            HTTPRoutes.FILES.value
        ):
            directory = sys.argv[2]
            filename = request.path[7:]

            if not os.path.exists(directory):
                os.makedirs(directory)
            filepath = os.path.join(directory, filename)

            try:
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(request.body)
                    return Response(http.HTTPStatus.CREATED, None)
            except IOError:
                return Response(http.HTTPStatus.INTERNAL_SERVER_ERROR, None)
        else:
            return Response(http.HTTPStatus.NOT_FOUND, None)

    def _build_response(self) -> bytes:
        response = b""

        response_body: bytes
        if self.headers.get("Content-Encoding", None) == "gzip":
            encoded_body: bytes = self.body.encode(encoding=self.encoding)
            compressed_body = gzip.compress(encoded_body)
            response_body = compressed_body
        else:
            response_body = self.body.encode(encoding=self.encoding)

        if self.status_code == http.HTTPStatus.OK:
            response += HTTPStatusLine.OK.value
        elif self.status_code == http.HTTPStatus.CREATED:
            response += HTTPStatusLine.CREATED.value
        elif self.status_code == http.HTTPStatus.NOT_FOUND:
            response += HTTPStatusLine.NOT_FOUND.value
        elif self.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR:
            response += HTTPStatusLine.INTERNAL_SERVER_ERROR.value

        if self.headers and "Content-Type" not in self.headers:
            self.headers["Content-Type"] = "text/plain"
        if len(response_body) > 0:
            self.headers["Content-Length"] = str(len(response_body))

        for key, val in self.headers.items():
            if (key == "Content-Type" or key == "Content-Length") and not self.body:
                continue
            elif key == "Content-Encoding" and val != "gzip":
                continue
            elif key == "Host":
                continue
            response += (
                bytes(key, encoding=self.encoding)
                + b": "
                + bytes(val, encoding=self.encoding)
                + b"\r\n"
            )

        return response + b"\r\n" + response_body

    def __str__(self):
        return f"status: {self.status_code}\nheaders:{self.headers}\nbody:{self.body}"
