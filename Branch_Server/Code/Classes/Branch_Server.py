import socket
import threading

class Branch_Server:
    def __init__(self, server_a_ip, server_a_port, listen_port=11005):
        self.server_a_ip = server_a_ip
        self.server_a_port = server_a_port
        self.listen_port = listen_port
        self.conn_a = None
        self.stop_event = threading.Event()

    def connect_to_server_a(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_a_ip, self.server_a_port))
        print("[B] Connected to server A")

        message = s.recv(1024).decode()
        print(f"[B] Message from A: {message}")

        credentials = "admin|admin"
        s.sendall(credentials.encode())

        response = s.recv(1024).decode()
        print(f"[B] Authentication response: {response}")

        if "successful" not in response.lower():
            print("[B] Authentication failed. Closing connection.")
            s.close()
            return None

        return s

    def handle_client_c(self, conn_c, conn_a):
        try:
            while True:
                data = conn_c.recv(1024)
                if not data:
                    break
                print(f"[B] Received from C: {data.decode()}")
                conn_a.sendall(data)

                response = conn_a.recv(1024)
                print(f"[B] Response from A: {response.decode()}")
                conn_c.sendall(response)
        except Exception as e:
            print(f"[B] Communication error: {e}")
        finally:
            conn_c.close()
            self.stop_event.set()  # Stop sending messages if client disconnects

    def listen_for_client_c(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('0.0.0.0', self.listen_port))
            server.listen()
            print("[B] Waiting for client C to connect...")
            conn_c, addr = server.accept()
            print(f"[B] Client C connected: {addr}")
            self.handle_client_c(conn_c, self.conn_a)

    def send_messages_to_a(self):
        """Thread method to send manual messages to server A."""
        try:
            while not self.stop_event.is_set():
                msg = input("[B] Enter message to send to A (or 'exit' to stop): ")
                if msg.strip().lower() == "exit":
                    print("[B] Stopping message sender.")
                    self.stop_event.set()
                    self.conn_a.close()
                    break
                self.conn_a.sendall(msg.encode())
                response = self.conn_a.recv(1024).decode()
                print(f"[B] Response from A: {response}")
        except Exception as e:
            print(f"[B] Error sending messages to A: {e}")
            self.stop_event.set()

    def start(self):
        self.conn_a = self.connect_to_server_a()
        if self.conn_a:
            # Start thread for manual sending messages to A
            sender_thread = threading.Thread(target=self.send_messages_to_a, daemon=True)
            sender_thread.start()

            # Listen for client C
            self.listen_for_client_c()

            # Wait for sender thread to finish before exiting
            sender_thread.join()

    def new_branch(self, name, last_name, password="000000"):
        message = f"NEW_BRANCH|{name}|{last_name}|{password}"
        return self.send_command_to_a(message)

    def change_branch_name(self, user_code, new_name):
        message = f"CHANGE_NAME_BRANCH|{user_code}|{new_name}"
        return self.send_command_to_a(message)

    def change_branch_last_name(self, user_code, new_last_name):
        message = f"CHANGE_LAST_NAME_BRANCH|{user_code}|{new_last_name}"
        return self.send_command_to_a(message)

    def change_password_branch(self, user_code, new_password):
        message = f"CHANGE_PASSWORD_BRANCH|{user_code}|{new_password}"
        return self.send_command_to_a(message)

    def delete_branch(self, user_code):
        message = f"DELETE_BRANCH|{user_code}"
        return self.send_command_to_a(message)

    def send_command_to_a(self, message):
        try:
            self.conn_a.sendall(message.encode())
            response = self.conn_a.recv(1024).decode()
            print(f"[B] Response from A: {response}")
            return response
        except Exception as e:
            print(f"[B] Error sending command to A: {e}")
            return f"ERROR|{str(e)}"

if __name__ == "__main__":
    ip_a = "127.0.0.1"
    port_a = 10000

    branch_server = Branch_Server(ip_a, port_a)
    branch_server.start()
