import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 12345


def handle_client(conn: socket.socket) -> None:
    conn_is_alive = True

    def get_message() -> None:
        nonlocal conn_is_alive
        while conn_is_alive:
            data = conn.recv(1024)
            if not data:
                print("Connection closed by the server")
                conn_is_alive = False
            print(data.decode())

    def send_message() -> None:
        nonlocal conn_is_alive

        user_name = input('What is your name?\n')
        user_name = '@' + user_name.encode("cp1251").decode("cp1251")  # возникли проблемы с utf-8 при
        output_message = user_name.encode()                            # использовании русской раскладки
        conn.sendall(output_message)                                   # и использовании backspace
        print('To exit from chat write ":q" and press "enter"')

        while conn_is_alive:

            user_message = input()
            user_message = user_message.encode("cp1251").decode("cp1251")

            if user_message == ':q':
                conn.sendall(user_message.encode())
                break

            output_message = f'{user_name}: {user_message}'.encode()
            conn.sendall(output_message)

    get = threading.Thread(target=get_message)
    get.start()
    send = threading.Thread(target=send_message)
    send.start()

    get.join()
    send.join()
    conn.close()
    sys.exit()


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        handle_client(s)
