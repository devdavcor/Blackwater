import numpy as np
import pandas as pd
import os

def new_user(curp, name, last_name):
    try:
        # Obtener rutas
        paths = _get_db_paths()

        # Cargar DataFrames
        users_data_df = pd.read_parquet(paths['users_data'])
        users_balance_df = pd.read_parquet(paths['users_balance'])
        users_biometrics_df = pd.read_parquet(paths['users_biometrics'])

        # Cargar o crear users_df
        if os.path.exists(paths['users']):
            users_df = pd.read_parquet(paths['users'])
        else:
            users_df = pd.DataFrame(columns=['user', 'password'])

        # Validar si el curp ya existe
        if (users_data_df['curp'] == curp).any():
            print("⚠️ El CURP ya existe. No se registró.")
            return False

        # Crear nuevo usuario
        user_number = len(users_data_df) + 1
        user_code = f"U{user_number:04d}{name[0].upper()}{last_name[0].upper()}"

        # Actualizar todos los DataFrames
        users_data_df = pd.concat([users_data_df, pd.DataFrame([{
            'user': user_code,
            'curp': curp,
            'name': name,
            'last_name': last_name,
            'number': user_number
        }])], ignore_index=True)

        users_balance_df = pd.concat([users_balance_df, pd.DataFrame([{
            'user': user_code,
            'balance': 0.0
        }])], ignore_index=True)

        users_biometrics_df = pd.concat([users_biometrics_df, pd.DataFrame([{
            'user': user_code,
            'biometrics': np.zeros(128).tolist()
        }])], ignore_index=True)

        users_df = pd.concat([users_df, pd.DataFrame([{
            'user': user_code,
            'password': "000000"
        }])], ignore_index=True)

        # Guardar cambios
        users_data_df.to_parquet(paths['users_data'], index=False)
        users_balance_df.to_parquet(paths['users_balance'], index=False)
        users_biometrics_df.to_parquet(paths['users_biometrics'], index=False)
        users_df.to_parquet(paths['users'], index=False)

        print(f"✅ Usuario '{user_code}' registrado correctamente con número {user_number}.")
        return True

    except Exception as e:
        print(f"❌ Error al registrar el usuario: {e}")
        return False


def delete_user(user_code):
    try:
        # Obtener rutas
        paths = _get_db_paths()
        user_found = False

        # Procesar cada archivo
        for key in ['users_data', 'users_balance', 'users_biometrics', 'users']:
            path = paths[key]
            if os.path.exists(path):
                df = pd.read_parquet(path)
                if user_code in df['user'].values:
                    user_found = True
                    df = df[df['user'] != user_code]
                    df.to_parquet(path, index=False)

        if user_found:
            print(f"🗑️ Usuario '{user_code}' eliminado correctamente de todos los registros existentes.")
        else:
            print(f"⚠️ El usuario '{user_code}' no existe en ninguno de los registros.")

    except Exception as e:
        print(f"❌ Error al eliminar el usuario: {e}")


def _get_db_paths():
    base_path = os.path.dirname(os.path.abspath(__file__))
    blackwater_root = os.path.abspath(os.path.join(base_path, "..", "..", ".."))
    db_path = os.path.join(blackwater_root, "Central_Server", "Resources", "DB")
    return {
        "users_data": os.path.join(db_path, 'users_data.parquet'),
        "users_balance": os.path.join(db_path, 'users_balance.parquet'),
        "users_biometrics": os.path.join(db_path, 'users_biometrics.parquet'),
        "users": os.path.join(db_path, 'users.parquet'),
    }


def change_name(user_code, new_name):
    paths = _get_db_paths()
    df = pd.read_parquet(paths['users_data'])
    if user_code not in df['user'].values:
        print(f"⚠️ Usuario '{user_code}' no encontrado.")
        return False
    df.loc[df['user'] == user_code, 'name'] = new_name
    df.to_parquet(paths['users_data'], index=False)
    print(f"✅ Nombre cambiado a '{new_name}' para usuario '{user_code}'.")
    return True

def change_last_name(user_code, new_last_name):
    paths = _get_db_paths()
    df = pd.read_parquet(paths['users_data'])
    if user_code not in df['user'].values:
        print(f"⚠️ Usuario '{user_code}' no encontrado.")
        return False
    df.loc[df['user'] == user_code, 'last_name'] = new_last_name
    df.to_parquet(paths['users_data'], index=False)
    print(f"✅ Apellido cambiado a '{new_last_name}' para usuario '{user_code}'.")
    return True

