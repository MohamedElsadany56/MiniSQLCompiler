def classify_char(ch): 
    """Classifies a character without using regex."""
    if 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
        return 'LETTER'
    if '0' <= ch <= '9':
        return 'DIGIT'
    if ch in ' \t\n\r':
        return 'SPACE'
    if ch in "+-*/=<>!": 
        return 'OP'
    if ch in '([{':
        return 'PAREN_LEFT'
    if ch in ')]}':
        return 'PAREN_RIGHT'
    if ch == "'":
        return 'QUOTE'
    if ch == '#':
        return 'HASH'
    if ch == '_':
        return 'UNDERSCORE'
    if ch in ',;':
        return 'DELIMITER'
    if ch == '.':
        return 'DOT'
    return 'OTHER'
# keywords
keywords = {
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES",
    "UPDATE", "SET", "DELETE", "CREATE", "TABLE",
    "INT", "FLOAT", "TEXT", "AND", "OR", "NOT",
    "AS", "JOIN", "ON", "GROUP", "BY", "ORDER", "DESC", "ASC"
}

# Identifier DFA
# State 0 -> Start
# State 1 -> Valid Identifier
identifier_dfa = {0: {}, 1: {}}
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
digits = "0123456789"

for c in chars:
    identifier_dfa[0][c] = 1
    identifier_dfa[1][c] = 1
for d in digits:
    identifier_dfa[1][d] = 1

identifier_accept = {1: "IDENTIFIER"}

# Number DFA (Integers and Floats)
# State 0 -> Start
# State 1 -> Integer part (Accepting)
# State 2 -> Decimal point (Intermediate)
# State 3 -> Fraction part (Accepting FLOAT)
number_dfa = {0: {}, 1: {}, 2: {}, 3: {}}

for d in digits:
    number_dfa[0][d] = 1
    number_dfa[1][d] = 1
    number_dfa[2][d] = 3
    number_dfa[3][d] = 3

number_dfa[1]['.'] = 2 # Transition on dot
number_accept = {1: "INTEGER", 3: "FLOAT"} # I added float because we missed it in phase 1

# OPERATOR DFA
operator_dfa = {0: {}, 1: {}, 2: {}}
simple_ops = "+-*/=<>!"

for op in simple_ops:
    operator_dfa[0][op] = 1

# Handling multi-char ops: >=, <=, !=, <>
operator_dfa[1]['='] = 2
operator_dfa[1]['>'] = 2 # for <>

operator_accept = {1: "OPERATOR", 2: "OPERATOR"}

# String DFA
string_dfa = {0: {"'": 1}, 1: {}, 2: {}}
# Allow all printable ascii in string
for i in range(32, 127):
    c = chr(i)
    if c != "'":
        string_dfa[1][c] = 1
string_dfa[1]["'"] = 2
string_accept = {2: "STRING"}

# Delimiters & Parentheses Mapping
delimiters = {",": "COMMA", ";": "SEMICOLON"}
parentheses = {
    "(": "LPAREN", ")": "RPAREN",
    "{": "LBRACE", "}": "RBRACE",
    "[": "LBRACKET", "]": "RBRACKET"
}
