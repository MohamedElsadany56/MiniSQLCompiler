# Phase 03: Semantic Analyzer for Mini SQL Compiler

class SymbolTable:
    """
    Hierarchical symbol table to store metadata about tables and columns.
    Each table entry contains:
    - Table name
    - Columns: list of (column_name, data_type) tuples
    - Line and column where defined
    """
    
    def __init__(self):
        self.tables = {}  # table_name -> {'columns': [(name, type)], 'line': int, 'col': int}
    
    def add_table(self, table_name, columns, line, col):
        """Register a new table with its column definitions."""
        if table_name in self.tables:
            return False  # Table already exists
        
        self.tables[table_name] = {
            'columns': columns,  # List of (column_name, data_type) tuples
            'line': line,
            'col': col
        }
        return True
    
    def table_exists(self, table_name):
        """Check if a table has been declared."""
        return table_name in self.tables
    
    def get_table(self, table_name):
        """Retrieve table metadata."""
        return self.tables.get(table_name, None)
    
    def get_column_type(self, table_name, column_name):
        """Get the data type of a specific column in a table."""
        if table_name not in self.tables:
            return None
        
        for col_name, col_type in self.tables[table_name]['columns']:
            if col_name == column_name:
                return col_type
        return None
    
    def column_exists(self, table_name, column_name):
        """Verify that a column exists within a table."""
        if table_name not in self.tables:
            return False
        
        for col_name, _ in self.tables[table_name]['columns']:
            if col_name == column_name:
                return True
        return False
    
    def get_column_count(self, table_name):
        """Get the number of columns in a table."""
        if table_name not in self.tables:
            return 0
        return len(self.tables[table_name]['columns'])
    
    def dump(self):
        """Pretty-print the symbol table contents."""
        output = []
        output.append("\n" + "_"*60)
        output.append("SYMBOL TABLE DUMP")
        output.append("_"*60)
        
        if not self.tables:
            output.append("No tables defined.")
        else:
            for table_name, table_info in self.tables.items():
                output.append(f"\nTable: {table_name}")
                output.append(f"  Defined at: Line {table_info['line']}, Column {table_info['col']}")
                output.append("  Columns:")
                for col_name, col_type in table_info['columns']:
                    output.append(f"    - {col_name}: {col_type}")
        
        output.append("_"*60)
        return "\n".join(output)


