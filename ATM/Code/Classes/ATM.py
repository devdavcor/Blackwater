import socket
import ast
import re

class ATM:
    def __init__(self, ip_branch, port_branch):
        self.ip_branch = ip_branch
        self.port_branch = port_branch
        self.balance = 0

    def send_alert(self, sender_info) :
        """Envía una alerta con la información del remitente."""
        command = f"ALERT|{sender_info}"
        response = self.send_message ( command )
        print ( f"[ATM] Alerta enviada: {response}" )
        return response

    def start(self, user, password) :
        try :
            self.conn_b = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
            self.conn_b.connect ( (self.ip_branch, self.port_branch) )
            print ( "[ATM] Conectado con Branch Server (B)" )

            credentials_msg = f"ATM_CREDENTIALS|{user}|{password}"
            self.conn_b.sendall ( credentials_msg.encode () )
            print ( f"[ATM] Credenciales enviadas: {credentials_msg}" )

            response = self.conn_b.recv ( 1024 ).decode ()
            print ( f"[ATM] Respuesta de B: {response}" )

            return "TRUE" in response.upper ()

        except Exception as e :
            print ( f"[ATM] Error: {e}" )
            return False

    '''def send_message(self, message):
        """Método auxiliar para enviar un mensaje al servidor y recibir respuesta."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip_branch, self.port_branch))
                s.sendall(message.encode())
                data = s.recv(32768)
                return data.decode()
        except Exception as e:
            return f"[ATM] Error: {e}"'''

    def check_balance(self, user):
        """Consulta el saldo del usuario."""
        response = self.send_message(f"CHECK_BALANCE|{user}")
        print(f"[ATM] Saldo de {user}: {response}")
        return response

    def deposit_cash(self, user, amount):
        """Deposita una cantidad de dinero en la cuenta del usuario."""
        response = self.send_message(f"DEPOSIT_CASH|{user}|{amount}")
        print(f"[ATM] Depósito: {response}")
        return response

    def withdraw_cash(self, user, amount):
        """Retira una cantidad de dinero de la cuenta del usuario."""
        response = self.send_message(f"WITHDRAW_CASH|{user}|{amount}")
        print(f"[ATM] Retiro: {response}")
        return response

    def send_message(self, message: str) -> str:
        self.conn_b.sendall(message.encode())
        return self.conn_b.recv(32768).decode()

    def get_biometrics(self, user):
        response = self.send_message(f"GET_BIOMETRICS|{user}")
        print(f"[ATM] Biometrics response: {response}")

        parts = response.split("|")
        if len(parts) >= 3 and parts[0] == "GET_BIOMETRICS" and parts[1] == user:
            vector_str = re.sub(r'\s+', ', ', parts[2].strip())
            try:
                biometrics_list = ast.literal_eval(vector_str)
                return biometrics_list
            except (SyntaxError, ValueError) as e:
                print(f"[ERROR] No se pudo interpretar el vector: {e}")
                return None
        else:
            raise ValueError("Respuesta inválida o inesperada")

    def update_password(self, user, new_password):
        """Actualiza la contraseña del usuario."""
        response = self.send_message(f"UPDATE_PASSWORD|{user}|{new_password}")
        print(f"[ATM] Contraseña actualizada: {response}")
        return response



if __name__ == "__main__":
    # IP y puerto de Branch Server (B) quemados para pruebas
    ip_b = "127.0.0.1"
    port_b = 11000

    atm = ATM(ip_b, port_b)
    atm.start()
