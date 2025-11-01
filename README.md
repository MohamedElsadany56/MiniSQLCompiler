# SQL Lexical Analyzer using DFA

A Python-based **lexical analyzer (lexer)** that tokenizes SQL code using **Deterministic Finite Automata (DFA)** for identifiers, numbers, and operators.
It detects SQL keywords, delimiters, string literals, and comments, while also generating a **symbol table** and **error report**.

---

## Features

* Tokenizes SQL input using multiple DFAs
* Detects keywords, identifiers, literals, and operators
* Handles comments (`--` and `## ##`) and string constants (`'string'`)
* Reports line and column for each token and error
* Builds a simple symbol table of identifiers

---

## Project Overview

| Member | Module                                     | Description                                                                          |
| :----: | :----------------------------------------- | :----------------------------------------------------------------------------------- |
|  **1** | [`dfa_definitions.py`](dfa_definitions.py) | Character classification and DFA definitions for identifiers, numbers, and operators |
|  **2** | [`dfa_runner.py`](dfa_runner.py)           | Generic DFA engine that simulates transitions and recognizes tokens                  |
|  **3** | [`lexer.py`](lexer.py)                     | Main lexical logic: applies DFAs, handles strings/comments/delimiters                |
|  **4** | [`main.py`](main.py)                       | Program entry point: integrates everything, displays tokens, symbols, and errors     |

---

## Repository Structure

```
MiniSQLCompiler/
│
├── dfa_definitions.py      # Mohamed Goma (Elsadany) - DFA definitions and classify_char()
├── dfa_runner.py           # Mohamed Hassan - Generic DFA runner
├── lexer.py                # Mostafa Adel  - Tokenization logic
├── main.py                 # Ziad Hamada - Main program entry point
│
├── samples/
│   └── test_1.sql          # Example SQL input file
│
├── README.md
└── requirements.txt
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

### Run the lexer

```bash
python main.py samples/test_1.sql
```

### Example Input (`samples/test_1.sql`)

```sql
SELECT name, age FROM students WHERE age >= 22;
INSERT INTO users VALUES ('Elsdany', 25);
## multi-line comment
```

### Example Output

```
=== TOKENS ===
KEYWORD       SELECT          (line 1, col 1)
IDENTIFIER    name            (line 1, col 8)
DELIMITER     ,               (line 1, col 12)
IDENTIFIER    age             (line 1, col 14)
KEYWORD       FROM            (line 1, col 18)
IDENTIFIER    students        (line 1, col 23)
KEYWORD       WHERE           (line 1, col 32)
IDENTIFIER    age             (line 1, col 38)
OPERATOR      >=              (line 1, col 41)
INTEGER       22              (line 1, col 44)
DELIMITER     ;               (line 1, col 46)

=== SYMBOL TABLE (Identifiers) ===
name
age
students

=== ERRORS ===
No lexical errors found.
```

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

## Algorithm Summary

1. **Character Classification**

   * Each character is classified (`LETTER`, `DIGIT`, `SPACE`, etc.) via `classify_char()`.

2. **DFA Simulation**

   * DFAs for identifiers, numbers, and operators define valid transitions between states.

3. **Lexical Analysis**

   * The `tokenize()` function:

     * Skips whitespace/comments
     * Tries each DFA in sequence
     * Recognizes string literals
     * Builds token list and error log

4. **Output**

   * The `main.py` script prints:

     * All tokens with positions
     * A symbol table for identifiers
     * Any lexical errors

---

## Contributors

| Name                    | Role                                       | Module               |
| ----------------------- | ------------------------------------------ | -------------------- |
| Mohamed Goma (Elsadany) | Character classification & DFA definitions | `dfa_definitions.py` |
| Mohamed Hassan          | DFA runner implementation                  | `dfa_runner.py`      |
| Mostafa Adel            | Tokenizer logic                            | `lexer.py`           |
| Ziad Hamada             | Integration & symbol table                 | `main.py`            |

---

## Future Enhancements

* Integration with a **syntax analyzer (parser)** and **semantic analyzer**
* Graphical User Interface (GUI)
* Unit tests for DFAs and tokenization

---

## License

This project is released under the **MIT License**.
Feel free to modify and distribute with credit to the contributors.

---

**© 2025 SQL Lexical Analyzer Project Team**