class SemanticAnalyzer:
    """
    Semantic Analyzer that consumes the parse tree from Phase 02
    and performs semantic checks including:
    - Identifier verification (table/column existence, redeclaration)
    - Type checking (valid types, INSERT consistency, WHERE compatibility)
    """
    
    def __init__(self, parse_tree):
        self.parse_tree = parse_tree
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_table = None  # Track current table context
    
    def analyze(self):
        """Main entry point for semantic analysis."""
        self._traverse_tree(self.parse_tree)
        return len(self.errors) == 0
    
    def _traverse_tree(self, node):
        """Recursively traverse the parse tree and analyze statements."""
        if not node:
            return
        
        # Route to appropriate handler based on node type
        if node.name == "Statement":
            self._analyze_statement(node)
        
        # Continue traversing children
        for child in node.children:
            self._traverse_tree(child)
    
    def _analyze_statement(self, node):
        """Route statement to appropriate semantic check handler."""
        if not node.children:
            return
        
        stmt_type = node.children[0].name
        
        if stmt_type == "CreateStmt":
            self._analyze_create_table(node.children[0])
        elif stmt_type == "InsertStmt":
            self._analyze_insert(node.children[0])
        elif stmt_type == "SelectStmt":
            self._analyze_select(node.children[0])
        elif stmt_type == "UpdateStmt":
            self._analyze_update(node.children[0])
        elif stmt_type == "DeleteStmt":
            self._analyze_delete(node.children[0])
    
    def _analyze_create_table(self, node):
        """
        Analyze CREATE TABLE statement:
        - Check for table redeclaration
        - Validate data types (INT, FLOAT, TEXT)
        - Build symbol table entry
        """
        # Extract table name (3rd child: CREATE TABLE [name])
        table_name_node = node.children[2]
        table_name = table_name_node.value
        line = self._get_line(table_name_node)
        col = self._get_col(table_name_node)
        
        # Check for redeclaration
        if self.symbol_table.table_exists(table_name):
            existing = self.symbol_table.get_table(table_name)
            self._report_error(
                f"Semantic Error: Table '{table_name}' already declared at line {existing['line']}",
                line, col
            )
            return
        
        # Extract column definitions
        columns = []
        for child in node.children:
            if child.name == "ColumnDef":
                col_name_node = child.children[0]
                col_type_node = child.children[1]
                
                col_name = col_name_node.value
                col_type = col_type_node.value
                
                # Validate data type (should already be validated in parser, but double-check)
                if col_type not in ["INT", "FLOAT", "TEXT"]:
                    self._report_error(
                        f"Semantic Error: Invalid data type '{col_type}'. Expected INT, FLOAT, or TEXT",
                        self._get_line(col_type_node), self._get_col(col_type_node)
                    )
                    continue
                
                columns.append((col_name, col_type))
                
                # Annotate column name node with type
                col_name_node.data_type = col_type
        
        # Add table to symbol table
        if columns:
            self.symbol_table.add_table(table_name, columns, line, col)
            table_name_node.symbol_ref = table_name
    
    def _analyze_insert(self, node):
        """
        Analyze INSERT INTO statement:
        - Verify table exists
        - Check value count matches column count
        - Verify type compatibility for each value
        """
        # Extract table name (3rd child: INSERT INTO [name])
        table_name_node = node.children[2]
        table_name = table_name_node.value
        line = self._get_line(table_name_node)
        col = self._get_col(table_name_node)
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self._report_error(
                f"Semantic Error: Table '{table_name}' not found. Ensure table is created before insertion",
                line, col
            )
            return
        
        # Get table metadata
        table_info = self.symbol_table.get_table(table_name)
        expected_columns = table_info['columns']
        
        # Extract values from INSERT statement
        values = []
        for child in node.children:
            if child.name == "Value":
                values.append(child)
        
        # Check value count
        if len(values) != len(expected_columns):
            self._report_error(
                f"Semantic Error: Column count mismatch. Table '{table_name}' has {len(expected_columns)} columns, but {len(values)} values provided",
                line, col
            )
            return
        
        # Type checking for each value
        for i, (value_node, (col_name, col_type)) in enumerate(zip(values, expected_columns)):
            value_type = self._infer_type(value_node)
            
            if not self._types_compatible(col_type, value_type):
                self._report_error(
                    f"Semantic Error: Type mismatch at line {self._get_line(value_node)}, position {self._get_col(value_node)}. "
                    f"Column '{col_name}' is defined as {col_type}, but a {value_type} literal was provided for insertion",
                    self._get_line(value_node), self._get_col(value_node)
                )
            else:
                # Annotate value with expected type
                value_node.data_type = col_type
        
        # Annotate table reference
        table_name_node.symbol_ref = table_name
    
    def _analyze_select(self, node):
        """
        Analyze SELECT statement:
        - Verify table exists
        - Verify columns exist (if not SELECT *)
        - Check WHERE clause for type compatibility
        """
        # Find table name (after FROM keyword)
        table_name_node = None
        from_found = False
        for child in node.children:
            if child.name == "KEYWORD" and child.value == "FROM":
                from_found = True
            elif from_found and child.name == "IDENTIFIER":
                table_name_node = child
                break
        
        if not table_name_node:
            return
        
        table_name = table_name_node.value
        line = self._get_line(table_name_node)
        col = self._get_col(table_name_node)
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self._report_error(
                f"Semantic Error: Table '{table_name}' not found",
                line, col
            )
            return
        
        # Set current table context for WHERE clause analysis
        self.current_table = table_name
        table_name_node.symbol_ref = table_name
        
        # Check selected columns (only BEFORE FROM keyword, skip if SELECT *)
        select_found = False
        for child in node.children:
            if child.name == "KEYWORD" and child.value == "SELECT":
                select_found = True
            elif child.name == "KEYWORD" and child.value == "FROM":
                # Stop checking columns once we hit FROM
                break
            elif select_found and child.name == "IDENTIFIER":
                col_name = child.value
                if not self.symbol_table.column_exists(table_name, col_name):
                    self._report_error(
                        f"Semantic Error: Column '{col_name}' does not exist in table '{table_name}'",
                        self._get_line(child), self._get_col(child)
                    )
                else:
                    # Annotate with column type
                    child.data_type = self.symbol_table.get_column_type(table_name, col_name)
                    child.symbol_ref = f"{table_name}.{col_name}"
        
        # Analyze WHERE clause if present
        for child in node.children:
            if child.name == "WhereClause":
                self._analyze_where_clause(child, table_name)
    
    def _analyze_update(self, node):
        """
        Analyze UPDATE statement:
        - Verify table exists
        - Verify column being updated exists
        - Check type compatibility of new value
        - Analyze WHERE clause
        """
        # Extract table name (2nd child: UPDATE [name])
        table_name_node = node.children[1]
        table_name = table_name_node.value
        line = self._get_line(table_name_node)
        col = self._get_col(table_name_node)
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self._report_error(
                f"Semantic Error: Table '{table_name}' not found",
                line, col
            )
            return
        
        self.current_table = table_name
        table_name_node.symbol_ref = table_name
        
        # Find column being updated and its new value
        # Pattern: UPDATE table SET [column] = [value]
        set_found = False
        column_node = None
        value_node = None
        
        for i, child in enumerate(node.children):
            if child.name == "KEYWORD" and child.value == "SET":
                set_found = True
            elif set_found and child.name == "IDENTIFIER" and column_node is None:
                column_node = child
            elif set_found and child.name == "Value":
                value_node = child
                break
            elif child.name == "WhereClause":
                self._analyze_where_clause(child, table_name)
        
        if column_node:
            col_name = column_node.value
            if not self.symbol_table.column_exists(table_name, col_name):
                self._report_error(
                    f"Semantic Error: Column '{col_name}' does not exist in table '{table_name}'",
                    self._get_line(column_node), self._get_col(column_node)
                )
            else:
                col_type = self.symbol_table.get_column_type(table_name, col_name)
                column_node.data_type = col_type
                column_node.symbol_ref = f"{table_name}.{col_name}"
                
                # Check type compatibility of new value
                if value_node:
                    value_type = self._infer_type(value_node)
                    if not self._types_compatible(col_type, value_type):
                        self._report_error(
                            f"Semantic Error: Type mismatch. Column '{col_name}' is {col_type}, but {value_type} value provided",
                            self._get_line(value_node), self._get_col(value_node)
                        )
                    else:
                        value_node.data_type = col_type
    
    def _analyze_delete(self, node):
        """
        Analyze DELETE statement:
        - Verify table exists
        - Analyze WHERE clause
        """
        # Find table name (after FROM keyword)
        table_name_node = None
        from_found = False
        for child in node.children:
            if child.name == "KEYWORD" and child.value == "FROM":
                from_found = True
            elif from_found and child.name == "IDENTIFIER":
                table_name_node = child
                break
        
        if not table_name_node:
            return
        
        table_name = table_name_node.value
        line = self._get_line(table_name_node)
        col = self._get_col(table_name_node)
        
        # Check table existence
        if not self.symbol_table.table_exists(table_name):
            self._report_error(
                f"Semantic Error: Table '{table_name}' not found",
                line, col
            )
            return
        
        self.current_table = table_name
        table_name_node.symbol_ref = table_name
        
        # Analyze WHERE clause if present
        for child in node.children:
            if child.name == "WhereClause":
                self._analyze_where_clause(child, table_name)
    
    def _analyze_where_clause(self, node, table_name):
        """
        Analyze WHERE clause:
        - Verify columns exist
        - Check type compatibility in comparisons
        """
        self._analyze_condition(node, table_name)
    
    def _analyze_condition(self, node, table_name):
        """Recursively analyze conditions in WHERE clause."""
        for child in node.children:
            if child.name == "Comparison":
                self._analyze_comparison(child, table_name)
            elif child.name in ["Condition", "Term", "Factor", "WhereClause"]:
                self._analyze_condition(child, table_name)
    
    def _analyze_comparison(self, node, table_name):
        """
        Analyze comparison operations (e.g., age > 18, name = 'Alice'):
        - Verify column exists
        - Check type compatibility between column and literal
        """
        operands = [child for child in node.children if child.name == "Operand"]
        
        if len(operands) < 2:
            return
        
        left_operand = operands[0]
        right_operand = operands[1]
        
        # Determine types of both operands
        left_type = None
        right_type = None
        
        # Check if left operand is a column identifier
        if left_operand.value and self.symbol_table.column_exists(table_name, left_operand.value):
            left_type = self.symbol_table.get_column_type(table_name, left_operand.value)
            left_operand.data_type = left_type
            left_operand.symbol_ref = f"{table_name}.{left_operand.value}"
        elif left_operand.value:
            # It's a literal
            left_type = self._infer_type_from_value(left_operand.value)
            left_operand.data_type = left_type
        
        # Check if right operand is a column identifier
        if right_operand.value and self.symbol_table.column_exists(table_name, right_operand.value):
            right_type = self.symbol_table.get_column_type(table_name, right_operand.value)
            right_operand.data_type = right_type
            right_operand.symbol_ref = f"{table_name}.{right_operand.value}"
        elif right_operand.value:
            # It's a literal
            right_type = self._infer_type_from_value(right_operand.value)
            right_operand.data_type = right_type
        
        # Type compatibility check
        if left_type and right_type:
            if not self._types_compatible(left_type, right_type):
                self._report_error(
                    f"Semantic Error: Type mismatch in comparison. Cannot compare {left_type} with {right_type}",
                    self._get_line(right_operand), self._get_col(right_operand)
                )
    
    def _infer_type(self, node):
        """Infer the semantic type from a parse tree node."""
        if not node or not node.value:
            return "UNKNOWN"
        
        # Check if it's a string literal (surrounded by quotes)
        value = str(node.value)
        if value.startswith("'") and value.endswith("'"):
            return "TEXT"
        
        # Try to parse as number
        try:
            if '.' in value:
                float(value)
                return "FLOAT"
            else:
                int(value)
                return "INT"
        except ValueError:
            pass
        
        return "TEXT"
    
    def _infer_type_from_value(self, value):
        """Infer type from a raw value string."""
        if not value:
            return "UNKNOWN"
        
        value_str = str(value)
        
        # Check if string literal
        if value_str.startswith("'") and value_str.endswith("'"):
            return "TEXT"
        
        # Try numeric types
        try:
            if '.' in value_str:
                float(value_str)
                return "FLOAT"
            else:
                int(value_str)
                return "INT"
        except ValueError:
            pass
        
        return "TEXT"
    
    def _types_compatible(self, expected_type, actual_type):
        """
        Check if two types are compatible.
        For strict type checking, they must match exactly.
        INT and FLOAT can be considered compatible (numeric types).
        """
        if expected_type == actual_type:
            return True
        
        # Allow INT and FLOAT to be somewhat compatible
        numeric_types = {"INT", "FLOAT"}
        if expected_type in numeric_types and actual_type in numeric_types:
            return True
        
        return False
    
    def _get_line(self, node):
        """Extract line number from parse node (if available)."""
        return getattr(node, 'line', 0)
    
    def _get_col(self, node):
        """Extract column number from parse node (if available)."""
        return getattr(node, 'col', 0)
    
    def _report_error(self, message, line, col):
        """Add an error to the error list with line and column information."""
        if line > 0 and col > 0:
            error_msg = f"{message} (Line {line}, Column {col})"
        else:
            error_msg = message
        self.errors.append(error_msg)
    
    def get_annotated_tree(self):
        """Return the parse tree with semantic annotations."""
        return self.parse_tree
    
    def get_symbol_table_dump(self):
        """Return formatted symbol table dump."""
        return self.symbol_table.dump()
    
    def get_errors(self):
        """Return list of semantic errors."""
        return self.errors
