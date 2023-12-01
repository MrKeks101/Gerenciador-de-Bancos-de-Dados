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

    query_list = query.split(' ')
    query_words = [element.replace(',', '') for element in query_list]

    if "PEGAR" in query_words and "DE" in query_words:
        select_index = query_words.index("PEGAR")
        from_index = query_words.index("DE")
        select_columns = [col for col in query_words[select_index + 1:from_index]]
    
    if "DE" in query_words:
        from_index = query_words.index("DE")
        table = query_words[from_index + 1]

        query_result = _from(select_columns, table)
        from_data = query_result
    
    if "ONDE" in query_words:
        where_index = query_words.index("ONDE")
        
        # column, condition and value
        where_column = query_words[where_index + 1]
        where_condition = query_words[where_index + 2]
        value = query_words[where_index + 3]

        # two conditions
        logical_operator = None
        if "OU" in query_words:
            logical_operator = "OU"
        elif "E" in query_words:
            logical_operator = "E"

        if logical_operator:
            logical_index = query_words.index(logical_operator)

            # column, condition and value of second condition
            where_column2 = query_words[logical_index + 1]
            where_condition2 = query_words[logical_index + 2]
            value2 = query_words[logical_index + 3]

            result = _and_or(from_data, where_column, where_condition, value, logical_operator, where_column2, where_condition2, value2)
        else:
            result = _where(from_data, where_column, where_condition, value)
    else:
        result = from_data  # Se não houver cláusula ONDE, o resultado é a tabela selecionada

    # Verificar se há cláusula ORDER BY
    if "ORDENE" in query_words:
        order_index = query_words.index("ORDENE")
        order_column = query_words[order_index + 1]

        order_type = "CRESCENTE"  # Default caso usuário não informe
        if "CRESCENTE" in query_words:
            order_type = "CRESCENTE"
        elif "DECRESCENTE" in query_words:
            order_type = "DECRESCENTE"

        result = _order(result, order_column, order_type)

    return result

def _order(data, column, order_type):
    # Se for decrescente, seta reverse_order para true e inverte a ordenação
    reverse_order = (order_type == "DECRESCENTE")
    return sorted(data, key=lambda x: x.get(column, 0), reverse=reverse_order)

def _from(select_columns, table):
    try:
        with open(os.path.join(data_directory, f"{table}.json"), 'r') as json_file:
            table_data = json.load(json_file).get(table, [])

            # Converter valores para float se possível
            for row in table_data:
                for col in row:
                    try:
                        row[col] = float(row[col])
                    except (ValueError, TypeError):
                        pass
            
            # Selecione apenas as colunas desejadas
            selected_data = [{col: row.get(col) for col in select_columns} for row in table_data]
            
            return selected_data
    except FileNotFoundError:
        print(f"Erro: O arquivo JSON '{table}' não foi encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON no arquivo '{table}'.")
        return None

def _where(data, column, condition, value):
    # Converta o valor para float se possível
    try:
        value = float(value)
    except (ValueError, TypeError):
        pass

    if condition == "=":
        return [entry for entry in data if entry.get(column) == value]
    elif condition == "<":
        return [entry for entry in data if entry.get(column) < value]
    elif condition == "<=":
        return [entry for entry in data if entry.get(column) <= value]
    elif condition == ">":
        return [entry for entry in data if entry.get(column) > value]
    elif condition == ">=":
        return [entry for entry in data if entry.get(column) >= value]
    else:
        print(f"Erro: Condição '{condition}' não suportada em _where.")
        return data

def _and_or(data, column1, condition1, value1, logical_operator, column2, condition2, value2):
    # Converta os valores para float se possível
    try:
        value1 = float(value1)
    except (ValueError, TypeError):
        pass

    try:
        value2 = float(value2)
    except (ValueError, TypeError):
        pass

    if logical_operator == "OU":
        data_condition1 = _where(data, column1, condition1, value1)
        data_condition2 = _where(data, column2, condition2, value2)
        return data_condition1 + data_condition2
    elif logical_operator == "E":
        data_condition1 = _where(data, column1, condition1, value1)
        return _where(data_condition1, column2, condition2, value2)
    else:
        print(f"Erro: Operador lógico '{logical_operator}' não suportado.")
        return data

json_query = "PEGAR Month, Average DE hurricanes ONDE Month = May OU Average > 2 ORDENE Average DECRESCENTE"
data = load_data()
result = parse_query(json_query, data)
print(result)
