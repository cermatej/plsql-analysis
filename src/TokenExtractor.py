from antlr_plsql import ast
from collections import defaultdict


class TokenExtractor:
    # todo link to RES_KEY attributes
    NODE_ATTRS = {
        'target_list': 'columns',
        'from_clause': 'tables',
        'table': 'tables',
        'where_clause': 'columns',
        'order_by_clause': 'columns',
        'group_by_clause': 'columns',
        'having_clause': 'columns'
    }

    RES_KEY_TYPE = 'type'
    RES_KEY_COLUMNS = 'columns'
    RES_KEY_TABLES = 'tables'
    RES_KEY_ALIASES = 'aliases'
    RES_KEY_FUNCS = 'funcs'

    STATEMENT_TYPES = {
        ast.SelectStmt: 'select',
        ast.InsertStmt: 'insert',
        ast.AlterTable: 'alter'
    }

    def __init__(self) -> None:
        self.tokens = defaultdict(set)
        self.tree = None

    def analyse(self, query):
        self.tree = ast.parse(query)
        body = self.tree.body[0]
        self.__get_stmt_type(body)
        self.__get_tokens(body)

    def __get_stmt_type(self, stmt_body):
        # if is one of known recognized statements, categorize the statement
        if isinstance(stmt_body, tuple(type for type in self.STATEMENT_TYPES.keys())):
            self.tokens[self.RES_KEY_TYPE] = self.STATEMENT_TYPES[type(stmt_body)]

    def __node_has_children(self, tree_node):
        return hasattr(tree_node, 'children') and tree_node.children

    def __get_tokens(self, tree_node):
        for attr, res_key in self.NODE_ATTRS.items():
            if hasattr(tree_node, attr) and bool(getattr(tree_node, attr)):
                child_attr = getattr(tree_node, attr)
                if type(child_attr) is not list: child_attr = [child_attr]  # cast to list if not
                for child in child_attr:
                    self.__save_token(child, res_key)

    def __save_token(self, node, res_key):
        # is alias expression
        if isinstance(node, ast.AliasExpr):
            self.tokens[res_key].add(node.expr.get_text())
            self.tokens[self.RES_KEY_ALIASES].add(node.alias.get_text())
        # is exact identifier
        elif isinstance(node, ast.Identifier):
            if hasattr(node.children[0], 'regular_id') and node.children[0].regular_id:
                self.tokens[res_key].add(node.get_text())
        elif isinstance(node, ast.Star):
            self.tokens[self.RES_KEY_COLUMNS].add(node.get_text())
        elif isinstance(node, ast.Call):
            for arg in node.args:
                self.__save_token(arg, res_key)
            self.tokens[self.RES_KEY_FUNCS].add(node.name)
        elif isinstance(node, ast.BinaryExpr):
            for n in [node.left, node.right]:
                self.__save_token(n, res_key)
        elif isinstance(node, ast.JoinExpr):
            for n in [node.left, node.right]:
                self.__save_token(n, res_key)
            self.__save_token(node.cond, self.RES_KEY_COLUMNS)
        elif isinstance(node, ast.OrderByExpr) or isinstance(node, ast.GroupBy):
            for expr in node.expr:
                self.__save_token(expr, res_key)
        elif isinstance(node, ast.SortBy):
            self.__save_token(node.expr, res_key)
