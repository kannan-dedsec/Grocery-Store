import sqlite3 as sq
import json
from collections import defaultdict
from queue import Queue
from utilities import CommonUtil
import ConfigurationConstants

ALTERATIONS = "alterations"
TABLE_NAME = "table_name"
COLUMNS = "columns"
TABLES = "TABLES"
CONSTRAINTS = "CONSTRAINTS"
TYPE = "type"


def createConnection():
    return sq.connect(ConfigurationConstants.DATABASE_FILE)


def getData(query):
    connection = createConnection()
    try:
        CommonUtil.getLogger().info(f"Execution Query {query}")
        cur = connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        cur.close()
        return data
    except sq.Error as error:
        CommonUtil.getLogger().error(error)
    finally:
        closeConnection(connection)


def executeQuery(query):
    CommonUtil.getLogger().info(f"Execution Query {query}")
    connection = createConnection()
    cursor = connection.cursor()
    try:
        cursor.executescript(f"{ConfigurationConstants.PRAGMA_QUERY}{query}")
        cursor.close()
    except sq.Error as error:
        CommonUtil.getLogger().error(error)
        return False
    except Exception as error:
        CommonUtil.getLogger().error(error)
        return False
    finally:
        closeConnection(connection)
    return True


def closeConnection(connection):
    connection.commit()
    connection.close()
    return True

def reinitializeDB():
    data = json.load(open(ConfigurationConstants.FILE_PATH_TO_TABLES_JSON))
    query = ""
    tables = drop_tables_in_order(data)
    mainTables = data["tables"].keys()
    for tab in mainTables:
        if tab not in tables:
            tables.append(tab)
    for table_name in tables:
        query += ConfigurationConstants.DROP_TABLE_TEMPLATE.substitute({'table_name': table_name})
    executeQuery(query)
    query = getDefaultSqlQuery(data)
    CommonUtil.getLogger().info(query)
    executeQuery(query)
    query = ""
    for unit in ConfigurationConstants.DEFAULT_UNITS:
        query += ConfigurationConstants.ADD_UNIT_TEMPLATE.substitute(
            {'unit_id': CommonUtil.generateRandomID(), 'unit_name': unit})
    CommonUtil.getLogger().info(query)
    executeQuery(query)
    query = ""
    for unit in ConfigurationConstants.DEFAULT_CATEGORIES:
        query += ConfigurationConstants.ADD_CATEGORY_TEMPLATE.substitute(
            {'category_id': CommonUtil.generateRandomID(), 'category_name': unit})
    CommonUtil.getLogger().info(query)
    executeQuery(query)

    return True

def generate_table_sql(table_name, columns_data, primary_key, foreign_keys):
    sql_columns = []
    for column_name, column_data in columns_data.items():
        sql_columns.append(f"{column_name} {column_data['type']} {column_data['constraints']}")
    if primary_key:
        sql_columns.append(f"PRIMARY KEY ({', '.join(primary_key)})")
    if foreign_keys:
        for fk in foreign_keys:
            fk_columns = ', '.join(fk['columns'])
            references_table = fk['references']['table']
            references_columns = ', '.join(fk['references']['columns'])
            on_delete = fk["on_delete"]
            sql_columns.append(
                f"FOREIGN KEY ({fk_columns}) REFERENCES {references_table}({references_columns}) ON DELETE {on_delete}")
    return f"CREATE TABLE {table_name} ({', '.join(sql_columns)});"


def getDefaultSqlQuery(data):
    sql_script = ""
    for table_name, table_data in data.get("tables", {}).items():
        columns_data = table_data.get("columns", {})
        primary_key = table_data.get("primary_key", [])
        foreign_keys = table_data.get("foreign_keys", [])
        table_sql = generate_table_sql(table_name, columns_data, primary_key, foreign_keys)
        sql_script += table_sql + "\n"
    return sql_script


def drop_tables_in_order(data):
    table_dependencies = defaultdict(list)
    for table_name, table_info in data["tables"].items():
        for foreign_key in table_info.get("foreign_keys", []):
            reference_table = foreign_key["references"]["table"]
            table_dependencies[reference_table].append(table_name)
    for table_name in data["tables"]:
        if table_name not in table_dependencies:
            table_dependencies[table_name] = []
    order_to_drop_tables = []
    queue = Queue()
    for table_name in data["tables"]:
        if not table_dependencies[table_name]:
            queue.put(table_name)
    while not queue.empty():
        table_name = queue.get()
        order_to_drop_tables.append(table_name)
        for dependent_table in table_dependencies[table_name]:
            table_dependencies[dependent_table].remove(table_name)
            if not table_dependencies[dependent_table]:
                queue.put(dependent_table)
    return order_to_drop_tables
