import sys

class ParseNode:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []

    def add(self, node):
        if node:
            self.children.append(node)

    def __repr__(self, level=0):
        ret = "  " * level + str(self.name)
        if self.value:
            ret += f": {self.value}"
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

    # استخدمنا advance عشان كودك كله مبني عليها
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
                node = ParseNode(curr_type, curr_val)
                self.advance()
                return node
        
        expected_desc = expected_val if expected_val else expected_type
        raise Exception(f"Syntax Error at {self.current_token[2]}:{self.current_token[3]} - Expected '{expected_desc}', found '{curr_val}'")

    def panic_mode(self):
        """Skips tokens until a SEMICOLON is found."""
        while self.current_token and self.current_token[1] != ';':
            self.advance()
        if self.current_token and self.current_token[1] == ';':
            self.advance() 

    # ---------------------------------------------------------
    # PART 1: Dispatcher (Routing Logic) - شغلك أنت
    # ---------------------------------------------------------
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
            raise Exception(f"Syntax Error - Unexpected start of statement: '{val}'")
        
        node.add(self.match("SEMICOLON", ";"))
        return node

    # ---------------------------------------------------------
    # PART 2: DDL (CREATE) - شغلك أنت
    # ---------------------------------------------------------
    def parse_create_stmt(self):
        node = ParseNode("CreateStmt")
        node.add(self.match("KEYWORD", "CREATE"))
        node.add(self.match("KEYWORD", "TABLE"))
        node.add(self.match("IDENTIFIER"))
        node.add(self.match("LPAREN"))
        
        # Parse ColumnList
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
            raise Exception(f"Expected Data Type (INT, FLOAT, TEXT)")
        return col

    # ---------------------------------------------------------
    # PART 3: DML (INSERT) - شغلك أنت
    # ---------------------------------------------------------
    def parse_insert_stmt(self):
        node = ParseNode("InsertStmt")
        node.add(self.match("KEYWORD", "INSERT"))
        node.add(self.match("KEYWORD", "INTO"))
        node.add(self.match("IDENTIFIER"))
        node.add(self.match("KEYWORD", "VALUES"))
        node.add(self.match("LPAREN"))
        
        # parse ValueList
        node.add(self.parse_value())
        while self.current_token and self.current_token[1] == ',':
            self.advance() 
            node.add(self.parse_value())
            
        node.add(self.match("RPAREN"))
        return node

    def parse_value(self):
        if self.current_token[0] in ["INTEGER", "FLOAT", "STRING"]:
            node = ParseNode("Value", self.current_token[1])
            self.advance()
            return node
        raise Exception(f"Expected Value (Integer, Float, or String)")

    # ---------------------------------------------------------
    # Placeholders - مكان شغل زمايلك
    # ---------------------------------------------------------
    def parse_select_stmt(self):
        pass

    def parse_update_stmt(self):
        pass

    def parse_delete_stmt(self):
        pass

    # ---------------------------------------------------------
    # Main Branch Logic - ده الكود اللي كان موجود في الـ Main
    # ---------------------------------------------------------
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