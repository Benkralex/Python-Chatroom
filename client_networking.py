import socket
import threading
import customtkinter as ctk

class ClientNetworking:
    def __init__(self):
        self.con_ip = None
        self.con_port = None
        self.con_username = None
        self.con_color = None
        self.status_label = None
        self.online_frame = None
        self.msg_display = None
        self.msg_button = None
        self.msg_box = None
        self.host = None
        self.port = None
        self.username = None
        self.message_color = None
        self.client_socket = None
        self.user_list = []
        self.timeout = 0.1

    def set_host(self, host, port, username, color):
        self.host = host
        self.port = port
        self.username = username
        self.message_color = color

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(f"{self.username}|{self.message_color}".encode('utf-8'))
        threading.Thread(target=self.receive_message).start()
        self.update_status("Verbunden", "green")
        return self.client_socket

    def send_message(self, message):
        if self.client_socket:
            full_message = f"{self.username}: {message}|{self.message_color}"
            self.client_socket.send(full_message.encode('utf-8'))

    def receive_message(self):
        while self.client_socket:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    continue
                print(f"Empfangene Nachricht: {message}")  # Debugging line
                if message.startswith("USERS_LIST:"):
                    self.update_users_list(message.replace("USERS_LIST:", ""))
                else:
                    self.display_message(message)
            except Exception as e:
                print(f"Fehler beim Empfangen der Nachricht: {str(e)}")
                self.close_connection()
                break

    def close_connection(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.update_status("Nicht verbunden", "red")

    def is_connected(self):
        return self.client_socket is not None

    def change_color(self, new_color):
        if self.client_socket:
            self.client_socket.send(f"COLOR_CHANGE:{self.username}|{new_color}".encode('utf-8'))

    def set_ctk_elements(self, msg_box, msg_button, msg_display, online_frame, status_label, con_ip, con_port, con_username, con_color):
        self.msg_box = msg_box
        self.msg_button = msg_button
        self.msg_display = msg_display
        self.online_frame = online_frame
        self.status_label = status_label
        self.con_ip = con_ip
        self.con_port = con_port
        self.con_username = con_username
        self.con_color = con_color
        self.update_status("Nicht verbunden", "red")

    def update_status(self, status, color):
        self.status_label.configure(state="normal")
        self.status_label.delete(0, "end")
        self.status_label.insert(0, status)
        self.status_label.configure(text_color=color)
        self.status_label.configure(state="disabled")

    def display_message(self, message):
        try:
            text, color = message.split("|")
            msg_label = ctk.CTkLabel(self.msg_display, text=text, text_color=color)
            msg_label.pack(pady=5)
        except ValueError:
            print(f"Fehlerhafte Nachricht: {message}")

    def update_users_list(self, users):
        for widget in self.online_frame.winfo_children():
            widget.destroy()
        for user_info in users.split(";"):
            try:
                username, color = user_info.split("|")
                user_label = ctk.CTkLabel(self.online_frame, text=username, text_color=color)
                user_label.pack(pady=5)
            except ValueError:
                print(f"Fehlerhafte Benutzerinfo: {user_info}")