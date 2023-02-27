import socket
import threading
from datetime import datetime
import atexit
import json
import os
import signal

HOST = "127.0.0.1"
PORT = 12345

chat_log = {
    'server_start_time': '',
    'clients': {},
    'log': [],
    'server_off_time': ''
}

client_connections = []


def send_messages(connection: socket.socket, data, to_sender=False) -> None:
    global client_connections

    for client_conn in client_connections:
        if not to_sender:
            if client_conn == connection:
                continue
        try:
            client_conn.sendall(data)
        except socket.error:
            client_connections.remove(client_conn)


def new_client(connection: socket.socket) -> None:
    global client_connections
    global chat_log

    with connection:

        client_connections.append(connection)
        new_user = connection.recv(1024).decode()
        chat_log['clients'][new_user] = str(connection)
        greetings = f'{new_user} has entered in the chat. Hello, {new_user}!'
        chat_log['log'].append(str(greetings))
        print(greetings)
        send_messages(connection, greetings.encode(), to_sender=True)

        while True:
            data = connection.recv(1024)

            if data.decode() == ':q':
                output_message = f'{new_user} has left the chat'
                send_messages(connection, output_message.encode())
                chat_log['log'].append(str(output_message))
                print(output_message)
                client_connections.remove(connection)
                connection.sendall('You have left the chat'.encode())
                connection.sendall(b'')
                connection.close()
                break

            print(data.decode())
            chat_log['log'].append(str(data.decode()))
            send_messages(connection, data)


def end_script() -> None:
    global chat_log
    FILENAME = 'server_log.json'

    chat_log['server_off_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if os.path.isfile(FILENAME):
        with open(FILENAME, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    data[f'Server lof from {chat_log["server_start_time"]} till {chat_log["server_off_time"]}'] = chat_log

    with open(FILENAME, 'w') as f:
        json.dump(data, f, indent=4)


def signal_handler() -> None:
    end_script()


def server_run() -> None:
    global chat_log

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.bind((HOST, PORT))
        s.listen()

        chat_log['server_start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        while True:
            conn, _ = s.accept()
            if conn not in client_connections:
                thread = threading.Thread(target=new_client, args=(conn,))
                thread.start()


# регистрируем функцию для запуска скрипта при завершении работы программы, в т.ч. при закрытии терминала
atexit.register(end_script)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGHUP, signal_handler)

if __name__ == "__main__":
    server_run()
