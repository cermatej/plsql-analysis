# plsql-analysis

### Submodule init
To fetch project submodules, you have to run these commands
```bash
git submodule init
git submodule update
```

### Developer notes

##### ANTLR notes
https://github.com/antlr/antlr4/blob/master/doc/python-target.md

##### ANTLR grammars
https://github.com/antlr/grammars-v4
 
##### ANTLR plsql project
https://github.com/datacamp/antlr-plsql

##### Building ANTLR grammar
https://www.antlr.org/download/antlr-4.8-complete.jar
https://tomassetti.me/antlr-mega-tutorial/
```
java -jar antlr-4.8-complete.jar -Dlanguage=Python3 -o antlr_py/ -visitor plsql.g4
```

##### ANTLR AST
https://github.com/datacamp/antlr-ast

### TODOS
* multiple tables - selecting column without defining table ???
* generate the grammar on demand

#### Missing classes 
* class AlterColumn(AliasNode):
* class Reference(AliasNode):

* class Union(AliasNode):
* class TableAliasExpr(AliasNode):
* class UnaryExpr(AliasNode):
* class Cast(AliasNode):
* class OverClause(AliasNode):
* class Case(AliasNode):
* class CaseWhen(AliasNode):
* class PartitionBy(AliasNode):
* class RenameColumn(AliasNode):
* class Column(AliasNode):
* class AddColumns(AliasNode):
* class DropColumn(AliasNode):
* class CreateTable(AliasNode):
* class DropConstraints(AliasNode):
* class DropConstraint(AliasNode):
* class DropTable(AliasNode):
* class UpdateStmt(AliasNode):
* class Update(AliasNode):
* class DeleteStmt(AliasNode):
* class Transformer(BaseNodeTransformer):
* class AstVisitor(BaseAstVisitor):
 