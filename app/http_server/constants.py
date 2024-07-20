from enum import Enum


class HTTPRoutes(Enum):
    """
    Enumeration of HTTP routes supported by the server.

    Attributes:
        INDEX: The root path ("/").
        ECHO: The path for echo functionality ("/echo/").
        USER_AGENT: The path for user agent information ("/user-agent").
        FILES: The path for file operations ("/files/").
    """

    INDEX = "/"
    ECHO = "/echo/"
    USER_AGENT = "/user-agent"
    FILES = "/files/"


class HTTPStatusLine(Enum):
    """
    Enumeration of HTTP status lines used in server responses.

    Each attribute represents a specific HTTP status, including the protocol version,
    status code, and reason phrase, formatted as bytes for direct inclusion in HTTP responses.

    Attributes:
        OK: 200 OK status line.
        CREATED: 201 Created status line, including an extra CRLF for an empty header section.
        NOT_FOUND: 404 Not Found status line.
        INTERNAL_SERVER_ERROR: 500 Internal Server Error status line.
    """

    OK = b"HTTP/1.1 200 OK\r\n"
    CREATED = b"HTTP/1.1 201 Created\r\n\r\n"
    NOT_FOUND = b"HTTP/1.1 404 Not Found\r\n"
    INTERNAL_SERVER_ERROR = b"HTTP/1.1 500 Internal Server Error\r\n"
