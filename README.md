# plsql-analysis
###About
##### Description
##### Motivation, use cases
##### Achitecture plan
##### Elasticsearch
##### Parser antlr-tree, how it works
##### Crawler
##### Api reference
##### Caveats
* optimizing parser
* cleaning crawler

### Usage
##### Discover example searches
`"on delete cascade"`
##### Dashboards
* main dashboard (controls, screenshots)



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

#### Problematic queries
* column name in CHECK missing completely from the tree
`ALTER TABLE suppliers ADD CONSTRAINT check_supplier_name   CHECK (supplier_name IN ('IBM', 'Microsoft', 'NVIDIA'))`