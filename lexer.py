# lexer.py
from dfa_definitions import (
    classify_char, identifier_dfa, identifier_accept,
    number_dfa, number_accept, operator_dfa, operator_accept,
    string_dfa, string_accept, delimiters, parentheses, keywords
)
from dfa_runner import run_dfa

def tokenize(text):
    tokens = []
    errors = []
    line_num = 1
    col = 1
    i = 0
    
    while i < len(text):
        ch = text[i]
        start_col = col

        # Handle Whitespace
        if ch in ' \t\r':
            i += 1
            col += 1
            continue
        if ch == '\n':
            line_num += 1
            col = 1
            i += 1
            continue

        # Handle Comments (-- and ##)
        if text[i:i+2] == "--":
            i += 2
            col += 2
            while i < len(text) and text[i] != '\n':
                i += 1
                col += 1
            continue
        
        if text[i:i+2] == "##":
            i += 2
            col += 2
            start_line = line_num
            while i < len(text):
                if text[i:i+2] == "##":
                    i += 2; col += 2; break
                if text[i] == '\n':
                    line_num += 1; col = 1; i += 1
                else:
                    i += 1; col += 1
            else:
                errors.append(f"Error: Unclosed comment starting line {start_line}")
            continue

        # Handle String Literals
        if ch == "'":
            lexeme, token_type, next_i = run_dfa(string_dfa, string_accept, text, i)
            if lexeme:
                tokens.append((token_type, lexeme, line_num, start_col))
                col += (next_i - i)
                i = next_i
                continue
            else:
                # Basic error recovery for string
                end = text.find('\n', i)
                if end == -1: end = len(text)
                errors.append(f"Error: Invalid string at line {line_num}")
                i = end
                continue

        # Handle DFAs (Identifier, Number, Operator)
        best_lexeme = None
        best_type = None
        best_len = 0

        # Try all DFAs and pick the one that matches
        for dfa, accept in [(identifier_dfa, identifier_accept), 
                            (number_dfa, number_accept), 
                            (operator_dfa, operator_accept)]:
            lexeme, token_type, next_i = run_dfa(dfa, accept, text, i)
            if lexeme and len(lexeme) > best_len:
                best_lexeme = lexeme
                best_type = token_type
                best_len = len(lexeme)
        
        if best_lexeme:
            # CHECK KEYWORD (now we deal wityh keywords as case-sensitive)
            if best_type == "IDENTIFIER" and best_lexeme in keywords:
                tokens.append(("KEYWORD", best_lexeme, line_num, start_col))
            else:
                tokens.append((best_type, best_lexeme, line_num, start_col))
            
            i += best_len
            col += best_len
            continue

        # Handle Delimiters & Parentheses
        if ch in delimiters:
            tokens.append((delimiters[ch], ch, line_num, start_col))
            i += 1; col += 1; continue
            
        if ch in parentheses:
            tokens.append((parentheses[ch], ch, line_num, start_col))
            i += 1; col += 1; continue
        
        # Fallback Error
        errors.append(f"Lexical Error: Unexpected character '{ch}' at {line_num}:{col}")
        i += 1
        col += 1

    return tokens, errors