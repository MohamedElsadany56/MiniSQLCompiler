# Mini SQL Compiler - Three-Phase Implementation

A Python-based **compiler for SQL-like languages** that performs complete **lexical, syntax, and semantic analysis**. The compiler is built in three phases, each handling a critical aspect of compilation: tokenization, parsing, and semantic verification.


---

## Features

**Phase 01 - Lexical Analysis:**
* Tokenizes SQL input using multiple DFAs
* Detects keywords, identifiers, literals, and operators
* Handles comments (`--` and `## ##`) and string constants (`'string'`)
* Reports line and column for each token and error

**Phase 02 - Syntax Analysis:**
* Parses SQL statements (CREATE TABLE, INSERT, SELECT, UPDATE, DELETE)
* Builds parse tree representing query structure
* Supports complex WHERE clauses with AND/OR/NOT logic
* Comprehensive error reporting with panic mode recovery

**Phase 03 - Semantic Analysis:**
* Symbol table management for tables and columns
* Identifier verification (table/column existence, redeclaration checking)
* Type checking (CREATE TABLE types, INSERT consistency, WHERE compatibility)
* Annotated parse tree with type information
* Detailed error messages with line and column numbers


---

## Project Overview

| Phase | Module | Description |
| :---: | :----- | :---------- |
| **1** | [`dfa_definitions.py`](dfa_definitions.py) | Character classification and DFA definitions |
| **1** | [`dfa_runner.py`](dfa_runner.py) | Generic DFA engine for token recognition |
| **1** | [`lexer.py`](lexer.py) | Main lexical analyzer - tokenization logic |
| **2** | [`parser.py`](parser.py) | Syntax analyzer - builds parse tree from tokens |
| **3** | [`semantic_analyzer.py`](semantic_analyzer.py) | Semantic analyzer - type checking and symbol table |
| **All** | [`main.py`](main.py) | Program entry point - integrates all three phases |


---

## Repository Structure

```
MiniSQLCompiler/
│
├── Phase 01 - Lexical Analysis
│   ├── dfa_definitions.py           # DFA definitions and character classification
│   ├── dfa_runner.py                # Generic DFA runner
│   └── lexer.py                     # Tokenization logic
│
├── Phase 02 - Syntax Analysis
│   └── parser.py                    # Parse tree builder
│
├── Phase 03 - Semantic Analysis
│   └── semantic_analyzer.py         # Symbol table and type checking
│
├── Integration
│   └── main.py                      # Three-phase compiler entry point
│
├── Test Files
│   ├── samples/
│   │   ├── test_1.sql               # Original test file
│   │   ├── test_semantic_valid.sql  # Valid semantic test cases
│   │   ├── test_semantic_errors.sql # Semantic error test cases
│   │   └── test_mixed.sql           # Mixed valid/invalid queries
│
├── Documentation
│   ├── README.md                    # This file
│   ├── PHASE03_REPORT.md            # Semantic analyzer report
│   └── requirements.txt             # Dependencies (none - pure Python)
```


---

## Installation

### Clone the Repository

```bash
git clone https://github.com/MohamedElsadany56/MiniSQLCompiler.git
cd MiniSQLCompiler
```

### (Optional) Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # On Linux/Mac
venv\Scripts\activate        # On Windows
```

### Install Requirements

```bash
pip install -r requirements.txt
```

*(Note: this project only uses built-in libraries — no external dependencies.)*

---

## Usage

### Run the Complete Compiler

```bash
python main.py samples/test_semantic_valid.sql
```

### Example Input (`samples/test_semantic_valid.sql`)

```sql
CREATE TABLE Students (name TEXT, age INT, gpa FLOAT);
INSERT INTO Students VALUES ('Alice', 20, 3.5);
SELECT name, age FROM Students WHERE age > 18;
```

### Example Output

```
======================================================================
MINI SQL COMPILER - THREE PHASE COMPILATION
======================================================================

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
PHASE 01: LEXICAL ANALYSIS
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

