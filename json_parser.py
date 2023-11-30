import json
import os

def load_data():
    data = {}
    
    current_directory = os.getcwd()


    for filename in os.listdir(current_directory):
        if filename.endswith(".json"):
            table_name = os.path.splitext(filename)[0]

            with open(filename, 'r') as jsonfile:
                table_data = json.load(jsonfile).get(table_name, [])

            data[table_name] = table_data

    return data

def parse_query(query,data):

    if query.startswith("PEGAR") and "DE" in query:
        select_clause, from_clause = query.split("DE", 1)

        column_name = select_clause.split("PEGAR")[1].strip()

        table = from_clause.strip()

        print(f"Query: {query}")
        print(f"Column Name: {column_name}")
        print(f"Table: {table}")

        result = execute_query(column_name,table,data)
        return result
    else:
        return "Sintaxe inválida"
    
def execute_query(column_name,table,data):

    with open(f"{table}.json",'r') as jsonfile:
        table_data = json.load(jsonfile).get(table, [])

        result = [row.get(column_name) for row in table_data]

        return result
    

json_query = "PEGAR Average DE hurricanes"
data = load_data()
result=parse_query(json_query,data)
print(result)
    

