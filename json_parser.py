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

def parse_query(query, data):

    if query.startswith("PEGAR") and "DE" in query:
        select_clause, from_clause = query.split("DE", 1)
        columns = [col.strip() for col in select_clause.split("PEGAR")[1].split(",")]

        table = from_clause.strip()

        print(f"Query: {query}")
        print(f"Columns: {columns}")
        print(f"Table: {table}")

        result = execute_query(columns, table, data)
        return result
    else:
        return "Sintaxe inválida"
    
def execute_query(columns, table, data):
    
    with open(f"{table}.json",'r') as jsonfile:
        table_data = json.load(jsonfile).get(table, [])
        result = [{col: row.get(col) for col in columns} for row in table_data]

        return result

json_query = "PEGAR Month, Average DE hurricanes"
data = load_data()
result=parse_query(json_query,data)
print(result)
