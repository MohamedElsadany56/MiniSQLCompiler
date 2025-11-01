import sys
from lexer import tokenize

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py inputfile.sql")
        return

    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found.")
        return

    tokens, errors = tokenize(text)

    print("\n=>> TOKENS  <<=")
    for ttype, val, line, col in tokens:
        print(f"{ttype:<12}  {val:<15}  (line {line}, col {col})")

    print("\n=>> SYMBOL TABLE (Identifiers) <<=")
    identifiers = sorted({val for ttype, val, _, _ in tokens if ttype == 'IDENTIFIER'})
    for identifier in identifiers:
        print(identifier)

    print("\n=>> ERRORS  <<=")
    if errors:
        for err in errors:
            print(err)
    else:
        print("No lexical errors found.")

if __name__ == "__main__":
    main()
