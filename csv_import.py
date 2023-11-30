import os
import csv
import json
import tkinter as tk
from tkinter import filedialog

def clean_column_name(column_name):
    return column_name.strip().replace('"', '')

def csv_import(directory):

    csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]

    for csv_file in csv_files:
        table_name = os.path.splitext(csv_file)[0]

        file_path = os.path.join(directory,csv_file)

        with open(file_path, 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            cleaned_column_names = [clean_column_name(column) for column in csv_reader.fieldnames]


            table_data = [{cleaned_column_names[i]: row[column] for i, column in enumerate(csv_reader.fieldnames)}
                for row in csv_reader]

        table_file_path = f"{table_name}.json"
        with open(table_file_path,'w') as jsonfile:
            json.dump({table_name: table_data}, jsonfile, indent=2)

def select_directory():
    root = tk.Tk()
    root.withdraw()

    directory_path = filedialog.askdirectory(title="Escolha o Diretório")
    return directory_path

selected_directory = select_directory()

if selected_directory:
    csv_import(selected_directory)
else:
    print("No directory selected. Exiting.")

