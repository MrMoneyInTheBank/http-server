import threading
from my_socket import MySocket
from http_response import Response
from client import Client


def handle_client(client: Client) -> None:
    request = client.listen()
    response = Response.construct_response(request)
    client.send_response(response)


def main() -> None:
    server_socket = MySocket("localhost", 4221)

    while True:
        client_thread = threading.Thread(
            target=handle_client, args=(Client(server_socket),)
        )
        client_thread.start()


if __name__ == "__main__":
    main()
