
import sqlite3


DATA_FILE = 'data.db'


def function(name1, args1, class_name1, doc_string1):
    argsSubstrings = [f'%{arg}%' for arg in args1.split(',')]
    argsFormat = ' and '.join(['args LIKE ?' for _ in range(len(argsSubstrings))])
    # print(argsSubstrings)
    # print(argsFormat)
    sql = f"""
            SELECT
                line_no,
                files.fname
            FROM
                functions
            INNER JOIN files
                ON files.id = functions.fname
            WHERE name LIKE ?
            and ({argsFormat})
            and class_name LIKE ?
            and doc_string LIKE ?
        """
    result = cur.execute(sql, (f'%{name1}%', *argsSubstrings,
                               f'%{class_name1}%', f'%{doc_string1}%')).fetchall()
    return result


def klass(name1, doc_string1):
    sql = """
        SELECT
            line_no,
            files.fname
        FROM
            classes
        INNER JOIN files
            ON files.id = classes.fname
        WHERE name LIKE ?
        and doc_string LIKE ?
    """
    result = cur.execute(sql, (f'%{name1}%', f'%{doc_string1}%')).fetchall()
    return result


def global_vars(name1):
    sql = """
        SELECT
            line_no,
            files.fname
        FROM
            global_vars
        INNER JOIN files
            ON files.id = global_vars.fname
        WHERE name LIKE ?
    """
    result = cur.execute(sql, (f'%{name1}%',)).fetchall()
    return result


def start(type1, name1, args1, class_name1, doc_string1):
    # функция
    if type1 == 'f':
        # print('f')
        return function(name1, args1, class_name1, doc_string1)

    # класс
    if type1 == 'c':
        # print('c')
        return klass(name1, doc_string1)

    # print('gv')
    # глобальная переменная (type1 == 'gv')
    return global_vars(name1)


con = sqlite3.connect(DATA_FILE)
cur = con.cursor()
