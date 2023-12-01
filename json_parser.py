import json
import os

# .json output data path
data_directory = os.path.join(os.path.dirname(__file__), 'data')

# Load data from JSON files
def load_data():
    data = {}

    for filename in os.listdir(data_directory):
        if filename.endswith(".json"):
            table_name = os.path.splitext(filename)[0]

            with open(os.path.join(data_directory, filename), 'r') as jsonfile:
                table_data = json.load(jsonfile).get(table_name, [])

            data[table_name] = table_data

    return data

# Parse and execute a query on the loaded data.
def parse_query(query, data):
    if query.startswith("PEGAR") and "DE" in query:
        select_clause, from_clause = query.split("DE", 1)

        columns_raw = select_clause.split("PEGAR")[1].strip()

        if columns_raw == "*":
            columns = ["*"]
        else:
            if "*" in columns_raw:
                raise ValueError("Não é permitido usar '*' junto com outros campos.")
            
            columns = [col.strip() for col in columns_raw.split(",")]

        table = from_clause.strip()

        print(f"Query: {query}")
        print(f"Columns: {columns}")
        print(f"Table: {table}")

        result = execute_query(columns, table, data)
        return result
    else:
        return "Sintaxe inválida"

# Execute a query on the loaded data and return the result of the query
def execute_query(columns, table, data):
    with open(os.path.join(data_directory, f"{table}.json"), 'r') as jsonfile:
        table_data = json.load(jsonfile).get(table, [])

        if columns == ["*"]:
            result = table_data
        else:
            result = [{col: row.get(col) for col in columns} for row in table_data]

        return result

json_query = "PEGAR * DE hurricanes"
data = load_data()
result = parse_query(json_query, data)
print(result)
