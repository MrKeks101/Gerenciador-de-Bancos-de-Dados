# Gerenciador-de-Bancos-de-Dados
O trabalho consiste no desenvolvimento de uma ferramenta de gerenciamento de bancos de dados, baseada em ingestão de dados de fontes externas e operações e consultas processadas nas tabelas. A ferramenta deverá utilizar uma linguagem de consulta e operações baseada em semântica própria, tendo como base algum dialeto local brasileiro.

Importação de dados:
    
    CSV e Importação de bancos de dados existentes
    
    Bancos de Dados Existentes
    conexão a um banco de dados existente (MySQL ou PostgreSQL)
    seleção do banco de dados
    seleção das tabelas para importação
    
    CSV
    selecionar um diretório onde estarão os arquivos de dados em formato CSV
    carregar um arquivo para cada tabela, com o nome do arquivo dando o nome à tabela

    Gerenciamento e manipulação de dados


    permitir a consulta aos dados, em formato SQL, com as seguintes cláusulas possíveis:

    -projeção (lista de campos ou todos)
    -filtros (semelhante a where)
    -ordenação (semelhante a order by)


    os filtros e ordenação poderão ser feitos por um ou dois campos, com modificadores lógicos semelhantes a AND e OR
    o gerenciador deverá ser capaz de implementar inner joins, permitindo uma sintaxe semelhante a USING e ON.

    deverão ser implementados os comandos de manipulação semelhantes a INSERT, UPDATE e DELETE


Os testes deverão ser feitos com a base de dados de exemplo Employee, disponível em https://github.com/datacharmer/test_db


