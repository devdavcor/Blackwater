import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 11000))  # Se conecta a B, no a A
    print("[C] Conectado con B")
    while True:
        msg = input("[C] Mensaje: ")
        s.sendall(msg.encode())
        data = s.recv(1024)
        print(f"[C] Respuesta: {data.decode()}")
