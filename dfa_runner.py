from dfa_definitions import classify_char

def run_dfa(dfa, accepting, text, start_index):
    state = 0
    i = start_index
    lexeme = ""

    while i < len(text):
        ch = text[i]
        token_class = classify_char(ch)
        next_state = dfa.get(state, {}).get(token_class)

        if next_state is None:
            next_state = dfa.get(state, {}).get(ch)

        if next_state is None:
            break

        lexeme += ch
        state = next_state
        i += 1

    if state in accepting:
        return lexeme, accepting[state], i
    return None, None, start_index + 1
