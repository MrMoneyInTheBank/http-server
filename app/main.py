import threading
from app.http_server.my_socket import MySocket
from app.http_server.client import Client


def main() -> None:
    server_socket = MySocket("localhost", 4221)

    while True:
        client_thread = threading.Thread(
            target=Client.handle_client, args=(Client(server_socket),)
        )
        client_thread.start()


if __name__ == "__main__":
    main()
