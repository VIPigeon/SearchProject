
import ast
import inspect


def walk_tree(node, className=None, parent=None):
    if isinstance(node, list):
        for e in node:
            yield from walk_tree(e, parent=parent)
    else:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            args = ','.join([a.arg for a in node.args.args])
            docStr = ''
            # print(type(node.body[0]))
            if isinstance(node.body[0], ast.Expr) \
                          and isinstance(node.body[0].value, ast.Str):
                docStr = node.body[0].value.s
            # print(inspect.getmembers(node))
            yield {
                'type': 'func',
                'class_name': className,
                'name': node.name,
                'args': args,
                'doc_str': docStr,
                'line_no': node.lineno
            }
        if isinstance(node, ast.ClassDef):
            className=node.name
            docStr = ''
            if isinstance(node.body[0], ast.Expr) \
                          and isinstance(node.body[0].value, ast.Str):
                docStr = node.body[0].value.s
            yield {
                'type': 'class',
                'name': node.name,
                'doc_str': docStr,
                'line_no': node.lineno
            }
        if parent is None and isinstance(node, ast.Assign):
            for var in node.targets:
                if not isinstance(var, ast.Name):
                    continue
                yield {
                    'type': 'global_var',
                    'name': var.id,
                    'line_no': node.lineno
                }
        if hasattr(node, 'body'):
            for e in node.body:
                yield from walk_tree(e, className=className, parent=node)


def scan_py_file(filePath):
    with open(filePath, 'rt', encoding='utf-8') as f:
        content = f.read()
    # source = filePath.read_text()
    tree = compile(content, filePath, "exec", ast.PyCF_ONLY_AST)
    yield from walk_tree(tree.body)
    

if __name__ == '__main__':
    import sys
    iFile = sys.argv[1]
    for d in scan_py_file(iFile):
        print(d)
