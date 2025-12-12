import sys
import os
from lexer import tokenize
from parser import Parser

#  Color Codes 
class Colors:
    RED = '\033[91m'      # Bright Red for Errors
    YELLOW = '\033[93m'   # Yellow for Suggestions/Details
    GREEN = '\033[92m'    # Green for Success headers
    BLUE = '\033[94m'     # Blue for Tokens
    RESET = '\033[0m'     # Reset to default

    # Enable colors in Windows CMD
    if os.name == 'nt':
        os.system('color')

def print_colored_error(error_msg):
    """
    Parses the error string to colorize the output.
    """
    if " - " in error_msg:
        head, suggestion = error_msg.split(" - ", 1)
        print(f"{Colors.RED} {head}{Colors.RESET} - {Colors.YELLOW}{suggestion}{Colors.RESET}")
    else:
        print(f"{Colors.RED} {error_msg}{Colors.RESET}")

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.YELLOW}Usage: python main.py <input_file.sql>{Colors.RESET}")
        return

    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File '{sys.argv[1]}' not found.{Colors.RESET}")
        return

    #  lexical analysis 
    print(f"\n{Colors.GREEN}  1: TOKENS {Colors.RESET}")
    tokens, lex_errors = tokenize(text)
    
    for t in tokens:
        print(f"{Colors.BLUE}{t[0]:<12}{Colors.RESET} {t[1]:<20} (Line {t[2]}, Col {t[3]})")
    
    if lex_errors:
        print(f"\n{Colors.RED} LEXICAL ERRORS {Colors.RESET}")
        for e in lex_errors: 
            print_colored_error(e)
        print(f"\n{Colors.RED}Aborting Parse due to Lexical Errors.{Colors.RESET}")
        return

    # syntax analysis
    print(f"\n{Colors.GREEN} 2: Parse Tree {Colors.RESET}")
    if not tokens:
        print(f"{Colors.YELLOW}No tokens to parse.{Colors.RESET}")
        return

    parser = Parser(tokens)
    
    # parse_query 
    tree = parser.parse_query()
    
    # Print the Tree
    print(tree)

    print(f"\n{Colors.GREEN} ERROR REPORT {Colors.RESET}")
    if parser.errors:
        for e in parser.errors:
            print_colored_error(e)
    else:
        print(f"{Colors.GREEN} No syntax errors found. Parse Successful.{Colors.RESET}")

if __name__ == "__main__":
    main()