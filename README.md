# psql-analysis

### Developer notes
#### ANTLR notes
https://github.com/antlr/antlr4/blob/master/doc/python-target.md

#### ANTLR plsql project
https://github.com/datacamp/antlr-plsql

#### tokenizer notes/todos

first only support explictitly mentioned tokens

todo
* having clause 
* select into clause
* groupby + agg functions
* aliased columns
* subqueries
* case when clause
* multiple tables - selecting column without defining table

#### Missing classes 
* class AlterTable(AliasNode):
* class AddConstraints(AliasNode):
* class AlterColumn(AliasNode):

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
* class Reference(AliasNode):
* class CreateTable(AliasNode):
* class DropConstraints(AliasNode):
* class DropConstraint(AliasNode):
* class DropTable(AliasNode):
* class Constraint(AliasNode):
* class UpdateStmt(AliasNode):
* class Update(AliasNode):
* class DeleteStmt(AliasNode):
* class Transformer(BaseNodeTransformer):
* class AstVisitor(BaseAstVisitor):
 