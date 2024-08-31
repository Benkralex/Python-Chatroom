import customtkinter as ctk
import client_networking as cn

def connect():
    cn.update_status("Nicht verbunden", "red")
    ip = ip_box.get()
    port = port_box.get()
    username = username_box.get()
    color = color_box.get()
    if not ip:
        cn.update_status("IP fehlt", "red")
        return
    if not port:
        cn.update_status("Port fehlt", "red")
        return
    if not username:
        cn.update_status("Nutzername fehlt", "red")
        return
    print(f"Verbinden zu {ip}:{port} als {username}")
    if not color:
        color = "#FF0000"
    cn.set_host(ip, int(port), username, color)
    cn.connect_to_server()
    if cn.is_connected():
        cn.update_status(f"Verbunden zu {cn.host}", "green")

def send_message():
    message = msgbox.get()
    if message:
        print(f"Nachricht senden: {message}")
        cn.send_message(message)
        msgbox.delete(0, "end")

def color_change():
    new_color = color_box.get()
    if new_color:
        print(f"Farbe ändern zu {new_color}")
        cn.change_color(new_color)

cn = cn.ClientNetworking()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

root = ctk.CTk()

root.title("Fox-Chat")
root.geometry("1000x700")
root.minsize(1000, 700)

main_frame = ctk.CTkFrame(root, width=1000, height=700)
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

settings_frame = ctk.CTkFrame(main_frame, width=1000, height=80, border_width=1, border_color="black")
settings_frame.pack(padx=5, pady=5, fill="x")

input_height = 40

ip_box = ctk.CTkEntry(settings_frame, width=20, height=input_height, placeholder_text="IP", fg_color="transparent")
ip_box.pack(side="left", padx=5, pady=5, fill="x", expand=True)
ip_box.insert(0, "localhost")

port_box = ctk.CTkEntry(settings_frame, width=20, height=input_height, placeholder_text="Port", fg_color="transparent")
port_box.pack(side="left", padx=5, pady=5, fill="x", expand=True)
port_box.insert(0, "50000")

username_box = ctk.CTkEntry(settings_frame, width=20, height=input_height, placeholder_text="Nutzername", fg_color="transparent")
username_box.pack(side="left", padx=5, pady=5, fill="x", expand=True)

connect_button = ctk.CTkButton(settings_frame, text="Verbinden", width=10, height=input_height, command=connect)
connect_button.pack(side="left", padx=5, pady=5)

color_box = ctk.CTkEntry(settings_frame, width=20, height=input_height, placeholder_text="Farbe (Hex)", fg_color="transparent")
color_box.pack(side="left", padx=5, pady=5, fill="x", expand=True)
color_box.insert(0, "#FF0000")
color_box.bind("<Return>", lambda e: color_change())

status_box = ctk.CTkEntry(settings_frame, width=20, height=input_height, fg_color="transparent", state="disabled")
status_box.pack(side="left", padx=5, pady=5, fill="x", expand=True)

left_sidebar_frame = ctk.CTkFrame(main_frame, width=170, height=590, border_width=1, border_color="black")
left_sidebar_frame.pack_propagate(False)
left_sidebar_frame.pack(side="left", padx=5, pady=5, fill="y")

online_label = ctk.CTkLabel(left_sidebar_frame, text="Online:", fg_color="transparent")
online_label.pack(pady=10)

online_users_frame = ctk.CTkFrame(left_sidebar_frame, width=810, height=420, border_width=1, border_color="black")
online_users_frame.pack(side="top", padx=5, pady=5, fill="both", expand=True)

chat_frame = ctk.CTkFrame(main_frame, width=810, height=500, border_width=1, border_color="black")
chat_frame.pack(side="left", padx=5, pady=5, fill="both", expand=True)

msg_display_frame = ctk.CTkFrame(chat_frame, width=810, height=420, border_width=1, border_color="black")
msg_display_frame.pack(side="top", padx=5, pady=5, fill="both", expand=True)

msgbox_frame = ctk.CTkFrame(chat_frame, width=810, height=(input_height + 10), border_width=1, border_color="black")
msgbox_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)
msgbox = ctk.CTkEntry(msgbox_frame, width=700, height=input_height, placeholder_text="Nachricht eingeben...", fg_color="transparent")
msgbox.pack(side="left", padx=5, pady=5, fill="x", expand=True)
msgbox.bind("<Return>", lambda e: send_message())
send_msg_button = ctk.CTkButton(msgbox_frame, text="Senden", width=10, height=input_height, command=send_message)
send_msg_button.pack(side="right", padx=5, pady=5)

msg_box = msgbox
msg_button = send_msg_button
msg_display = msg_display_frame
online_frame = online_users_frame
status_label = status_box
con_ip = ip_box
con_port = port_box
con_username = username_box
con_color = color_box

cn.set_ctk_elements(msg_box, msg_button, msg_display, online_frame, status_label, con_ip, con_port, con_username, con_color)

root.mainloop()