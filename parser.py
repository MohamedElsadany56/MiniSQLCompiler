class ParseNode:
    def __init__(self, name, value=None, token=None):
        self.name = name
        self.value = value
        self.children = []
        # Semantic annotations
        self.data_type = None  # For type annotation
        self.symbol_ref = None  # Reference to symbol table entry
        # Token tracking for error reporting
        self.token = token  # Store original token (type, value, line, col)
        self.line = token[2] if token and len(token) > 2 else 0
        self.col = token[3] if token and len(token) > 3 else 0

    def add(self, node):
        if node:
            self.children.append(node)

    def __repr__(self, level=0):
        ret = "  " * level + str(self.name)
        if self.value:
            ret += f": {self.value}"
        if self.data_type:
            ret += f" [Type: {self.data_type}]"
        ret += "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
        self.errors = []

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match(self, expected_type, expected_val=None):
        """Consumes token if it matches type and optional value."""
        if not self.current_token:
            raise Exception(f"Unexpected End of Input. Expected {expected_type}")
        
        curr_type = self.current_token[0]
        curr_val = self.current_token[1]

        if curr_type == expected_type:
            if expected_val is None or curr_val == expected_val:
                node = ParseNode(curr_type, curr_val, self.current_token)
                self.advance()
                return node
        
        expected_desc = expected_val if expected_val else expected_type
        raise Exception(f"Syntax Error at {self.current_token[2]}:{self.current_token[3]} - Expected '{expected_desc}', found '{curr_val}'")

    def panic_mode(self):
        """Skips tokens until a SEMICOLON is found."""
        while self.current_token and self.current_token[1] != ';':
            self.advance()
        if self.current_token and self.current_token[1] == ';':
            self.advance() # Consume the semicolon to reset

    # CFG implelmetation 

    # Query -> Statement | Statement Query
    def parse_query(self):
        root = ParseNode("Query")
        while self.current_token:
            try:
                root.add(self.parse_statement())
            except Exception as e:
                self.errors.append(str(e))
                self.panic_mode()
        return root

    # Statement -> CreateStmt SEMICOLON | InsertStmt SEMICOLON ...
    def parse_statement(self):
        if not self.current_token: return None
        val = self.current_token[1]
        
        node = ParseNode("Statement")
        
        if val == "CREATE":
            node.add(self.parse_create_stmt())
        elif val == "INSERT":
            node.add(self.parse_insert_stmt())
        elif val == "SELECT":
            node.add(self.parse_select_stmt())
        elif val == "UPDATE":
            node.add(self.parse_update_stmt())
        elif val == "DELETE":
            node.add(self.parse_delete_stmt())
        else:
            raise Exception(f"Syntax Error at {self.current_token[2]}:{self.current_token[3]} - Unexpected start of statement: '{val}'")
        
        # The SEMICOLON belongs to the Statement rule
        node.add(self.match("SEMICOLON", ";"))
        return node

    # CreateStmt -> CREATE TABLE IDENTIFIER ( ColumnList )
    def parse_create_stmt(self):
        node = ParseNode("CreateStmt")
        node.add(self.match("KEYWORD", "CREATE"))
        node.add(self.match("KEYWORD", "TABLE"))
        node.add(self.match("IDENTIFIER"))
        node.add(self.match("LPAREN"))
        
        # Parse ColumnList manually
        node.add(self.parse_column_def())
        while self.current_token and self.current_token[1] == ',':
            self.advance() # skip comma
            node.add(self.parse_column_def())
            
        node.add(self.match("RPAREN"))
        return node

    def parse_column_def(self):
        col = ParseNode("ColumnDef")
        col.add(self.match("IDENTIFIER"))
        
        if self.current_token[1] in ["INT", "FLOAT", "TEXT"]:
            col.add(self.match("KEYWORD"))
        else:
            raise Exception(f"Expected Data Type (INT, FLOAT, TEXT) at {self.current_token[2]}:{self.current_token[3]}")
        return col

    # InsertStmt -> INSERT INTO IDENTIFIER VALUES ( ValueList )
    def parse_insert_stmt(self):
        node = ParseNode("InsertStmt")
        node.add(self.match("KEYWORD", "INSERT"))
        node.add(self.match("KEYWORD", "INTO"))
        node.add(self.match("IDENTIFIER"))
        node.add(self.match("KEYWORD", "VALUES"))
        node.add(self.match("LPAREN"))
        
        # parse ValueList manually
        node.add(self.parse_value())
        while self.current_token and self.current_token[1] == ',':
            self.advance() # skip comma
            node.add(self.parse_value())
            
        node.add(self.match("RPAREN"))
        return node

    #SelectStmt -> SELECT SelectList FROM IDENTIFIER WhereClause
    def parse_select_stmt(self):
        node = ParseNode("SelectStmt")
        node.add(self.match("KEYWORD", "SELECT"))
        
        # SelectList rule implementation
        if self.current_token[1] == '*':
             node.add(self.match("OPERATOR", "*"))
        else:
            node.add(self.match("IDENTIFIER"))
            while self.current_token and self.current_token[1] == ',':
                self.advance()
                node.add(self.match("IDENTIFIER"))
                
        node.add(self.match("KEYWORD", "FROM"))
        node.add(self.match("IDENTIFIER"))
        
        if self.current_token and self.current_token[1] == "WHERE":
            node.add(self.parse_where_clause())
            
        return node

    # UpdateStmt -> UPDATE IDENTIFIER SET IDENTIFIER = Value WhereClause
    def parse_update_stmt(self):
        node = ParseNode("UpdateStmt")
        node.add(self.match("KEYWORD", "UPDATE"))
        node.add(self.match("IDENTIFIER"))
        node.add(self.match("KEYWORD", "SET"))
        node.add(self.match("IDENTIFIER"))
        node.add(self.match("OPERATOR", "="))
        node.add(self.parse_value())
        if self.current_token and self.current_token[1] == "WHERE":
            node.add(self.parse_where_clause())
        return node

    # DeleteStmt -> DELETE FROM IDENTIFIER WhereClause
    def parse_delete_stmt(self):
        node = ParseNode("DeleteStmt")
        node.add(self.match("KEYWORD", "DELETE"))
        node.add(self.match("KEYWORD", "FROM"))
        node.add(self.match("IDENTIFIER"))
        if self.current_token and self.current_token[1] == "WHERE":
            node.add(self.parse_where_clause())
        return node

    # WhereClause -> WHERE Condition
    def parse_where_clause(self):
        node = ParseNode("WhereClause")
        node.add(self.match("KEYWORD", "WHERE"))
        node.add(self.parse_condition())
        return node

    #  Condition Logic (Boolean Logic for WhereClause) 

    def parse_condition(self):
        node = ParseNode("Condition")
        node.add(self.parse_term())
        while self.current_token and self.current_token[1] == "OR":
            node.add(self.match("KEYWORD", "OR"))
            node.add(self.parse_term())
        return node

    def parse_term(self):
        node = ParseNode("Term")
        node.add(self.parse_factor())
        while self.current_token and self.current_token[1] == "AND":
            node.add(self.match("KEYWORD", "AND"))
            node.add(self.parse_factor())
        return node

    def parse_factor(self):
        if self.current_token[1] == "NOT":
            node = ParseNode("Factor")
            node.add(self.match("KEYWORD", "NOT"))
            node.add(self.parse_factor())
            return node
        elif self.current_token[1] == "(":
            node = ParseNode("Factor")
            self.match("LPAREN")
            node.add(self.parse_condition())
            self.match("RPAREN")
            return node
        else:
            return self.parse_comparison()

    def parse_comparison(self):
        node = ParseNode("Comparison")
        # Left Operand
        node.add(self.parse_operand())
        
        # Operator
        node.add(self.match("OPERATOR"))
        
        # Right Operand
        node.add(self.parse_operand())
        return node

    def parse_operand(self):
        if self.current_token[0] in ["IDENTIFIER", "INTEGER", "FLOAT", "STRING"]:
             node = ParseNode("Operand", self.current_token[1], self.current_token)
             self.advance()
             return node
        
        raise Exception(f"Expected Expression at {self.current_token[2]}:{self.current_token[3]}")

    def parse_value(self):
        if self.current_token[0] in ["INTEGER", "FLOAT", "STRING"]:
            node = ParseNode("Value", self.current_token[1], self.current_token)
            self.advance()
            return node
        raise Exception(f"Expected Value at {self.current_token[2]}:{self.current_token[3]}")