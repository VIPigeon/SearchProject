
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from scan_one import scan_py_file


DB_FILE = 'data.db'
SOURCES_FILE = 'sources.txt'
g_log = None


def create_tables(connection):
    cursor = connection.cursor()
    sql = """
        CREATE TABLE IF NOT EXISTS "files" (
            "id"    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            "fname" TEXT NOT NULL
        );
    """
    cursor.execute(sql)
    sql = """
        CREATE TABLE IF NOT EXISTS "global_vars" (
            "fname" INTEGER NOT NULL,
            "name"  TEXT NOT NULL,
            "line_no"   INTEGER NOT NULL,
            UNIQUE (fname, line_no) ON CONFLICT REPLACE
        );
    """
    cursor.execute(sql)
    sql = """
        CREATE TABLE IF NOT EXISTS "classes" (
            "fname" INTEGER NOT NULL,
            "name"  TEXT NOT NULL,
            "doc_string"    TEXT NOT NULL DEFAULT '',
            "line_no"   INTEGER NOT NULL,
            UNIQUE (fname, line_no) ON CONFLICT REPLACE
        );
    """
    cursor.execute(sql)
    sql = """
        CREATE TABLE IF NOT EXISTS "functions" (
            "fname" INTEGER NOT NULL,
            "name"  TEXT NOT NULL,
            "args"  TEXT NOT NULL DEFAULT '',
            "class_name"    TEXT NOT NULL DEFAULT '',
            "doc_string"    TEXT NOT NULL DEFAULT '',
            "line_no"   INTEGER,
            UNIQUE (fname, line_no) ON CONFLICT REPLACE
        );
    """
    cursor.execute(sql)

    connection.commit()


def get_fname_id(fname, connection):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    # print(fname)
    cursor.execute("""SELECT id
                    FROM files
                    WHERE fname=?;
                    """, (str(fname),))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(f"""
                INSERT INTO files(fname)
                VALUES (?)""", (str(fname),))
    connection.commit()

    cursor.execute("""SELECT id
                    FROM files
                    WHERE fname=?;
                    """, (str(fname),))
    res = cursor.fetchone()
    return res[0]


def add_func(fnameId, data, connection):
    cursor = connection.cursor()

    name = data['name']
    args = data['args']
    className = data['class_name']
    docStr = data['doc_str']
    lineNo = data['line_no']

    cursor.execute(f"""
             INSERT OR REPLACE into functions
             (name, args, class_name, fname, doc_string, line_no)
             VALUES (?, ?, ?, ?, ?, ?)""", (name, args, className, fnameId, docStr, lineNo))


def add_class(fnameId, data, connection):
    cursor = connection.cursor()

    name = data['name']
    docStr = data['doc_str']
    lineNo = data['line_no']

    cursor.execute(f"""
             INSERT OR REPLACE into classes
             (name, fname, doc_string, line_no)
             VALUES (?, ?, ?, ?)""", (name, fnameId, docStr, lineNo))


def add_global_var(fnameId, data, connection):
    cursor = connection.cursor()

    name = data['name']
    lineNo = data['line_no']

    cursor.execute(f"""
             INSERT OR REPLACE into global_vars
             (name, fname, line_no)
             VALUES (?, ?, ?)""", (name, fnameId, lineNo))


def process_py_file(fname, connection):
    fname = Path(fname).resolve()
    fnameId = get_fname_id(fname, connection)
    try:
        for d in scan_py_file(fname):
            # print(d)
            if d['type'] == 'func':
                add_func(fnameId, d, connection)
            elif d['type'] == 'class':
                add_class(fnameId, d, connection)
            elif d['type'] == 'global_var':
                add_global_var(fnameId, d, connection)
            else:
                raise Exception(f'Unsupported type: {d["type"]}')
    except Exception as e:
        g_log.warning(f'Не удалось обработать файл "{fname}", {e}')
        return
    connection.commit()


def process_dir(dirName, connection):
    for f in dirName.glob('**/*.py'):
        g_log.info(f'Обрабатываем файл "{f}"')
        process_py_file(f, connection)


def init_logger():
    logger = logging.getLogger('server')
    # вывод лога в файл
    logger.setLevel(logging.DEBUG)
    dt = datetime.now().isoformat().replace(':', '.')
    scriptName = f'scanner_{dt}.log'
    handler = logging.FileHandler(scriptName, mode='w', encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # вывод лога на экран
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


if __name__ == '__main__':
    g_log = init_logger()
    g_log.info(f'Открываем файл базы данных "{DB_FILE}"')
    connection = sqlite3.connect(DB_FILE)
    create_tables(connection)
    g_log.info(f'Читаем список источников из файла "{SOURCES_FILE}"')
    sources = Path(SOURCES_FILE).read_text().splitlines()
    for srcDir in sources:
        srcDir = srcDir.strip()
        if not srcDir or srcDir.startswith('#'):
            continue
        g_log.info(f'Начинаем обработку источника "{srcDir}"')
        process_dir(Path(srcDir), connection)
    connection.commit()
    connection.close()
