from typing import Dict, Type


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
