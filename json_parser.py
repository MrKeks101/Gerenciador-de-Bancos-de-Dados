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

def _join_tables(table1, table2, condition):
    result = []
    
    for row1 in table1:
        for row2 in table2:
            if _check_join_condition(row1, row2, condition):
                # Criar uma cópia das linhas para evitar modificar as tabelas originais
                new_row1 = row1.copy()
                new_row2 = row2.copy()
                
                # Renomear colunas da segunda tabela para evitar duplicatas
                for col in new_row2.copy():
                    new_row2[f"{col}_right"] = new_row2.pop(col)

                # Combinar as duas linhas
                new_row = {**new_row1, **new_row2}

                # Remover colunas com valor None
                new_row = {key: value for key, value in new_row.items() if value is not None}

                result.append(new_row)
    
    # Renomear colunas removendo "_right" do final antes de retornar o resultado
    renamed_result = []
    for row in result:
        renamed_row = {key.rstrip('_right'): value for key, value in row.items()}
        renamed_result.append(renamed_row)

    return renamed_result


def _check_join_condition(row1, row2, condition):
    col1, _, col2 = condition
    col1 = col1.split('.')[-1]  # Extrai a segunda palavra após o ponto
    col2 = col2.split('.')[-1]  # Extrai a segunda palavra após o ponto

    return row1.get(col1) == row2.get(col2)

# Parse and execute a query on the loaded data.
def parse_query(query, data):

    query_list = query.split(' ')
    query_words = [element.replace(',', '') for element in query_list]

    if "PEGAR" in query_words and "DE" in query_words:
        select_index = query_words.index("PEGAR")
        from_index = query_words.index("DE")
        
        if select_index < from_index - 1:
            select_columns = [col.split('.')[-1] for col in query_words[select_index + 1:from_index]]
        else:
            select_columns = ["*"]
            
    elif "INSERIR" in query_words and "EM" in query_words:
        #print("INSERIR EM tabela (campo1, campo2, ....) VALORES (valor1, valor2, ...)")
        insert_index = query_words.index("INSERIR")
        into_index = query_words.index("EM")

        insert_values_index = into_index + 1
        into_table = query_words[into_index + 1]

        if "VALORES" in query_words:
            values_index = query_words.index("VALORES")
            columns = query_words[(insert_values_index + 1):values_index]
            values = query_words[values_index + 1:]

            # remove os parenteses da statement
            columns_clean = [s.replace('(', '').replace(')', '') for s in columns]
            values_clean = [s.replace('(', '').replace(')', '') for s in values]

            # insere
            _insert_into(into_table, columns_clean, values_clean)

            # retorna o registro inserido
            return (columns_clean, values_clean)
        else:
            raise ValueError("Cláusula 'VALORES' não encontrada na instrução INSERIR.")

    elif "ATUALIZAR" in query_words and "DEFINIR" in query_words:
        #print("ATUALIZAR tabela DEFINIR campo1 = valor1, campo2 = valor2 ONDE condicao")
        update_index = query_words.index("ATUALIZAR")
        set_index = query_words.index("DEFINIR")
        where_index = query_words.index("ONDE")

        update_table = query_words[update_index + 1]
        columns = query_words[set_index + 1:where_index]

        # Inicializar conjuntos para colunas e valores
        colunas = []
        valores = []

        # Iterar pelos dados de 3 em 3 elementos
        for i in range(0, len(columns), 3):
            coluna = columns[i]
            valor = columns[i + 2]

            colunas.append(coluna)
            valores.append(valor)
        
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

        # Chamar a função para atualizar os dados
        _update_set(update_table, colunas, valores, conditions)

        return "Dados atualizados!"

    elif "APAGAR" in query_words and "DE" in query_words:
        #print("APAGAR DE tabela ONDE condicao")
        delete_index = query_words.index("APAGAR")
        from_index = query_words.index("DE")
        where_index = query_words.index("ONDE")

        delete_table = query_words[delete_index + 2]
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

        # Chamar a função para apagar os dados
        _delete_from(delete_table, conditions)

        return f"Registros apagados da tabela '{delete_table}'."
    else:
        raise ValueError("Statement não reconhecida")

    if "DE" in query_words:
        from_index = query_words.index("DE")
        table = query_words[from_index + 1]

        query_result = _from(select_columns, table)
        from_data = query_result

        if "JUNCAO" in query_words and "USANDO" in query_words:
            join_index = query_words.index("JUNCAO")
            on_index = query_words.index("USANDO")
            join_table = query_words[join_index + 1]
            join_condition = query_words[on_index + 1:on_index + 4]

            join_table_data = _from(select_columns, join_table)

            # Realizar a junção com a tabela especificada e a condição de junção
            join_result = _join_tables(from_data, join_table_data, join_condition)
            
            # Atualizar o contexto da junção para ser utilizado como base na próxima parte do SELECT
            from_data = join_result
    
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
            
            # limpa o tabela.coluna
            column = column.split('.')[-1]

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

