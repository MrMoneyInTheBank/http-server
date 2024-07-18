import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, _ = server_socket.accept()

    request = connection.recv(1024).decode()
    print(request)
    response = "HTTP/1.1 200 OK\r\n\r\n"
    connection.send(response.encode())


if __name__ == "__main__":
    main()
