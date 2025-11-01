from dfa_definitions import (
    classify_char, identifier_dfa, identifier_accept,
    number_dfa, number_accept, operator_dfa, operator_accept,
    string_dfa, string_accept,
    delimiters, parentheses, keywords
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

        # Handle newlines
        if ch == '\n':
            line_num += 1
            col = 1
            i += 1
            continue

        # Ignore whitespace
        if ch.isspace():
            i += 1
            col += 1
            continue

        # Single-line comments (--)
        if text[i:i+2] == "--":
            while i < len(text) and text[i] != '\n':
                i += 1
            continue

        # Multi-line comments (## ##)
        if text[i:i+2] == "##":
            start_line = line_num
            i += 2
            while i < len(text) - 1 and text[i:i+2] != "##":
                if text[i] == '\n':
                    line_num += 1
                    col = 1
                else:
                    col += 1
                i += 1
            if i >= len(text) - 1:
                errors.append(f"Error: unclosed comment starting at line {start_line}.")
                break
            i += 2
            continue

        # -------------------------------
        # String literal using DFA
        # -------------------------------
        if ch == "'":
            lexeme, token_type, next_i = run_dfa(string_dfa, string_accept, text, i)
            if lexeme:
                tokens.append((token_type, lexeme, line_num, start_col))
                consumed = next_i - i
                i = next_i
                col += consumed
                continue
            else:
                errors.append(f"Error: unclosed string starting at line {line_num}.")
                break

        # -------------------------------
        # Run DFAs: identifiers, numbers, operators
        # -------------------------------
        matched = False
        for dfa, accept in [
            (identifier_dfa, identifier_accept),
            (number_dfa, number_accept),
            (operator_dfa, operator_accept),
        ]:
            lexeme, token_type, next_i = run_dfa(dfa, accept, text, i)
            if lexeme:
                if token_type == 'IDENTIFIER' and lexeme.upper() in keywords:
                    tokens.append(("KEYWORD", lexeme.upper(), line_num, start_col))
                else:
                    tokens.append((token_type, lexeme, line_num, start_col))
                consumed = next_i - i
                i = next_i
                col += consumed
                matched = True
                break

        if matched:
            continue

        # -------------------------------
        # Parentheses
        # -------------------------------
        if ch in parentheses:
            tokens.append((parentheses[ch], ch, line_num, start_col))
            i += 1
            col += 1
            continue

        # -------------------------------
        # Delimiters
        # -------------------------------
        if ch in delimiters:
            tokens.append(("DELIMITER", ch, line_num, start_col))
            i += 1
            col += 1
            continue

        # -------------------------------
        # Unknown characters
        # -------------------------------
        errors.append(f"Error: invalid character '{ch}' at line {line_num}, column {col}.")
        i += 1
        col += 1

    return tokens, errors