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
        select_clause, from_and_where_clause = query.split("DE", 1)

        columns_raw = select_clause.split("PEGAR")[1].strip()

        if columns_raw == "*":
            columns = ["*"]
        else:
            if "*" in columns_raw:
                raise ValueError("Não é permitido usar '*' junto com outros campos.")
            
            columns = [col.strip() for col in columns_raw.split(",")]

        if "ONDE" in from_and_where_clause:
            from_clause, where_clause = map(str.strip, from_and_where_clause.split("ONDE"))
        else:
            from_clause = from_and_where_clause.strip()
            where_clause = None

        print(f"Query: {query}")
        print(f"Columns: {columns}")
        print(f"Table: {from_clause}")
        print(f"Where Clause: {where_clause}")

        result = execute_query(columns, from_clause, where_clause, data)
        return result
    else:
        return "Sintaxe inválida"

# Execute a query on the loaded data and return the result of the query
def execute_query(columns, table, where_clause, data):
    with open(os.path.join(data_directory, f"{table}.json"), 'r') as jsonfile:
        table_data = json.load(jsonfile).get(table, [])

        if columns == ["*"]:
            result = table_data
        else:
            result = [{col: row.get(col) for col in columns} for row in table_data]

        # Apply WHERE clause
        if where_clause:
            result = apply_where_clause(result, where_clause)

        return result

# Apply the WHERE clause to filter the data.
def apply_where_clause(data, where_clause):
    if not where_clause:
        return data

    # Break string into field, operator and value
    column, operator, value = map(str.strip, where_clause.split())
    filtered_data = [row for row in data if compare_values(row.get(column), operator, value)]
    return filtered_data

# Compare values based on the operator
def compare_values(data_value, operator, condition_value):

    if operator == "=":
        return data_value == condition_value
    elif operator == ">":
        return data_value > condition_value
    elif operator == ">=":
        return data_value >= condition_value
    elif operator == "<":
        return data_value < condition_value
    elif operator == "<=":
        return data_value <= condition_value
    else:
        raise ValueError(f"Operador desconhecido: {operator}")

json_query = "PEGAR Average, Month DE hurricanes ONDE Month = Dec"
data = load_data()
result = parse_query(json_query, data)
print(result)
