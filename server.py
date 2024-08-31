import socket
import threading

HOST = 'localhost'
PORT = 50000

clients = []
client_names = {}
client_colors = {}

def broadcast(message):
    print(f'Nachricht senden: {message.decode("utf-8")}')
    for client in clients:
        try:
            client.send(message)
        except Exception as e:
            print(f'Fehler beim Senden der Nachricht: {str(e)}')
            clients.remove(client)

def send_users_list():
    print('Aktualisiere Benutzerliste...')
    print(client_names)
    if client_names:
        users_list = "USERS_LIST:" + ";".join(
            f"{name}|{client_colors.get(name, '#FF0000')}" for name in client_names.values())
    else:
        users_list = "USERS_LIST:"
    broadcast(users_list.encode('utf-8'))

def handle_client(client_socket):
    try:
        # Empfange den Namen und die Farbe des Clients
        name_and_color = client_socket.recv(1024).decode('utf-8').split("|")
        print(f'Name und Farbe: {name_and_color}')
        if len(name_and_color) != 2:
            client_socket.close()
            return

        client_name, client_color = name_and_color
        if not client_name or not client_color:
            client_socket.close()
            return

        client_names[client_socket] = client_name
        client_colors[client_name] = client_color
        clients.append(client_socket)

        broadcast(f'{client_name} hat den Chat betreten.'.encode('utf-8'))
        send_users_list()

        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break

                if message.startswith(b"COLOR_CHANGE:"):
                    _, client_name, new_color = message.decode('utf-8').split("|")
                    if client_name in client_colors:
                        client_colors[client_name] = new_color
                        send_users_list()
                else:
                    broadcast(message)
            except Exception as e:
                print(f'Fehler beim Empfangen der Nachricht: {str(e)}')
                break
    finally:
        if client_socket in clients:
            clients.remove(client_socket)
        if client_socket in client_names:
            client_name = client_names.pop(client_socket, None)
            if client_name:
                client_colors.pop(client_name, None)
                broadcast(f'{client_name} hat den Chat verlassen.'.encode('utf-8'))
        client_socket.close()
        send_users_list()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f'Server gestartet. Wartet auf Verbindungen bei {HOST}:{PORT}...')

    while True:
        client_socket, client_address = server.accept()
        print(f'Neue Verbindung: {client_address}')

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    start_server()