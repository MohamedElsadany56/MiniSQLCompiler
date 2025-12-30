import sys
import os
from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

# Colors for terminal output
class Colors:
    RED = '\033[91m'      # Errors
    YELLOW = '\033[93m'   # Warnings or details
    GREEN = '\033[92m'    # Success or headers
    BLUE = '\033[94m'     # Tokens or info
    CYAN = '\033[96m'     # Phase titles
    RESET = '\033[0m'

    # Enable colors on windows
    if os.name == 'nt':
        os.system('color')


def print_colored_error(error_msg):
    """
    Colorize errors that contain suggestions.
    Format: error - suggestion
    """
    if " - " in error_msg:
        head, suggestion = error_msg.split(" - ", 1)
        print(f"{Colors.RED}{head}{Colors.RESET} - {Colors.YELLOW}{suggestion}{Colors.RESET}")
    else:
        print(f"{Colors.RED}{error_msg}{Colors.RESET}")


def print_separator(title=None):
    line = "_" * 55
    if title:
        print(f"\n{Colors.CYAN}{line}")
        print(f"{title}")
        print(f"{line}{Colors.RESET}")
    else:
        print(f"{Colors.CYAN}{line}{Colors.RESET}")


def main():
    if len(sys.argv) < 2:
        print(f"{Colors.YELLOW}Usage: python main.py <inputfile.sql>{Colors.RESET}")
        return

    try:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"{Colors.RED}Error: file '{sys.argv[1]}' not found.{Colors.RESET}")
        return

    print_separator("Mini sql compiler - 3 phase compilation")

    # Phase 1: lexical analysis
    print_separator("Phase 1: lexical analysis")

    tokens, lex_errors = tokenize(text)

    print(f"\n{Colors.GREEN}-> Tokens{Colors.RESET}")
    for ttype, val, line, col in tokens:
        print(
            f"{Colors.BLUE}{ttype:<12}{Colors.RESET} "
            f"{val:<15} "
            f"(Line {line}, col {col})"
        )

    print(f"\n{Colors.GREEN}-> Lexical errors{Colors.RESET}")
    if lex_errors:
        for err in lex_errors:
            print_colored_error(err)
        print(f"\n{Colors.RED} ! Compilation stopped due to lexical errors.{Colors.RESET}")
        return
    else:
        print(f"{Colors.GREEN}No lexical errors found.{Colors.RESET}")

    # Phase 2: syntax analysis
    print_separator("Phase 2: syntax analysis")

    parser = Parser(tokens)
    parse_tree = parser.parse_query()

    print(f"\n{Colors.GREEN}-> Parse tree{Colors.RESET}")
    print(parse_tree)

    print(f"\n{Colors.GREEN}-> Syntax errors{Colors.RESET}")
    if parser.errors:
        for err in parser.errors:
            print_colored_error(err)
        print(f"\n{Colors.RED} ! Compilation stopped due to syntax errors.{Colors.RESET}")
        return
    else:
        print(f"{Colors.GREEN}No syntax errors found.{Colors.RESET}")

    # Phase 3: semantic analysis
    print_separator("Phase 3: semantic analysis")

    analyzer = SemanticAnalyzer(parse_tree)
    success = analyzer.analyze()

    print(f"\n{Colors.GREEN}-> Symbol table{Colors.RESET}")
    print(analyzer.get_symbol_table_dump())

    print(f"\n{Colors.GREEN}-> Semantic errors{Colors.RESET}")
    if not success:
        for err in analyzer.get_errors():
            print_colored_error(err)
        print(f"\n{Colors.RED} ! Semantic analysis failed. Query is invalid.{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}No semantic errors found.{Colors.RESET}")
        print_separator("Semantic analysis successful")
        print(f"{Colors.GREEN}-> Annotated parse tree{Colors.RESET}")
        print(analyzer.get_annotated_tree())

    # Summary
    print_separator("Compilation summary")
    print(f"{Colors.BLUE}Lexical errors : {len(lex_errors)}{Colors.RESET}")
    print(f"{Colors.BLUE}Syntax errors  : {len(parser.errors)}{Colors.RESET}")
    print(f"{Colors.BLUE}Semantic errors: {len(analyzer.get_errors())}{Colors.RESET}")
    print(
        f"{Colors.GREEN if success else Colors.RED}"
        f"Status: {'Success' if success else 'Failed'}"
        f"{Colors.RESET}"
    )
    print_separator()


if __name__ == "__main__":
    main()
