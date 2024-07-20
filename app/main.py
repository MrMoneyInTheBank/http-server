from app.http_server.my_server import MyServer


def main() -> None:
    server = MyServer("localhost", 4221)
    server.start()


if __name__ == "__main__":
    main()