def change_curp(user_code, new_curp):
    paths = _get_db_paths()
    df = pd.read_parquet(paths['users_data'])

    if user_code not in df['user'].values:
        print(f"⚠️ Usuario '{user_code}' no encontrado.")
        return False

    # Verificar que new_curp no exista en otro usuario distinto
    curp_exists = df[(df['curp'] == new_curp) & (df['user'] != user_code)]
    if not curp_exists.empty:
        print("⚠️ El CURP ya existe para otro usuario.")
        return False

    df.loc[df['user'] == user_code, 'curp'] = new_curp
    df.to_parquet(paths['users_data'], index=False)
    print(f"✅ CURP cambiado a '{new_curp}' para usuario '{user_code}'.")
    return True

def change_password(user_code, new_password):
    paths = _get_db_paths()
    df = pd.read_parquet(paths['users'])
    if user_code not in df['user'].values:
        print(f"⚠️ Usuario '{user_code}' no encontrado.")
        return False
    df.loc[df['user'] == user_code, 'password'] = new_password
    df.to_parquet(paths['users'], index=False)
    print(f"✅ Password cambiado para usuario '{user_code}'.")
    return True

def withdraw_balance(user_code, amount):
    paths = _get_db_paths()
    df = pd.read_parquet(paths['users_balance'])
    if user_code not in df['user'].values:
        print(f"⚠️ Usuario '{user_code}' no encontrado.")
        return False
    amount = abs(amount)
    current_balance = df.loc[df['user'] == user_code, 'balance'].iloc[0]
    if current_balance < amount:
        print(f"⚠️ Saldo insuficiente para retirar {amount}. Saldo actual: {current_balance}")
        return False
    df.loc[df['user'] == user_code, 'balance'] = current_balance - amount
    df.to_parquet(paths['users_balance'], index=False)
    print(f"✅ Se retiraron {amount} del balance del usuario '{user_code}'. Nuevo saldo: {current_balance - amount}")
    return True

def deposit_balance(user_code, amount):
    paths = _get_db_paths()
    df = pd.read_parquet(paths['users_balance'])
    if user_code not in df['user'].values:
        print(f"⚠️ Usuario '{user_code}' no encontrado.")
        return False
    amount = abs(amount)
    current_balance = df.loc[df['user'] == user_code, 'balance'].iloc[0]
    df.loc[df['user'] == user_code, 'balance'] = current_balance + amount
    df.to_parquet(paths['users_balance'], index=False)
    print(f"✅ Se depositaron {amount} al balance del usuario '{user_code}'. Nuevo saldo: {current_balance + amount}")
    return True

def check_balance(user_code):
    paths = _get_db_paths()
    df = pd.read_parquet(paths['users_balance'])
    if user_code not in df['user'].values:
        print(f"⚠️ Usuario '{user_code}' no encontrado.")
        return None
    balance = df.loc[df['user'] == user_code, 'balance'].iloc[0]
    print(f"💰 El balance del usuario '{user_code}' es: {balance}")
    return balance

def get_user_by_curp(curp: str) :
    paths = _get_db_paths ()
    users_data_path = paths['users_data']

    if not os.path.exists ( users_data_path ) :
        print ( "⚠️ El archivo users_data.parquet no existe." )
        return None

    df = pd.read_parquet ( users_data_path )
    user_row = df.loc[df['curp'] == curp]

    if user_row.empty :
        print ( f"⚠️ No se encontró usuario con CURP '{curp}'." )
        return None

    user_code = user_row.iloc[0]['user']
    return user_code

def print_parquet(path, name):
    if os.path.exists(path):
        df = pd.read_parquet(path)
        print(f"\n--- Contenido de {name} ---")
        print(df)
    else:
        print(f"\n⚠️ Archivo {name} no encontrado en {path}")

def _get_admin_path():
    base_path = os.path.dirname(os.path.abspath(__file__))
    blackwater_root = os.path.abspath(os.path.join(base_path, "..", "..", ".."))
    db_path = os.path.join(blackwater_root, "Central_Server", "Resources", "DB")
    return os.path.join(db_path, 'administrators.parquet')

