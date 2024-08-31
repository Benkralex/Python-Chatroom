####################################
#
#      Outdated Version
#
# New version: client_new_layout.py
#
####################################

import socket
import threading
import customtkinter as ctk
import random
from tkinter.colorchooser import askcolor
from tkinter import simpledialog, messagebox

def generate_random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.online_users = {}

        # Default-Werte
        self.username = ""
        self.message_color = generate_random_color()
        self.client_socket = None
        self.host = 'localhost'
        self.port = 50000

        # Hauptlayout
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Obere Leiste für Einstellungen und Status
        self.settings_frame = ctk.CTkFrame(self.main_frame)
        self.settings_frame.pack(side='top', fill='x', pady=10)

        # Chat-Title
        self.chat_title_label = ctk.CTkLabel(self.settings_frame, text="Chat-Title")
        self.chat_title_label.pack(side='left', padx=5)

        # IP-Eingabefeld
        self.host_label = ctk.CTkLabel(self.settings_frame, text="IP:Port")
        self.host_label.pack(side='left', padx=5)
        self.host_entry = ctk.CTkEntry(self.settings_frame, width=150)
        self.host_entry.pack(side='left', padx=5)
        self.host_entry.insert(0, self.host)

        # Port-Eingabefeld
        self.port_entry = ctk.CTkEntry(self.settings_frame, width=80)
        self.port_entry.pack(side='left', padx=5)
        self.port_entry.insert(0, str(self.port))

        # Username-Eingabefeld
        self.username_label = ctk.CTkLabel(self.settings_frame, text="Nutzername")
        self.username_label.pack(side='left', padx=5)
        self.username_entry = ctk.CTkEntry(self.settings_frame, width=150)
        self.username_entry.pack(side='left', padx=5)
        self.username_entry.insert(0, self.username)

        # Farbe-Eingabefeld
        self.color_label = ctk.CTkLabel(self.settings_frame, text="Farbe")
        self.color_label.pack(side='left', padx=5)
        self.color_button = ctk.CTkButton(self.settings_frame, text="Farbe wählen", command=self.choose_color)
        self.color_button.pack(side='left', padx=5)

        # Speichern-Button
        self.save_button = ctk.CTkButton(self.settings_frame, text="Speichern", command=self.save_settings)
        self.save_button.pack(side='left', padx=5)

        # Status-Anzeige
        self.status_label = ctk.CTkLabel(self.settings_frame, text="Status", text_color="red")
        self.status_label.pack(side='left', padx=5)

        # Layout für Chat und Online-Liste
        self.chat_frame = ctk.CTkFrame(self.main_frame)
        self.chat_frame.pack(side='left', fill='both', expand=True)

        self.online_frame = ctk.CTkFrame(self.main_frame)
        self.online_frame.pack(side='right', fill='y', padx=10)

        # Nachrichtenanzeige
        self.text_area = ctk.CTkTextbox(self.chat_frame, height=20, width=50)
        self.text_area.pack(padx=10, pady=10, fill='both', expand=True)
        self.text_area.configure(state='disabled')

        # Online-Liste
        self.users_label = ctk.CTkLabel(self.online_frame, text="Online:")
        self.users_label.pack(pady=10)

        self.users_listbox = ctk.CTkTextbox(self.online_frame, height=20, width=20)
        self.users_listbox.pack(padx=10, pady=10, fill='both', expand=True)
        self.users_listbox.configure(state='disabled')

        # Eingabefeld und Senden-Button
        self.entry_frame = ctk.CTkFrame(self.root)
        self.entry_frame.pack(side='bottom', padx=10, pady=10, fill='x')

        self.message_entry = ctk.CTkEntry(self.entry_frame)
        self.message_entry.pack(side='left', padx=10, pady=10, fill='x', expand=True)
        self.message_entry.bind('<Return>', self.send_message)

        self.send_button = ctk.CTkButton(self.entry_frame, text="Senden", command=self.send_message)
        self.send_button.pack(side='left', padx=10, pady=10)

    def choose_color(self):
        color_code = askcolor(title="Wähle eine Farbe")[1]
        if color_code:
            self.message_color = color_code
            self.color_button.config(bg=color_code)  # Optional: Update the button color

    def save_settings(self):
        self.host = self.host_entry.get()
        self.port = int(self.port_entry.get())
        self.username = self.username_entry.get()

        if not self.username:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Benutzernamen ein.")
            return

        if self.client_socket:
            self.client_socket.close()

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.client_socket.send(f"{self.username}|{self.message_color}".encode('utf-8'))

            # Clear the chat area
            self.text_area.configure(state='normal')
            self.text_area.delete("1.0", "end")
            self.text_area.configure(state='disabled')

            # Update status
            self.status_label.config(text="Verbunden", text_color="green")

            # Start receiving messages
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.start()

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Verbinden: {str(e)}")
            self.status_label.config(text="Nicht verbunden", text_color="red")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("USERS_LIST:"):
                    self.update_users_list(message.replace("USERS_LIST:", ""))
                else:
                    self.display_message(message)
            except Exception as e:
                self.display_message(f'Fehler beim Empfang der Nachricht: {str(e)}')
                self.client_socket.close()
                self.status_label.config(text="Nicht verbunden", text_color="red")
                break

    def send_message(self, event=None):
        if self.client_socket:
            message = self.message_entry.get()
            if message:
                full_message = f"{self.username}: {message}|{self.message_color}"
                self.client_socket.send(full_message.encode('utf-8'))
                self.message_entry.delete(0, 'end')

    def display_message(self, message):
        try:
            if "|" in message:
                user_message, color = message.rsplit("|", 1)
                self.text_area.configure(state='normal')
                self.text_area.insert('end', f"{user_message}\n", ("color",))
                self.text_area.tag_config("color", foreground=color)
                self.text_area.configure(state='disabled')
                self.text_area.yview('end')
            else:
                self.text_area.configure(state='normal')
                self.text_area.insert('end', f"{message}\n")
                self.text_area.configure(state='disabled')
                self.text_area.yview('end')
        except Exception as e:
            self.text_area.configure(state='normal')
            self.text_area.insert('end', f"Fehler beim Anzeigen der Nachricht: {str(e)}\n")
            self.text_area.configure(state='disabled')
            self.text_area.yview('end')

    def update_users_list(self, users):
        self.users_listbox.configure(state='normal')
        self.users_listbox.delete("1.0", "end")
        self.online_users = {}
        for user_info in users.split(";"):
            username, color = user_info.split("|")
            self.online_users[username] = color
            self.users_listbox.insert('end', f"{username}\n")
            self.users_listbox.tag_config(username, foreground=color)
        self.users_listbox.configure(state='disabled')

def start_gui_client():
    root = ctk.CTk()
    app = ChatClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui_client()
