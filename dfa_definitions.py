import re

def classify_char(ch):
    if re.match(r'[A-Za-z]', ch):
        return 'LETTER'
    elif re.match(r'[0-9]', ch):
        return 'DIGIT'
    elif re.match(r'\s', ch):
        return 'SPACE'
    elif re.match(r"[+\-*/=<>{},;.:]", ch):
        return 'OP'  
    elif ch in '([{':
        return 'PAREN_LEFT'  
    elif ch in ')]}':
        return 'PAREN_RIGHT'  
    elif ch == "'":
        return 'QUOTE'  
    elif ch == '#':
        return 'HASH'
    elif ch == '_':
        return 'UNDERSCORE'
    else:
        return ch  

# KEYWORDS
keywords = {
    "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES",
    "UPDATE", "SET", "DELETE", "CREATE", "TABLE",
    "INT", "FLOAT", "TEXT"
}

# IDENTIFIER DFA
identifier_dfa = {0:{}, 1:{}}
for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_":
    identifier_dfa[0][c] = 1
    identifier_dfa[1][c] = 1
for c in "0123456789":
    identifier_dfa[1][c] = 1
identifier_accept = {1:"IDENTIFIER"}

# NUMBER DFA 
number_dfa = {0:{}, 1:{}}
for d in "0123456789":
    number_dfa[0][d] = 1
    number_dfa[1][d] = 1
number_accept = {1:"INTEGER"}

# OPERATOR DFA
operator_dfa = {0:{},1:{},2:{}}
single_ops = "=<>+-*/"
for op in single_ops:
    operator_dfa[0][op] = 1
operator_dfa[0][">"] = 1
operator_dfa[0]["<"] = 1
operator_dfa[0]["!"] = 1
operator_dfa[1]["="] = 2
operator_accept = {1:"OPERATOR",2:"OPERATOR"}

# STRING DFA
string_dfa = {0:{"'":1}, 1:{}, 2:{}}
for code in range(32,127):
    c = chr(code)
    if c != "'":
        string_dfa[1][c] = 1
string_dfa[1]["'"] = 2
string_accept = {2:"STRING"}

# DELIMITERS AND PARENTHESES
delimiters = {",": "COMMA", ";": "SEMICOLON"}
parentheses = {"(": "LPAREN", ")": "RPAREN"}