def new_administrator(name, last_name, password="000000"):
    try:
        admin_path = _get_admin_path()

        if os.path.exists(admin_path):
            admins_df = pd.read_parquet(admin_path)
        else:
            admins_df = pd.DataFrame(columns=['user', 'password', 'name', 'last_name', 'number'])

        # Calcular número para nuevo admin
        user_number = len(admins_df) + 1
        user_code = f"A{user_number:04d}{name[0].upper()}{last_name[0].upper()}"

        # Verificar que no exista ya el user_code
        if user_code in admins_df['user'].values:
            print(f"⚠️ El usuario '{user_code}' ya existe.")
            return False

        new_admin = pd.DataFrame([{
            'user': user_code,
            'password': password,
            'name': name,
            'last_name': last_name,
            'number': user_number
        }])

        admins_df = pd.concat([admins_df, new_admin], ignore_index=True)
        admins_df.to_parquet(admin_path, index=False)

        print(f"✅ Administrador '{user_code}' creado correctamente.")
        return True

    except Exception as e:
        print(f"❌ Error al crear administrador: {e}")
        return False

def change_password_admin(user_code, new_password):
    try:
        admin_path = _get_admin_path()

        if not os.path.exists(admin_path):
            print("⚠️ Archivo de administradores no existe.")
            return False

        admins_df = pd.read_parquet(admin_path)

        if user_code not in admins_df['user'].values:
            print(f"⚠️ Administrador '{user_code}' no encontrado.")
            return False

        admins_df.loc[admins_df['user'] == user_code, 'password'] = new_password
        admins_df.to_parquet(admin_path, index=False)

        print(f"✅ Password cambiado para administrador '{user_code}'.")
        return True

    except Exception as e:
        print(f"❌ Error al cambiar password del administrador: {e}")
        return False


def delete_administrator(user_code):
    try:
        admin_path = _get_admin_path()

        if not os.path.exists(admin_path):
            print("⚠️ Archivo de administradores no existe.")
            return False

        admins_df = pd.read_parquet(admin_path)

        if user_code not in admins_df['user'].values:
            print(f"⚠️ Administrador '{user_code}' no encontrado.")
            return False

        admins_df = admins_df[admins_df['user'] != user_code]
        admins_df.to_parquet(admin_path, index=False)

        print(f"🗑️ Administrador '{user_code}' eliminado correctamente.")
        return True

    except Exception as e:
        print(f"❌ Error al eliminar administrador: {e}")
        return False

def change_admin_name(user_code, new_name):
    try:
        admin_path = _get_admin_path()

        if not os.path.exists(admin_path):
            print("⚠️ Archivo de administradores no existe.")
            return False

        admins_df = pd.read_parquet(admin_path)

        if user_code not in admins_df['user'].values:
            print(f"⚠️ Administrador '{user_code}' no encontrado.")
            return False

        admins_df.loc[admins_df['user'] == user_code, 'name'] = new_name
        admins_df.to_parquet(admin_path, index=False)

        print(f"✅ Nombre actualizado para administrador '{user_code}'.")
        return True

    except Exception as e:
        print(f"❌ Error al cambiar el nombre del administrador: {e}")
        return False

def change_admin_last_name(user_code, new_last_name):
    try:
        admin_path = _get_admin_path()

        if not os.path.exists(admin_path):
            print("⚠️ Archivo de administradores no existe.")
            return False

        admins_df = pd.read_parquet(admin_path)

        if user_code not in admins_df['user'].values:
            print(f"⚠️ Administrador '{user_code}' no encontrado.")
            return False

        admins_df.loc[admins_df['user'] == user_code, 'last_name'] = new_last_name
        admins_df.to_parquet(admin_path, index=False)

        print(f"✅ Apellido actualizado para administrador '{user_code}'.")
        return True

    except Exception as e:
        print(f"❌ Error al cambiar el apellido del administrador: {e}")
        return False

def _get_branch_path():
    base_path = os.path.dirname(os.path.abspath(__file__))
    blackwater_root = os.path.abspath(os.path.join(base_path, "..", "..", ".."))
    db_path = os.path.join(blackwater_root, "Central_Server", "Resources", "DB")
    return os.path.join(db_path, 'branches.parquet')


def new_branch(name, last_name, password="000000"):
    try:
        branch_path = _get_branch_path()

        if os.path.exists(branch_path):
            branches_df = pd.read_parquet(branch_path)
        else:
            branches_df = pd.DataFrame(columns=['user', 'password', 'name', 'last_name', 'number'])

        user_number = len(branches_df) + 1
        user_code = f"B{user_number:04d}{name[0].upper()}{last_name[0].upper()}"

        if user_code in branches_df['user'].values:
            print(f"⚠️ La sucursal '{user_code}' ya existe.")
            return False

        new_branch = pd.DataFrame([{
            'user': user_code,
            'password': password,
            'name': name,
            'last_name': last_name,
            'number': user_number
        }])

        branches_df = pd.concat([branches_df, new_branch], ignore_index=True)
        branches_df.to_parquet(branch_path, index=False)

        print(f"✅ Sucursal '{user_code}' creada correctamente.")
        return True

    except Exception as e:
        print(f"❌ Error al crear sucursal: {e}")
        return False

