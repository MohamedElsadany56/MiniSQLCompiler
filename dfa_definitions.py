import re

def classify_char(ch):
    if re.match(r'[A-Za-z]', ch):
        return 'LETTER'
    elif re.match(r'[0-9]', ch):
        return 'DIGIT'
    elif re.match(r'\s', ch):
        return 'SPACE'
    elif re.match(r"[+\-*/=<>{},;.:]", ch):
        return 'OP'  # arithmetic / comparison / punctuation operators
    elif ch in '([{':
        return 'PAREN_LEFT'   # left parentheses types
    elif ch in ')]}':
        return 'PAREN_RIGHT'  # right parentheses types
    elif ch == "'":
        return 'QUOTE'  # string quote delimiter
    elif ch == '#':
        return 'HASH'
    elif ch == '_':
        return 'UNDERSCORE'
    else:
        return ch  # allow direct symbol matching


# DFA DEFINITIONS

# Identifier DFA: [a-zA-Z][a-zA-Z0-9_]*
identifier_dfa = {
    0: {'LETTER': 1},
    1: {'LETTER': 1, 'DIGIT': 1, 'UNDERSCORE': 1},
}
identifier_accept = {1: 'IDENTIFIER'}


# Number DFA: [0-9]+(\.[0-9]+)?
number_dfa = {
    0: {'DIGIT': 1},
    1: {'DIGIT': 1, '.': 2},
    2: {'DIGIT': 3}, 
    3: {'DIGIT': 3},
}
number_accept = {1: 'INTEGER', 3: 'FLOAT'}


# Operator DFA: + - * / = <> >= <= !=
operator_dfa = {
    0: {'OP': 1},
    1: {'=': 2, '>': 2, '<': 2, '!': 2},
}
operator_accept = {1: 'OPERATOR', 2: 'OPERATOR'}



# String DFA:  '...'
string_dfa = {
    0: {'QUOTE': 1},           # opening quote
    1: {'QUOTE': 2, 'OTHER': 1}  # inside string until closing quote
}
string_accept = {2: 'STRING'}


# Delimiters and parentheses
delimiters = {',', ';'}

parentheses = {
    '(': 'LEFT_PAREN',
    ')': 'RIGHT_PAREN',
    '{': 'LEFT_BRACE',
    '}': 'RIGHT_BRACE',
    '[': 'LEFT_BRACKET',
    ']': 'RIGHT_BRACKET'
}


# SQL keywords
keywords = {
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES",
    "UPDATE", "SET", "DELETE", "CREATE", "TABLE",
    "INT", "FLOAT", "TEXT", "AND", "OR", "NOT",
    "AS", "JOIN", "ON", "GROUP", "BY", "ORDER", "DESC", "ASC"
}
