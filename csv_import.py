import os
import csv
import json
import tkinter as tk
from tkinter import filedialog

# .json output data path
data_directory = os.path.join(os.path.dirname(__file__), 'data')

# Remove extra spaces and double quotes from column name
def clean_column_name(column_name):
    return column_name.strip().replace('"', '')

# Import .csv files from a directory and convert to .json
def csv_import(directory):
    # List all .csv files in the directory
    csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]

    for csv_file in csv_files:
        table_name = os.path.splitext(csv_file)[0]

        file_path = os.path.join(directory, csv_file)

        with open(file_path, 'r', newline='') as csvfile:
            csv_reader = csv.DictReader(csvfile)

            # Clears column names
            cleaned_column_names = [clean_column_name(column) for column in csv_reader.fieldnames]

            # Create a list of dictionaries that represent CSV rows
            table_data = [{cleaned_column_names[i]: row[column] for i, column in enumerate(csv_reader.fieldnames)}
                for row in csv_reader]

        # Path to output .json files
        table_file_path = os.path.join(data_directory, f"{table_name}.json")
        with open(table_file_path,'w') as jsonfile:
            json.dump({table_name: table_data}, jsonfile, indent=2)

# Opens a directory selection window and returns the chosen path
def select_directory():
    root = tk.Tk()
    root.withdraw()

    directory_path = filedialog.askdirectory(title="Escolha o Diretório")
    
    return directory_path

selected_directory = select_directory()

if selected_directory:
    # create data folder if it does not exist
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    csv_import(selected_directory)
else:
    print("No directory selected. Exiting.")
