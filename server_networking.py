import socket
import threading
import datetime

def log(message, log_type='INFO'):
    full_msg = f'[{str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))}] [{str(log_type)}] {str(message)}\n'
    print(full_msg)
    with open('server_log.txt', 'a') as log_file:
        log_file.write(full_msg)

class ServerNetworking:
    def __init__(self, host, port):
        self.client_names = {}
        self.client_colors = {}
        self.clients = []
        self.host = host
        self.port = port
        self.server_socket = None

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        log(f'Server gestartet auf {self.host}:{self.port}')
        while True:
            client_socket, client_address = self.server_socket.accept()
            log(f'Neue Verbindung: {client_address}')
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()

    def handle_client(self, client_socket):
        try:
            # Empfange den Namen und die Farbe des Clients
            name_and_color = client_socket.recv(1024).decode('utf-8').split("|")
            if len(name_and_color) != 2:
                client_socket.close()
                return

            client_name, client_color = name_and_color
            if not client_name or not client_color:
                client_socket.close()
                return

            self.client_names[client_socket] = client_name
            self.client_colors[client_name] = client_color
            self.clients.append(client_socket)

            self.broadcast(f'{client_name} hat den Chat betreten.|{client_color}'.encode('utf-8'))
            self.send_users_list()

            while True:
                try:
                    message = client_socket.recv(1024)
                    if not message:
                        break
                    self.validate_message(message, client_socket)
                except Exception as e:
                    log(f'Fehler beim Empfangen der Nachricht: {str(e)}')
                    break
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            if client_socket in self.client_names:
                client_name = self.client_names.pop(client_socket, None)
                if client_name:
                    color = self.client_colors.pop(client_name, None)
                    self.broadcast(f'{client_name} hat den Chat verlassen.|{color}'.encode('utf-8'))
            client_socket.close()
            self.send_users_list()

    def broadcast(self, message):
        log(f'Broadcasting: {message}')
        for client in self.clients:
            try:
                client.send(b"RECEIVE_MESSAGE|" + message)
            except Exception as e:
                log(f'Fehler beim Senden der Nachricht: {str(e)}')
                self.clients.remove(client)

    def send_users_list(self):
        log('Aktualisiere Benutzerliste...')
        if self.client_names:
            users_list = "USERS_LIST|" + ";".join(
                f"{name}|{self.client_colors.get(name, '#FF0000')}" for name in self.client_names.values())
        else:
            users_list = "USERS_LIST|"
        for client in self.clients:
            try:
                client.send(users_list.encode('utf-8'))
            except Exception as e:
                log(f'Fehler beim Senden der Nachricht: {str(e)}')
                self.clients.remove(client)

    def validate_message(self, message, client_socket):
        client_name = self.client_names[client_socket]
        client_color = self.client_colors[client_name]
        if message.startswith(b"COLOR_CHANGE"):
            _, new_color = message.decode('utf-8').split("|")
            if client_name in self.client_colors:
                self.client_colors[client_name] = new_color
                self.send_users_list()
        elif message.startswith(b"PRIVATE_MESSAGE"):
            _, sender_name, receiver_name, message = message.decode('utf-8').split("|")
            if receiver_name in self.client_names:
                receiver_socket = [client for client, name in self.client_names.items() if name == receiver_name][0]
                receiver_socket.send(f'RECEIVE_PRIVATE_MESSAGE|{sender_name}: {message}|{client_color}'.encode('utf-8'))
        elif message.startswith(b"MESSAGE"):
            _, message = message.decode('utf-8').split("|")
            self.broadcast(f'{client_name}: {message}|{client_color}'.encode('utf-8'))
        elif message.startswith(b"USERS_LIST_REQUEST"):
            self.send_users_list()
        elif message.startswith(b"DISCONNECT"):
            _, client_name = message.decode('utf-8').split("|")
            if client_name in self.client_names:
                client_socket = [client for client, name in self.client_names.items() if name == client_name][0]
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
                self.client_names.pop(client_socket, None)
                self.client_colors.pop(client_name, None)
                client_socket.close()
                self.broadcast(f'{client_name} hat den Chat verlassen.'.encode('utf-8'))
                self.send_users_list()
            else:
                log(f'Client {client_name} nicht gefunden.')
        else:
            log(f'Ungültige Nachricht: {message}')