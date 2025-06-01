import os
import pandas as pd
import hashlib


class Login :
    def __init__(self, base_path, parquet_filename="administrators.parquet") :
        # Construimos la ruta absoluta del parquet, relativa al base_path
        parquet_path = os.path.join ( base_path, "Resources", "DB", parquet_filename )

        if not os.path.isfile ( parquet_path ) :
            raise FileNotFoundError ( f"No se encontró el archivo parquet en: {parquet_path}" )

        self.df = pd.read_parquet ( parquet_path )

    def verify_credentials(self, username, password) :
        result = self.df.loc[self.df['user'] == username, 'password'].values
        if len ( result ) == 0 :
            print ( "User not found." )
            return False

        stored_password = result[0]

        input_hash = hashlib.sha512 ( (username + password).encode () ).hexdigest ()
        stored_hash = hashlib.sha512 ( (username + stored_password).encode () ).hexdigest ()

        return input_hash == stored_hash

    def start_login(self, username, password) :
        if self.verify_credentials ( username, password ) :
            print ( "Login successful." )
            return username
        else :
            return False


# Código para probar o usar la clase desde un script principal (fuera de la clase)

if __name__ == "__main__":
    # base_path es la carpeta Central_Server, subiendo 3 niveles desde Code/Classes/Login.py
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    login_system = Login(base_path)

    user = "admin"
    pwd = "admin"

    logged_user = login_system.start_login(user, pwd)

    if logged_user:
        print(f"Welcome, {logged_user}!")
    else:
        print("Login failed.")

