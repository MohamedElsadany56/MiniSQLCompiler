# Phase 03: Semantic Analyzer - Implementation Report

**Project:** Mini Compiler for SQL-like Languages  
**Phase:** 03 - Semantic Analysis  
**Team Members:** Mohamed Goma (Elsadany), Mohamed Hassan, Mostafa Adel, Ziad Hamada

---

## 1. Symbol Table Design and Implementation

### 1.1 Structure

The Symbol Table is implemented as a hierarchical dictionary-based structure in the `SymbolTable` class. The design follows these principles:

**Data Structure:**
```python
tables = {
    'table_name': {
        'columns': [(column_name, data_type), ...],
        'line': integer,
        'col': integer
    }
}
```

**Key Design Decisions:**

1. **Hierarchical Organization**: Each table is a top-level entry, with columns stored as a list of tuples within that table's metadata.

2. **Type Information**: Column definitions store both the column name and its declared data type (INT, FLOAT, or TEXT).

3. **Source Location Tracking**: Each table records the line and column number where it was declared, enabling precise error reporting.

4. **Efficient Lookup**: Dictionary-based storage allows O(1) table lookup and O(n) column lookup where n is the number of columns in a table (typically small).

### 1.2 Core Operations

The Symbol Table provides the following essential operations:

- `add_table()`: Registers a new table with its column definitions
- `table_exists()`: Checks if a table has been declared
- `get_column_type()`: Retrieves the data type of a specific column
- `column_exists()`: Verifies column existence within a table
- `dump()`: Produces formatted output of all tables and columns

### 1.3 Population Strategy

The Symbol Table is populated during semantic analysis:

1. When a `CREATE TABLE` statement is encountered, the analyzer extracts the table name and column definitions
2. Before adding, it checks for redeclaration (semantic error if table exists)
3. Column metadata (name and type) is stored as a list of tuples
4. The table entry is added to the symbol table with source location information

---

## 2. Semantic Rules Implemented

### 2.1 Identifier Verification

#### Table Existence
**Rule**: Any table referenced in INSERT, SELECT, UPDATE, or DELETE must be previously declared.

**Implementation**:
- Before processing any DML statement, the analyzer calls `table_exists()`
- If the table is not found, a semantic error is reported with the line and column number
- Example error: `"Semantic Error: Table 'NonExistent' not found (Line 5, Column 13)"`

#### Column Existence
**Rule**: All column identifiers in SELECT, UPDATE, and WHERE clauses must exist in the referenced table.

**Implementation**:
- For each column reference, the analyzer calls `column_exists(table_name, column_name)`
- The current table context is tracked during SELECT/UPDATE/DELETE analysis
- Invalid column references generate errors with precise location information
- Example error: `"Semantic Error: Column 'invalid_col' does not exist in table 'Products' (Line 12, Column 8)"`

#### Ambiguity Prevention
**Rule**: Column names must not be ambiguous when multiple tables are involved.

**Implementation**:
- Current implementation focuses on single-table queries as per project scope
- The `current_table` context variable tracks which table is being queried
- Foundation is laid for future multi-table query support

#### Redeclaration Prevention
**Rule**: CREATE TABLE must not declare a table that already exists.

**Implementation**:
- Before adding a table to the symbol table, `table_exists()` is checked
- If the table exists, the error message includes the original declaration location
- Example error: `"Semantic Error: Table 'Users' already declared at line 3 (Line 5, Column 14)"`

### 2.2 Type Checking

#### Data Type Validation in CREATE TABLE
**Rule**: Only INT, FLOAT, and TEXT are valid data types.

**Implementation**:
- The parser enforces this at syntax level, but the semantic analyzer double-checks
- Invalid types generate semantic errors during CREATE TABLE analysis
- Example error: `"Semantic Error: Invalid data type 'BOOLEAN'. Expected INT, FLOAT, or TEXT (Line 2, Column 25)"`

#### INSERT Type Consistency
**Rule**: The number and types of VALUES must match the table's column definitions.

**Implementation**:

1. **Count Verification**: 
   - Compare the number of values against `get_column_count()`
   - Error if mismatch: `"Semantic Error: Column count mismatch. Table 'Products' has 3 columns, but 2 values provided (Line 8, Column 13)"`

2. **Type Verification**:
   - Iterate through values and corresponding column types
   - Call `_infer_type()` to determine the literal's type from the token
   - Use `_types_compatible()` to check if types match
   - Type inference logic:
     - String literals (surrounding quotes) → TEXT
     - Decimal numbers (contains '.') → FLOAT
     - Integer numbers → INT
   - Example error: `"Semantic Error: Type mismatch at line 10, position 35. Column 'price' is defined as FLOAT, but a TEXT literal was provided for insertion (Line 10, Column 35)"`

