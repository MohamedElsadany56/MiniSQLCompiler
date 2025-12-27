import sys
from lexer import tokenize
from parser import Parser
from semantic_analyzer import SemanticAnalyzer

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

    print("\n" + "_"*50)
    print("Mini SQL Compiler - 3 phase Compilation")
    print("_"*50)

    # Phase 1: Lexical Analysis
    print("\n" + "_"*50)
    print("Phase 1: Lexical Analysis")
    print("_"*50)
    
    tokens, lex_errors = tokenize(text)
    
    print("\n-> Tokens")
    for ttype, val, line, col in tokens:
        print(f"{ttype:<12}  {val:<15}  (line {line}, col {col})")
    
    print("\n-> Lexical Errors")
    if lex_errors:
        for err in lex_errors:
            print(err)
        print("\n[!] Lexical errors found. Cannot proceed to syntax analysis.")
        return
    else:
        print("No lexical errors found. ")

    # Phase 2: Syntax Analysis
    print("\n" + "_"*50)
    print("phase 2: Syntax Analysis")
    print("_"*50)
    
    parser = Parser(tokens)
    parse_tree = parser.parse_query()
    
    print("\n-> PARSE TREE")
    print(parse_tree)
    
    print("-> SYNTAX ERRORS")
    if parser.errors:
        for err in parser.errors:
            print(err)
        print("\n[!] Syntax errors found. Cannot proceed to semantic analysis.")
        return
    else:
        print("No syntax errors found. ")

    # Phase 3: Semantic Analysis
    print("\n" + "_"*50)
    print("Phase 3: Semantic Analysis")
    print("_"*50)
    
    analyzer = SemanticAnalyzer(parse_tree)
    success = analyzer.analyze()
    
    print(analyzer.get_symbol_table_dump())
    
    print("\n-> Semantic Errors")
    if not success:
        for err in analyzer.get_errors():
            print(err)
        print("\n ! Semantic errors found. Query is invalid.")
    else:
        print("No semantic errors found. ")
        print("\n" + "_"*50)
        print(" Semantic Analysis Successful. Query is Valid.")
        print("_"*50)
        
        print("\n-> Annotated Parse Tree")
        print("(Parse tree with type annotations and symbol table references)")
        print(analyzer.get_annotated_tree())

    # SUMMARY
    print("\n" + "_"*50)
    print("Compilation Summary")
    print("_"*50)
    print(f"Lexical Errors:   {len(lex_errors)}")
    print(f"Syntax Errors:    {len(parser.errors)}")
    print(f"Semantic Errors:  {len(analyzer.get_errors())}")
    print(f"Status:           {'Success ' if success else 'Failed '}")
    print("_"*50)

if __name__ == "__main__":
    main()
