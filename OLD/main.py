import socket

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 12345))
    s.send("Hello, world!")
    s.close()