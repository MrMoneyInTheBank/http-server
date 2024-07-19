import threading
from http_server.my_socket import MySocket
from http_server.client import Client
from http_server.http_response import Response


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
