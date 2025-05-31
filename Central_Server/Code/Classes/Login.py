import os
import pandas as pd
import hashlib


class Login:
    def __init__(self, parquet_path):
        # The constructor has a reference to the database path, and reads the database into a DataFrame.
        self.df = pd.read_parquet(parquet_path)

    def verify_credentials(self, username, password):
        # The method reads the username and search for the corresponding password in the database
        # If the username is not found, return False
        result = self.df.loc[self.df['admin'] == username, 'password'].values
        if len(result) == 0:
            print("User not found.")
            return False

        stored_password = result[0]

        # Create SHA512 hashes for comparison
        input_hash = hashlib.sha512((username + password).encode()).hexdigest()
        stored_hash = hashlib.sha512((username + stored_password).encode()).hexdigest()

        # Compare hashes
        return input_hash == stored_hash

    def start_login(self,username, password):
        while True:
            #username = input("<USER>: ")
            #password = input("<PASSWORD>: ")
            #print("Logging in...")

            if self.verify_credentials(username, password):
                print("Login successful.")
                return username
            else:
                return False

# ---- This part should be outside the class ----
'''
if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(base_path, "..", "db", "usuarios.parquet")

    login_system = Login(parquet_path)
    logged_user = login_system.start_login()

    print(f"Welcome, {logged_user}!")
'''