>> TOKENS
KEYWORD       CREATE          (line 1, col 1)
KEYWORD       TABLE           (line 1, col 8)
IDENTIFIER    Students        (line 1, col 14)
LPAREN        (               (line 1, col 23)
IDENTIFIER    name            (line 1, col 24)
KEYWORD       TEXT            (line 1, col 29)
COMMA         ,               (line 1, col 33)
...

>> LEXICAL ERRORS
No lexical errors found. ✓

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
PHASE 02: SYNTAX ANALYSIS
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

>> PARSE TREE
Query
  Statement
    CreateStmt
      KEYWORD: CREATE
      KEYWORD: TABLE
      IDENTIFIER: Students
      ...

>> SYNTAX ERRORS
No syntax errors found. ✓

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
PHASE 03: SEMANTIC ANALYSIS
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

============================================================
SYMBOL TABLE DUMP
============================================================

Table: Students
  Defined at: Line 1, Column 14
  Columns:
    - name: TEXT
    - age: INT
    - gpa: FLOAT
============================================================

>> SEMANTIC ERRORS
No semantic errors found. ✓

======================================================================
✓ SEMANTIC ANALYSIS SUCCESSFUL. QUERY IS VALID.
======================================================================

>> ANNOTATED PARSE TREE
(Parse tree with type annotations and symbol table references)
...

======================================================================
COMPILATION SUMMARY
======================================================================
Lexical Errors:   0
Syntax Errors:    0
Semantic Errors:  0
Status:           SUCCESS ✓
======================================================================
```

### Testing Semantic Errors

```bash
python main.py samples/test_semantic_errors.sql
```

This will display all detected semantic errors with line and column numbers.


---

## Token Types

| Token Type   | Description                       | Example                 |
| :----------- | :-------------------------------- | :---------------------- |
| `KEYWORD`    | SQL reserved word                 | `SELECT`, `FROM`        |
| `IDENTIFIER` | User-defined name                 | `table_name`, `column1` |
| `INTEGER`    | Integer number                    | `42`                    |
| `FLOAT`      | Decimal number                    | `3.14`                  |
| `STRING`     | String literal                    | `'Alice'`               |
| `OPERATOR`   | Arithmetic or relational operator | `+`, `-`, `=`, `<=`     |
| `DELIMITER`  | Special separator symbol          | `,`, `;`, `(`, `)`      |
| `ERROR`      | Invalid or unrecognized character | `@`, `$`, etc.          |

---

## Compilation Process

### Phase 01: Lexical Analysis

1. **Character Classification**
   * Each character is classified (`LETTER`, `DIGIT`, `SPACE`, etc.) via `classify_char()`.

2. **DFA Simulation**
   * DFAs for identifiers, numbers, and operators define valid transitions between states.

3. **Tokenization**
   * The `tokenize()` function:
     * Skips whitespace/comments
     * Tries each DFA in sequence
     * Recognizes string literals
     * Builds token list and error log

### Phase 02: Syntax Analysis

1. **Recursive Descent Parsing**
   * Parser implements a grammar for SQL-like statements
   * Each grammar rule is implemented as a parsing function

2. **Parse Tree Construction**
   * `ParseNode` objects represent each syntactic construct
   * Tree structure preserves the hierarchical nature of the query

3. **Error Recovery**
   * Panic mode recovery skips to next semicolon after syntax error
   * Multiple errors can be collected in one compilation pass

### Phase 03: Semantic Analysis

1. **Symbol Table Construction**
   * Tables and columns are registered during CREATE TABLE processing
   * Metadata includes column names, data types, and source locations

2. **Semantic Verification**
   * Table and column existence checks for all DML statements
   * Type compatibility verification for INSERT values and WHERE conditions
   * Redeclaration prevention for tables

3. **Parse Tree Annotation**
   * Each node is annotated with inferred or verified type information
   * Identifiers are linked to their symbol table entries

4. **Comprehensive Error Reporting**
   * All semantic errors are collected with precise line and column information
   * Descriptive messages explain what was expected vs. what was found


---

## Contributors

| Name                    | Role                                       | Module               |
| ----------------------- | ------------------------------------------ | -------------------- |
| Mohamed Goma (Elsadany) | Character classification & DFA definitions | `dfa_definitions.py` |
| Mohamed Hassan          | DFA runner implementation                  | `dfa_runner.py`      |
| Mostafa Adel            | Tokenizer logic                            | `lexer.py`           |
| Ziad Hamada             | Integration & symbol table                 | `main.py`            |

---


## License

This project is released under the **MIT License**.
Feel free to modify and distribute with credit to the contributors.

---

**© 2025 SQL Lexical Analyzer Project Team**

