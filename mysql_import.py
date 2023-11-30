import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import mysql.connector
import json
from datetime import date, datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def mysql_import(host, user, password, database, tables):

    try:
        connection = mysql.connector.connect(
            
            host=host,
            user=user,
            password=password,
            database=database
            )
    except mysql.connector.Error as err:
        print(f"Erro")
        return
    
    for table in tables:
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(f"SELECT * FROM {table}")
            table_data = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erro buscando dados de {table}: {err}")
            continue
        finally:
            cursor.close()

        table_file_path = f"{table}.json"
        with open(table_file_path,"w") as jsonfile:
            json.dump({table: table_data}, jsonfile,cls=CustomJSONEncoder, indent=2)

    connection.close()

def select_directory():
    directory_path = filedialog.askdirectory(title="Selecione o diretório")
    return directory_path

def on_import_button_click():
    host = host_entry.get()
    user = user_entry.get()
    password = password_entry.get()
    database = database_entry.get()
    selected_tables = tables_entry.get().split(",") 

    if not all([host, user, password, database, selected_tables]):
        messagebox.showerror("Erro", "Complete todos os campos")
        return

    mysql_import(host, user, password, database, selected_tables)
    messagebox.showinfo("Successo", "Dados importados com sucesso")


window = tk.Tk()
window.title("Importar dados do MySQL")

tk.Label(window, text="MySQL Host:").grid(row=0, column=0, sticky="e")
tk.Label(window, text="MySQL Usuário:").grid(row=1, column=0, sticky="e")
tk.Label(window, text="Senha:").grid(row=2, column=0, sticky="e")
tk.Label(window, text="Database:").grid(row=3, column=0, sticky="e")
tk.Label(window, text="Tabelas (separadas por vírgula):").grid(row=4, column=0, sticky="e")

host_entry = tk.Entry(window)
user_entry = tk.Entry(window)
password_entry = tk.Entry(window, show="*")
database_entry = tk.Entry(window)
tables_entry = tk.Entry(window)

host_entry.grid(row=0, column=1)
user_entry.grid(row=1, column=1)
password_entry.grid(row=2, column=1)
database_entry.grid(row=3, column=1)
tables_entry.grid(row=4, column=1)

import_button = tk.Button(window, text="Importar Dados", command=on_import_button_click)
import_button.grid(row=5, column=0, columnspan=2, pady=10)

window.mainloop()





        