def change_password_branch(user_code, new_password):
    try:
        branch_path = _get_branch_path()

        if not os.path.exists(branch_path):
            print("⚠️ Archivo de sucursales no existe.")
            return False

        branches_df = pd.read_parquet(branch_path)

        if user_code not in branches_df['user'].values:
            print(f"⚠️ Sucursal '{user_code}' no encontrada.")
            return False

        branches_df.loc[branches_df['user'] == user_code, 'password'] = new_password
        branches_df.to_parquet(branch_path, index=False)

        print(f"✅ Password actualizado para sucursal '{user_code}'.")
        return True

    except Exception as e:
        print(f"❌ Error al cambiar password de la sucursal: {e}")
        return False

def delete_branch(user_code):
    try:
        branch_path = _get_branch_path()

        if not os.path.exists(branch_path):
            print("⚠️ Archivo de sucursales no existe.")
            return False

        branches_df = pd.read_parquet(branch_path)

        if user_code not in branches_df['user'].values:
            print(f"⚠️ Sucursal '{user_code}' no encontrada.")
            return False

        branches_df = branches_df[branches_df['user'] != user_code]
        branches_df.to_parquet(branch_path, index=False)

        print(f"🗑️ Sucursal '{user_code}' eliminada correctamente.")
        return True

    except Exception as e:
        print(f"❌ Error al eliminar sucursal: {e}")
        return False

def change_branch_name(user_code, new_name):
    try:
        branch_path = _get_branch_path()

        if not os.path.exists(branch_path):
            print("⚠️ Archivo de sucursales no existe.")
            return False

        branches_df = pd.read_parquet(branch_path)

        if user_code not in branches_df['user'].values:
            print(f"⚠️ Sucursal '{user_code}' no encontrada.")
            return False

        branches_df.loc[branches_df['user'] == user_code, 'name'] = new_name
        branches_df.to_parquet(branch_path, index=False)

        print(f"✅ Nombre actualizado para sucursal '{user_code}'.")
        return True

    except Exception as e:
        print(f"❌ Error al cambiar el nombre de la sucursal: {e}")
        return False

def change_branch_last_name(user_code, new_last_name):
    try:
        branch_path = _get_branch_path()

        if not os.path.exists(branch_path):
            print("⚠️ Archivo de sucursales no existe.")
            return False

        branches_df = pd.read_parquet(branch_path)

        if user_code not in branches_df['user'].values:
            print(f"⚠️ Sucursal '{user_code}' no encontrada.")
            return False

        branches_df.loc[branches_df['user'] == user_code, 'last_name'] = new_last_name
        branches_df.to_parquet(branch_path, index=False)

        print(f"✅ Apellido actualizado para sucursal '{user_code}'.")
        return True

    except Exception as e:
        print(f"❌ Error al cambiar el apellido de la sucursal: {e}")
        return False



if __name__ == "__main__" :
    '''
    curp = "MCRJ850712HDFLNS09"
    name = "Marco"
    last_name = "Jiménez"

    # Cambiar nombre
    change_name ( "U0008MJ", "Marcos" )

    # Cambiar apellido
    change_last_name ( "U0008MJ", "Nava" )

    # Cambiar CURP
    change_curp ( "U0008MJ", "CRZL900101HDFABC02" )

    # Cambiar password
    change_password ( "U0008MJ", "nuevo_pass123" )

    # Depositar saldo
    deposit_balance ( "U0008MJ", 500.50 )

    # Retirar saldo
    withdraw_balance ( "U0008MJ", 200.0 )
    '''
    '''
    new_administrator("Michael", "Jordan")       # Creará algo como A0001MJ con password default "000000"
    change_password_admin("A0009MJ", "newpass")  # Cambiar contraseña
    change_admin_name("A0009MJ", "Ronaldo")
    change_admin_last_name("A0009MJ", "Dos Santos")
    delete_administrator("A0010MJ")               # Eliminar admin
    '''
    #new_branch ( "Michael", "Jordan" )  # Creará algo como B0001MJ con password default "000000"
    #change_password_branch ( "B0009MJ", "newpass" )  # Cambiar contraseña
    #change_branch_name ( "B0009MJ", "Ronaldo" )  # Cambiar nombre
    #change_branch_last_name ( "B0009MJ", "Dos Santos" )  # Cambiar apellido
    delete_user('U0008MJ')







