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
        
        if select_index < from_index - 1:
            select_columns = [col for col in query_words[select_index + 1:from_index]]
        else:
            select_columns = ["*"]
    
    if "DE" in query_words:
        from_index = query_words.index("DE")
        table = query_words[from_index + 1]

        query_result = _from(select_columns, table)
        from_data = query_result
    
    if "ONDE" in query_words:
        where_index = query_words.index("ONDE")
        conditions = []

        i = where_index + 1
        while i < len(query_words):
            if query_words[i] in ["E", "OU"]:
                logical_operator = query_words[i]
                i += 1
            else:
                logical_operator = None

            column = query_words[i]
            condition = query_words[i + 1]
            value = query_words[i + 2]

            if logical_operator:
                conditions.append(logical_operator)

            conditions.append((column, condition, value))

            i += 3

        result = _where(from_data, conditions)
    else:
        result = from_data

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
            
            if "*" in select_columns:
                # Se "*" estiver presente, selecione todas as colunas disponíveis
                return table_data

            # Selecione apenas as colunas desejadas
            selected_data = [{col: row.get(col) for col in select_columns} for row in table_data]
            
            return selected_data
    except FileNotFoundError:
        print(f"Erro: O arquivo JSON '{table}' não foi encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON no arquivo '{table}'.")
        return None

def _where(data, conditions):
    filtered_data = []

    i = 0
    tuple_count = 0
    tuples = []
    logical_op_count = 0
    logicals = []
    or_count = 1 # primeira condição
    and_count = 0

    while i < len(conditions):
        if isinstance(conditions[i], tuple):
            tuple_count += 1
            tuples.append(conditions[i])
        else:
            logical_op_count += 1
            logicals.append(conditions[i])
            if conditions[i] == "OU":
                or_count += 1
            else:
                and_count += 1
        i += 1

    # OU aparece antes do E
    logicals.sort(reverse=True)

    i = 0
    while i < tuple_count:
        column = tuples[i][0]
        condition = tuples[i][1]
        value = tuples[i][2]

        if or_count > 0: # acumula os dados
            filtered_data += _apply_condition(data, column, condition, value)
            or_count -= 1
        elif and_count > 0: # restringe
            filtered_data = _apply_condition(filtered_data, column, condition, value)
            and_count -= 1

        i += 1

    return filtered_data

def _apply_condition(data, column, condition, value):
    # Convert value to float if possible
    try:
        value = float(value)
    except (ValueError, TypeError):
        pass

    if condition == '=':
        return [row for row in data if row.get(column) == value]
    elif condition == '<':
        return [row for row in data if row.get(column) < value]
    elif condition == '<=':
        return [row for row in data if row.get(column) <= value]
    elif condition == '>':
        return [row for row in data if row.get(column) > value]
    elif condition == '>=':
        return [row for row in data if row.get(column) >= value]
    else:
        print(f"Erro: Operador de comparação '{condition}' não suportado.")
        return data

json_query = "PEGAR Month, Average DE hurricanes ONDE Average >= 0.1 E Average < 2 ORDENE Average DECRESCENTE"
data = load_data()
result = parse_query(json_query, data)
print(result)
