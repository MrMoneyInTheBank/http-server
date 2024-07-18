import socket


def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, _ = server_socket.accept()

    request = connection.recv(1024).decode().split("\r\n")[0].split(" ")
    endpoint, string = request[1].split("/")
    response = ""

    if endpoint == "echo":
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {string}\r\n"
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    connection.send(response.encode())


if __name__ == "__main__":
    main()
