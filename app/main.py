import socket


def main():
    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, _ = server_socket.accept()  # wait for client

    response = "HTTP/1.1 200 OK\r\n\r\n"
    connection.send(response.encode())


if __name__ == "__main__":
    main()
