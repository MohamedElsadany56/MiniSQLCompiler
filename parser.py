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

    def next(self):
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
                self.next()
                return node
        
        expected_desc = expected_val if expected_val else expected_type
        raise Exception(f"Syntax Error at {self.current_token[2]}:{self.current_token[3]} - Expected '{expected_desc}', found '{curr_val}'")

    def panic_mode(self):
        """Skips tokens until a SEMICOLON is found."""
        while self.current_token and self.current_token[1] != ';':
            self.next()
        if self.current_token and self.current_token[1] == ';':
            self.next() # Consume the semicolon to reset

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