#### WHERE Clause Type Compatibility
**Rule**: In comparison operations, the column type must be compatible with the compared literal.

**Implementation**:
- Parse the WHERE clause to extract comparisons
- For each comparison, identify left and right operands
- If an operand is a column identifier, look up its type from the symbol table
- If an operand is a literal, infer its type
- Check compatibility using `_types_compatible()`
- Numeric compatibility: INT and FLOAT are considered compatible
- TEXT must match TEXT exactly
- Example error: `"Semantic Error: Type mismatch in comparison. Cannot compare INT with TEXT (Line 15, Column 42)"`

---

## 3. Error Detection and Reporting

### 3.1 Error Detection Mechanism

**Strategy**: The semantic analyzer employs a comprehensive error collection approach rather than fail-fast:

1. **Tree Traversal**: The parse tree is traversed recursively
2. **Error Accumulation**: Errors are collected in a list rather than immediately terminating
3. **Context Preservation**: Each error includes the source location (line and column)
4. **Descriptive Messages**: Each error explains what was expected vs. what was found

### 3.2 Line and Column Tracking

**Implementation**:
- The `ParseNode` class was enhanced to store token information
- Each node created during parsing includes:
  - `token`: The original token tuple (type, value, line, col)
  - `line`: Extracted line number
  - `col`: Extracted column number
- Semantic analyzer accesses `node.line` and `node.col` for error reporting

### 3.3 Error Message Format

**Standard Format**:
```
Semantic Error: [Description of error] (Line X, Column Y)
```

**Examples**:

1. **Table Not Found**:
   ```
   Semantic Error: Table 'NonExistent' not found (Line 5, Column 13)
   ```

2. **Type Mismatch in INSERT**:
   ```
   Semantic Error: Type mismatch at line 10, position 35. Column 'price' is 
   defined as FLOAT, but a TEXT literal was provided for insertion (Line 10, Column 35)
   ```

3. **Column Count Mismatch**:
   ```
   Semantic Error: Column count mismatch. Table 'Products' has 3 columns, 
   but 2 values provided (Line 8, Column 13)
   ```

4. **Column Not Found**:
   ```
   Semantic Error: Column 'invalid_col' does not exist in table 'Products' (Line 12, Column 8)
   ```

5. **Table Redeclaration**:
   ```
   Semantic Error: Table 'Users' already declared at line 3 (Line 5, Column 14)
   ```

6. **WHERE Type Mismatch**:
   ```
   Semantic Error: Type mismatch in comparison. Cannot compare INT with TEXT (Line 15, Column 42)
   ```

### 3.4 Output Organization

The compiler produces structured output for each phase:

**Phase 01 (Lexical)**: Token list and lexical errors  
**Phase 02 (Syntax)**: Parse tree and syntax errors  
**Phase 03 (Semantic)**: Symbol table dump, annotated parse tree, and semantic errors

**Success Output** (when no errors):
```
 SEMANTIC ANALYSIS SUCCESSFUL. QUERY IS VALID.

Symbol Table displays all tables and columns with types
Annotated Parse Tree shows type information for each node
```

**Failure Output** (when errors found):
```
[!] Semantic errors found. Query is invalid.

[List of all semantic errors with line:col information]
```

---

## 4. Integration and Testing

### 4.1 Integration with Previous Phases

The semantic analyzer seamlessly integrates with Phases 01 and 02:
- Consumes tokens from the lexer (Phase 01)
- Receives parse tree from the parser (Phase 02)
- Annotates the parse tree with semantic information
- Builds and maintains the symbol table independently

### 4.2 Test Files

Three comprehensive test files were created:

1. **test_semantic_valid.sql**: Demonstrates fully valid SQL queries
2. **test_semantic_errors.sql**: Contains 12 different semantic error scenarios
3. **test_mixed.sql**: Combines valid and invalid queries to test error recovery

### 4.3 Verification

All semantic rules have been tested and verified:
-  Table existence checking
-  Column existence checking
-  Redeclaration prevention
-  INSERT type and count checking
-  WHERE clause type compatibility
-  Accurate line/column error reporting

---

## 5. Conclusion

The Phase 03 Semantic Analyzer successfully implements all required functionality:
- **Symbol Table**: Hierarchical structure efficiently stores table and column metadata
- **Semantic Checks**: Comprehensive identifier and type verification
- **Error Reporting**: Precise, descriptive errors with source location information
- **Output**: Clear symbol table dump and annotated parse tree
---

**End of Report**
