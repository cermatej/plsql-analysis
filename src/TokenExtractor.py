from collections import defaultdict
from antlr_plsql import ast

class TokenExtractor:
    RES_KEY_TYPE = 'type'
    RES_KEY_METADATA = 'metadata'
    RES_KEY_COLUMNS = 'columns'
    RES_KEY_TABLES = 'tables'
    RES_KEY_FUNCS = 'funcs'
    RES_KEY_CONSTRAINT = 'constraint'
    RES_KEY_ALIASES = 'aliases'
    RES_KEY_VALUES = 'values'

    STATEMENT_TYPES = {
        ast.SelectStmt: 'select',
        ast.InsertStmt: 'insert',
        ast.AlterColumn: 'alter_column',
        ast.UpdateStmt: 'update',
        ast.AlterTable: 'alter_table',
        ast.CreateTable: 'create_table',
        ast.DropTable: 'drop_table'
    }

    RECOGNIZED_NODE_TYPES = {
        'Paren_column_list',
        'Column_list',
        'Dml_table_expression_clause'
    }

    METADATA_IGNORED = {
        ast.SelectStmt, ast.InsertStmt, ast.DeleteStmt, ast.UpdateStmt, ast.Identifier,
        ast.AlterColumn, ast.AlterTable, ast.Column
    }

    # todo dict res_key > list(attrs)?
    GENERAL_FIELDS_MAPPING = {
        'target_list': RES_KEY_COLUMNS,
        'where_clause': RES_KEY_COLUMNS,
        'order_by_clause': RES_KEY_COLUMNS,
        'group_by_clause': RES_KEY_COLUMNS,
        'having_clause': RES_KEY_COLUMNS,
        'cond': RES_KEY_COLUMNS,
        'columns': RES_KEY_COLUMNS,
        'column': RES_KEY_COLUMNS,
        'column_list': RES_KEY_COLUMNS,
        'from_clause': RES_KEY_TABLES,
        'table': RES_KEY_TABLES,
        'tableview_name': RES_KEY_TABLES,
        'values': RES_KEY_VALUES
    }

    # nodes that contain identifiers
    NODE_FIELDS_MAPPING = {
        ast.AliasExpr: {
            'alias': RES_KEY_ALIASES
        },
        ast.AlterTable: {
            'name': RES_KEY_TABLES
        },
        ast.Constraint: {
            'name': RES_KEY_CONSTRAINT
        },
        ast.CreateTable: {
            'name': RES_KEY_TABLES
        },
        ast.DropTable: {
            'name': RES_KEY_TABLES
        },
        ast.TableAliasExpr: {
            'alias': RES_KEY_ALIASES
        },
        ast.Update: {
            'expression': RES_KEY_COLUMNS
        }
    }

    # fields that needs to be saved immediately (does not contain Identifier)
    # there are some exceptions where the behaviour is ambiguous
    SPECIAL_FIELDS_MAPPING = {
        ast.Call: {
            'name': RES_KEY_FUNCS
        },
        ast.Constraint: {
            'type': 'constraint_type'
        }
    }

    IGNORED_ATTRS = {
        'op', 'direction', 'LEFT_PAREN', 'RIGHT_PAREN', 'COMMA', 'data_type'
    }

    def __init__(self) -> None:
        self.tokens = defaultdict(set)
        self.tree = None

    def analyse(self, query):
        #try:
        self.tree = ast.parse(query)
        # except KeyError:
        #     print('fail')

        if self.tree.body:
            body = self.tree.body[0]
            self.__get_stmt_type(body)
            self.__get_tokens(body)

    def __get_stmt_type(self, stmt_body):
        # if is one of known recognized statements, categorize the statement
        if isinstance(stmt_body, tuple(type for type in self.STATEMENT_TYPES.keys())):
            self.tokens[self.RES_KEY_TYPE] = self.STATEMENT_TYPES[type(stmt_body)]

    def __node_has_children(self, tree_node):
        return hasattr(tree_node, 'children') and tree_node.children

    def __get_save_key(self, attr, node_type):
        # if its generally recognized attribute
        if attr in self.GENERAL_FIELDS_MAPPING.keys():
            return self.GENERAL_FIELDS_MAPPING[attr]
        # if its recognized attribute for specific type
        if node_type in self.NODE_FIELDS_MAPPING.keys() and attr in self.NODE_FIELDS_MAPPING[node_type].keys():
            return self.NODE_FIELDS_MAPPING[node_type][attr]
        # not recognized by neither
        return None

    def __get_tokens(self, tree_node, save_key_prev=None):
        node_type = type(tree_node)

        # if list > iterate
        if isinstance(tree_node, list):
            for i in tree_node:
                self.__get_tokens(i, save_key_prev)
            return None

        # is identifier / literal value
        if isinstance(tree_node, (ast.Terminal, ast.Identifier)):
            # is a sql identifier
            if hasattr(tree_node.children[0], 'regular_id') and tree_node.children[0].regular_id:
                self.tokens[save_key_prev].add(tree_node.get_text())
            # is literal value
            else:
                self.tokens[self.RES_KEY_VALUES].add(self.__strip_quotes(tree_node.get_text()))
            return None

        # special cases, that does not contain Identifiers > contain the actual value directly
        if node_type in self.SPECIAL_FIELDS_MAPPING.keys():
            for attr, save_key in self.SPECIAL_FIELDS_MAPPING[node_type].items():
                attr_val = getattr(tree_node, attr)
                if attr_val is not None:
                    val = attr_val.get_text() if isinstance(attr_val, ast.Terminal) else attr_val
                    self.tokens[save_key].add(val)

        # collect metadata based on node type
        if node_type not in self.METADATA_IGNORED:
            self.tokens[self.RES_KEY_METADATA].add(f'uses_{node_type.__name__}')

        # iterate nodes
        for attr in self.__get_node_attrs(tree_node):
            save_key = self.__get_save_key(attr, node_type)
            attr_val = getattr(tree_node, attr)
            if save_key:
                self.__iter_attr(attr_val, save_key)
            else:
                self.__iter_attr(attr_val, save_key_prev)

    def __get_node_attrs(self, node):
        # iterate through non-empty children nodes
        attrs_ne = [a for a in node._fields if getattr(node, a) is not None]
        # that are not ignored
        return set(attrs_ne) - self.IGNORED_ATTRS

    def __strip_quotes(self, str):
        return str.strip('"').strip("'")

    def __iter_attr(self, attr_val, save_key):
        for node in self.__cast_list_if_not(attr_val):
            # only iterate through known nodes (prevent iteration to actual variables only)
            if self.__is_known_node(node): # todo move to __get_tokens method?
                self.__get_tokens(node, save_key)

    def __is_known_node(self, node):
        return isinstance(node, (ast.AliasNode, ast.Terminal, list)) or type(
            node).__name__ in self.RECOGNIZED_NODE_TYPES

    def __cast_list_if_not(self, child_attr):
        return [child_attr] if not isinstance(child_attr, list) else child_attr