def _insert_into(table, columns, values):
    try:
        with open(os.path.join(data_directory, f"{table}.json"), 'r') as json_file:
            table_data = json.load(json_file).get(table, [])

            # Criar um novo registro
            new_record = {}
            for col, val in zip(columns, values):
                new_record[col] = val

            # Adicionar o novo registro aos dados existentes
            table_data.append(new_record)

            # Escrever os dados atualizados de volta ao arquivo JSON
            with open(os.path.join(data_directory, f"{table}.json"), 'w') as json_file:
                json.dump({table: table_data}, json_file, indent=2)

    except FileNotFoundError:
        print(f"Erro: O arquivo JSON '{table}' não foi encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON no arquivo '{table}'.")

def _update_set(table, columns, values, conditions):
    try:
        with open(os.path.join(data_directory, f"{table}.json"), 'r') as json_file:
            table_data = json.load(json_file).get(table, [])

            for row in table_data:
                # Verificar se a linha atende às condições
                if _check_conditions(row, conditions):
                    # Atualizar os valores nas colunas correspondentes
                    for col, val in zip(columns, values):
                        row[col] = val

            # Escrever os dados atualizados de volta ao arquivo JSON
            with open(os.path.join(data_directory, f"{table}.json"), 'w') as json_file:
                json.dump({table: table_data}, json_file, indent=2)

    except FileNotFoundError:
        print(f"Erro: O arquivo JSON '{table}' não foi encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON no arquivo '{table}'.")

def _check_conditions(row, conditions):
    for condition in conditions:
        column = condition[0]
        comparison_operator = condition[1]
        value = condition[2]

        # Verificar se as condições são atendidas
        if not _compare_values(row[column], comparison_operator, value):
            return False

    return True

def _compare_values(data_value, operator, condition_value):
    # Comparar valores de acordo com o operador
    if operator == '=':
        return data_value == condition_value
    elif operator == '<':
        return data_value < condition_value
    elif operator == '<=':
        return data_value <= condition_value
    elif operator == '>':
        return data_value > condition_value
    elif operator == '>=':
        return data_value >= condition_value
    else:
        print(f"Erro: Operador de comparação '{operator}' não suportado.")
        return False

def _delete_from(table, conditions):
    try:
        with open(os.path.join(data_directory, f"{table}.json"), 'r') as json_file:
            table_data = json.load(json_file).get(table, [])

            # Filtrar os dados que NÃO atendem às condições
            filtered_data = [row for row in table_data if not _check_conditions(row, conditions)]

            # Escrever os dados filtrados de volta ao arquivo JSON
            with open(os.path.join(data_directory, f"{table}.json"), 'w') as json_file:
                json.dump({table: filtered_data}, json_file, indent=2)

    except FileNotFoundError:
        print(f"Erro: O arquivo JSON '{table}' não foi encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON no arquivo '{table}'.")

#json_query = "PEGAR Month, Average DE hurricanes ONDE Average >= 0.1 E Average < 2 ORDENE Average DECRESCENTE"
#json_query = "INSERIR EM homes (Sell, List, Living, Rooms) VALORES (TESTE, TESTE, TESTE, TESTE)"
#json_query = "ATUALIZAR hurricanes DEFINIR Month = January, Average = 1.1 ONDE Average > 3.0"
#json_query = "APAGAR DE hurricanes ONDE Average = 0.0"
json_query = """"
                PEGAR actor.actor_id, actor.first_name, actor.last_name, film_actor.film_id 
                DE actor 
                JUNCAO film_actor USANDO actor.actor_id = film_actor.actor_id 
                ONDE actor.actor_id = 4
            """
data = load_data()
result = parse_query(json_query, data)

for r in result:
    print(r)
