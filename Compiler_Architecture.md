# Mini SQL Compiler - Architecture and Flow Diagrams

This document provides a comprehensive visual representation of the three-phase compilation process using Mermaid diagrams.

---

## Table of Contents
1. [Overall Compilation Flow](#overall-compilation-flow)
2. [Phase 01: Lexical Analysis](#phase-01-lexical-analysis)
3. [Phase 02: Syntax Analysis](#phase-02-syntax-analysis)
4. [Phase 03: Semantic Analysis](#phase-03-semantic-analysis)
5. [Data Flow Between Phases](#data-flow-between-phases)
6. [Error Handling Flow](#error-handling-flow)
7. [Symbol Table Management](#symbol-table-management)

---

## Overall Compilation Flow

```mermaid
flowchart TD
    Start([SQL Source File]) --> Lexer[Phase 01: Lexical Analysis]
    Lexer --> LexCheck{Lexical Errors?}
    LexCheck -->|Yes| LexError[Report Lexical Errors<br/>STOP]
    LexCheck -->|No| Tokens[Token Stream]
    
    Tokens --> Parser[Phase 02: Syntax Analysis]
    Parser --> SyntaxCheck{Syntax Errors?}
    SyntaxCheck -->|Yes| SyntaxError[Report Syntax Errors<br/>STOP]
    SyntaxCheck -->|No| ParseTree[Parse Tree]
    
    ParseTree --> Semantic[Phase 03: Semantic Analysis]
    Semantic --> SemanticCheck{Semantic Errors?}
    SemanticCheck -->|Yes| SemanticError[Report Semantic Errors<br/>STOP]
    SemanticCheck -->|No| Success[ Valid Query<br/>Symbol Table Dump<br/>Annotated Parse Tree]
    
    LexError --> Summary[Compilation Summary]
    SyntaxError --> Summary
    SemanticError --> Summary
    Success --> Summary
    Summary --> End([End])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style Success fill:#c8e6c9
    style LexError fill:#ffcdd2
    style SyntaxError fill:#ffcdd2
    style SemanticError fill:#ffcdd2
    style Lexer fill:#bbdefb
    style Parser fill:#c5cae9
    style Semantic fill:#d1c4e9
```

---

## Phase 01: Lexical Analysis

### Lexical Analysis Process Flow

```mermaid
flowchart TD
    Input[SQL Source Code] --> ReadChar[Read Character]
    ReadChar --> Classify[Classify Character]

    Classify --> CheckType{Character Type?}

    CheckType -->|Whitespace| Skip[Skip Character]
    CheckType -->|Comment| HandleComment[Process Comment<br/>SQL comment]
    CheckType -->|Quote| HandleString[String DFA<br/>Match quoted string]
    CheckType -->|Letter| IdentDFA[Identifier DFA<br/>Match letters or underscore]
    CheckType -->|Digit| NumDFA[Number DFA<br/>Match integer or float]
    CheckType -->|Operator| OpDFA[Operator DFA<br/>Match arithmetic or comparison]
    CheckType -->|Delimiter| DelimDFA[Delimiter DFA<br/>Comma Semicolon Parentheses Brackets Braces]
    CheckType -->|Other| Error[Lexical Error<br/>Invalid Character]

    IdentDFA --> IsKeyword{Is Keyword?}
    IsKeyword -->|Yes| KeywordToken[Create KEYWORD Token]
    IsKeyword -->|No| IdToken[Create IDENTIFIER Token]

    NumDFA --> NumType{Has Decimal Point?}
    NumType -->|Yes| FloatToken[Create FLOAT Token]
    NumType -->|No| IntToken[Create INTEGER Token]

    OpDFA --> OpToken[Create OPERATOR Token]
    HandleString --> StrToken[Create STRING Token]
    DelimDFA --> DelimToken[Create DELIMITER Token]
    HandleComment --> Skip

    KeywordToken --> AddToken[Add Token to List<br/>Store type value line column]
    IdToken --> AddToken
    FloatToken --> AddToken
    IntToken --> AddToken
    OpToken --> AddToken
    StrToken --> AddToken
    DelimToken --> AddToken
    Error --> ErrorList[Add to Error List]

    Skip --> MoreChars{More Characters?}
    AddToken --> MoreChars
    ErrorList --> MoreChars

    MoreChars -->|Yes| ReadChar
    MoreChars -->|No| Output[Output Token List and Error List]

    style Input fill:#e1f5e1
    style Output fill:#c8e6c9
    style Error fill:#ffcdd2
    style ErrorList fill:#ffcdd2

```

### DFA State Machines

```mermaid
stateDiagram-v2
    [*] --> Start
    
    state "Identifier DFA" as ID {
        [*] --> ID_Start
        ID_Start --> ID_Valid: Letter or _
        ID_Valid --> ID_Valid: Letter, Digit, or _
        ID_Valid --> [*]: Accept
    }
    
    state "Number DFA" as NUM {
        [*] --> NUM_Start
        NUM_Start --> Integer: Digit
        Integer --> Integer: Digit
        Integer --> Decimal: .
        Integer --> [*]: Accept (INTEGER)
        Decimal --> Float: Digit
        Float --> Float: Digit
        Float --> [*]: Accept (FLOAT)
    }
    
    state "Operator DFA" as OP {
        [*] --> OP_Start
        OP_Start --> Single: +, -, *, /, =, <, >, !
        Single --> Double: =, >
        Single --> [*]: Accept (OPERATOR)
        Double --> [*]: Accept (OPERATOR)
    }
    
    Start --> ID
    Start --> NUM
    Start --> OP
```

---

## Phase 02: Syntax Analysis

### Syntax Analysis Process Flow

```mermaid
flowchart TD
    Input[Token Stream] --> InitParser[Initialize Parser<br/>pos = 0, errors = []]
    InitParser --> ParseQuery[parse_query]
    
    ParseQuery --> CheckToken{More Tokens?}
    CheckToken -->|No| Done[Return Parse Tree]
    CheckToken -->|Yes| ParseStmt[parse_statement]
    
    ParseStmt --> StmtType{Statement Type?}
    
    StmtType -->|CREATE| ParseCreate[parse_create_stmt]
    StmtType -->|INSERT| ParseInsert[parse_insert_stmt]
    StmtType -->|SELECT| ParseSelect[parse_select_stmt]
    StmtType -->|UPDATE| ParseUpdate[parse_update_stmt]
    StmtType -->|DELETE| ParseDelete[parse_delete_stmt]
    StmtType -->|Unknown| SyntaxErr[Syntax Error<br/>Unexpected Statement]
    
    ParseCreate --> CreateTree[Build CREATE Tree<br/>- Table Name<br/>- Column Definitions<br/>- Data Types]
    ParseInsert --> InsertTree[Build INSERT Tree<br/>- Table Name<br/>- Value List]
    ParseSelect --> SelectTree[Build SELECT Tree<br/>- Column List<br/>- Table Name<br/>- WHERE Clause]
    ParseUpdate --> UpdateTree[Build UPDATE Tree<br/>- Table Name<br/>- SET Clause<br/>- WHERE Clause]
    ParseDelete --> DeleteTree[Build DELETE Tree<br/>- Table Name<br/>- WHERE Clause]
    
    CreateTree --> MatchSemi[Match SEMICOLON]
    InsertTree --> MatchSemi
    SelectTree --> MatchSemi
    UpdateTree --> MatchSemi
    DeleteTree --> MatchSemi
    
    SyntaxErr --> PanicMode[Panic Mode Recovery<br/>Skip to next SEMICOLON]
    PanicMode --> AddError[Add to Error List]
    
    MatchSemi --> AddNode[Add Statement Node<br/>to Parse Tree]
    AddError --> CheckToken
    AddNode --> CheckToken
    
    Done --> Output[Output:<br/>- Parse Tree<br/>- Syntax Errors]
    
    style Input fill:#e1f5e1
    style Output fill:#c8e6c9
    style SyntaxErr fill:#ffcdd2
    style AddError fill:#ffcdd2
```

### Parse Tree Structure

```mermaid
graph TD
    Query[Query]
    Query --> Stmt1[Statement 1]
    Query --> Stmt2[Statement 2]
    Query --> StmtN[Statement N]
    
    Stmt1 --> Create[CreateStmt]
    Create --> CreateKW[KEYWORD: CREATE]
    Create --> TableKW[KEYWORD: TABLE]
    Create --> TableName[IDENTIFIER: TableName]
    Create --> LParen[LPAREN]
    Create --> ColDef1[ColumnDef]
    Create --> ColDef2[ColumnDef]
    Create --> RParen[RPAREN]
    Create --> Semi1[SEMICOLON]
    
    ColDef1 --> ColName1[IDENTIFIER: column_name]
    ColDef1 --> ColType1[KEYWORD: INT/FLOAT/TEXT]
    
    Stmt2 --> Insert[InsertStmt]
    Insert --> InsertKW[KEYWORD: INSERT]
    Insert --> IntoKW[KEYWORD: INTO]
    Insert --> TableName2[IDENTIFIER: TableName]
    Insert --> ValuesKW[KEYWORD: VALUES]
    Insert --> LParen2[LPAREN]
    Insert --> Val1[Value: 'text']
    Insert --> Val2[Value: 123]
    Insert --> RParen2[RPAREN]
    Insert --> Semi2[SEMICOLON]
    
    StmtN --> Select[SelectStmt]
    Select --> SelectKW[KEYWORD: SELECT]
    Select --> Col1[IDENTIFIER: col1]
    Select --> Col2[IDENTIFIER: col2]
    Select --> FromKW[KEYWORD: FROM]
    Select --> TableName3[IDENTIFIER: TableName]
    Select --> Where[WhereClause]
    Select --> Semi3[SEMICOLON]
    
    Where --> WhereKW[KEYWORD: WHERE]
    Where --> Condition[Condition]
    Condition --> Term[Term]
    Term --> Comp[Comparison]
    Comp --> Left[Operand: age]
    Comp --> Op[OPERATOR: >]
    Comp --> Right[Operand: 18]
    
    style Query fill:#c5cae9
    style Create fill:#e1bee7
    style Insert fill:#f8bbd0
    style Select fill:#c5e1a5
```

---

## Phase 03: Semantic Analysis

### Semantic Analysis Process Flow

```mermaid
flowchart TD
    Input[Parse Tree] --> InitAnalyzer[Initialize Semantic Analyzer<br/>symbol_table = {}<br/>errors = []]
    InitAnalyzer --> Traverse[Traverse Parse Tree]
    
    Traverse --> NodeType{Node Type?}
    
    NodeType -->|CreateStmt| AnalyzeCreate[Analyze CREATE TABLE]
    NodeType -->|InsertStmt| AnalyzeInsert[Analyze INSERT]
    NodeType -->|SelectStmt| AnalyzeSelect[Analyze SELECT]
    NodeType -->|UpdateStmt| AnalyzeUpdate[Analyze UPDATE]
    NodeType -->|DeleteStmt| AnalyzeDelete[Analyze DELETE]
    NodeType -->|Other| Continue[Continue Traversing]
    
    AnalyzeCreate --> CheckRedecl{Table Already<br/>Exists?}
    CheckRedecl -->|Yes| ErrRedecl[Semantic Error:<br/>Table Redeclaration]
    CheckRedecl -->|No| ValidTypes{Valid Data<br/>Types?}
    ValidTypes -->|No| ErrType[Semantic Error:<br/>Invalid Data Type]
    ValidTypes -->|Yes| AddTable[Add Table to<br/>Symbol Table]
    
    AnalyzeInsert --> CheckTable1{Table<br/>Exists?}
    CheckTable1 -->|No| ErrNoTable1[Semantic Error:<br/>Table Not Found]
    CheckTable1 -->|Yes| CheckCount{Value Count<br/>= Column Count?}
    CheckCount -->|No| ErrCount[Semantic Error:<br/>Count Mismatch]
    CheckCount -->|Yes| CheckTypes{Value Types<br/>Match?}
    CheckTypes -->|No| ErrTypeMismatch[Semantic Error:<br/>Type Mismatch]
    CheckTypes -->|Yes| AnnotateInsert[Annotate Values<br/>with Types]
    
    AnalyzeSelect --> CheckTable2{Table<br/>Exists?}
    CheckTable2 -->|No| ErrNoTable2[Semantic Error:<br/>Table Not Found]
    CheckTable2 -->|Yes| CheckCols{Columns<br/>Exist?}
    CheckCols -->|No| ErrNoCols[Semantic Error:<br/>Column Not Found]
    CheckCols -->|Yes| AnalyzeWhere1[Analyze WHERE Clause<br/>Type Compatibility]
    AnalyzeWhere1 --> AnnotateSelect[Annotate Columns<br/>with Types]
    
    AnalyzeUpdate --> CheckTable3{Table<br/>Exists?}
    CheckTable3 -->|No| ErrNoTable3[Semantic Error:<br/>Table Not Found]
    CheckTable3 -->|Yes| CheckUpdateCol{Column<br/>Exists?}
    CheckUpdateCol -->|No| ErrNoCol[Semantic Error:<br/>Column Not Found]
    CheckUpdateCol -->|Yes| CheckUpdateType{Value Type<br/>Matches?}
    CheckUpdateType -->|No| ErrUpdateType[Semantic Error:<br/>Type Mismatch]
    CheckUpdateType -->|Yes| AnalyzeWhere2[Analyze WHERE Clause]
    AnalyzeWhere2 --> AnnotateUpdate[Annotate Update<br/>with Types]
    
    AnalyzeDelete --> CheckTable4{Table<br/>Exists?}
    CheckTable4 -->|No| ErrNoTable4[Semantic Error:<br/>Table Not Found]
    CheckTable4 -->|Yes| AnalyzeWhere3[Analyze WHERE Clause]
    AnalyzeWhere3 --> AnnotateDelete[Annotate Delete<br/>with Types]
    
    ErrRedecl --> AddErr[Add Error to List]
    ErrType --> AddErr
    ErrNoTable1 --> AddErr
    ErrCount --> AddErr
    ErrTypeMismatch --> AddErr
    ErrNoTable2 --> AddErr
    ErrNoCols --> AddErr
    ErrNoTable3 --> AddErr
    ErrNoCol --> AddErr
    ErrUpdateType --> AddErr
    ErrNoTable4 --> AddErr
    
    AddTable --> MoreNodes{More Nodes?}
    AnnotateInsert --> MoreNodes
    AnnotateSelect --> MoreNodes
    AnnotateUpdate --> MoreNodes
    AnnotateDelete --> MoreNodes
    Continue --> MoreNodes
    AddErr --> MoreNodes
    
    MoreNodes -->|Yes| Traverse
    MoreNodes -->|No| CheckErrors{Errors<br/>Found?}
    
    CheckErrors -->|Yes| ErrorOutput[Output:<br/>- Error List<br/>- Symbol Table<br/>Status: FAILED]
    CheckErrors -->|No| SuccessOutput[Output:<br/>- Symbol Table Dump<br/>- Annotated Parse Tree<br/>Status: SUCCESS]
    
    ErrorOutput --> End[End]
    SuccessOutput --> End
    
    style Input fill:#e1f5e1
    style SuccessOutput fill:#c8e6c9
    style ErrorOutput fill:#ffcdd2
    style ErrRedecl fill:#ffcdd2
    style ErrType fill:#ffcdd2
    style ErrNoTable1 fill:#ffcdd2
    style ErrCount fill:#ffcdd2
    style ErrTypeMismatch fill:#ffcdd2
    style ErrNoCols fill:#ffcdd2
    style End fill:#e1f5e1
```

### Type Checking Flow

```mermaid
flowchart TD
    Start[Value or Operand] --> InferType[Infer Type from Token]
    
    InferType --> CheckFormat{Token Format?}
    CheckFormat -->|'...'| TextType[Type: TEXT]
    CheckFormat -->|Contains '.'| FloatType[Type: FLOAT]
    CheckFormat -->|Integer| IntType[Type: INT]
    
    TextType --> LookupExpected[Lookup Expected Type<br/>from Symbol Table]
    FloatType --> LookupExpected
    IntType --> LookupExpected
    
    LookupExpected --> Compare{Types<br/>Compatible?}
    
    Compare -->|Exact Match| Success[ Type Valid]
    Compare -->|INT ↔ FLOAT| NumCompat[ Numeric Compatible]
    Compare -->|Mismatch| TypeError[ Type Mismatch Error]
    
    Success --> Annotate[Annotate Node<br/>with Type Info]
    NumCompat --> Annotate
    TypeError --> ReportError[Report Semantic Error<br/>with Line & Column]
    
    Annotate --> Done[Continue Analysis]
    ReportError --> Done
    
    style Start fill:#e1f5e1
    style Success fill:#c8e6c9
    style NumCompat fill:#c8e6c9
    style TypeError fill:#ffcdd2
    style ReportError fill:#ffcdd2
```

---

## Data Flow Between Phases

```mermaid
flowchart LR
    subgraph Input
        SQL[SQL Source File<br/>*.sql]
    end
    
    subgraph Phase1[Phase 01: Lexical Analysis]
        Lexer[Lexer]
        DFA[DFA Engines]
        Lexer --> DFA
    end
    
    subgraph Phase1Output[Phase 01 Output]
        Tokens[Token Stream<br/>type, value, line, col]
        LexErrors[Lexical Errors List]
    end
    
    subgraph Phase2[Phase 02: Syntax Analysis]
        Parser[Parser]
        TreeBuilder[Parse Tree Builder]
        Parser --> TreeBuilder
    end
    
    subgraph Phase2Output[Phase 02 Output]
        ParseTree[Parse Tree<br/>Hierarchical Structure]
        SynErrors[Syntax Errors List]
    end
    
    subgraph Phase3[Phase 03: Semantic Analysis]
        Analyzer[Semantic Analyzer]
        SymbolTable[Symbol Table]
        TypeChecker[Type Checker]
        Analyzer --> SymbolTable
        Analyzer --> TypeChecker
    end
    
    subgraph Phase3Output[Phase 03 Output]
        AnnotatedTree[Annotated Parse Tree<br/>With Type Info]
        SymbolDump[Symbol Table Dump]
        SemErrors[Semantic Errors List]
    end
    
    subgraph FinalOutput[Final Output]
        Report[Compilation Report<br/>- All Errors<br/>- Symbol Table<br/>- Status]
    end
    
    SQL --> Lexer
    DFA --> Tokens
    DFA --> LexErrors
    Tokens --> Parser
    TreeBuilder --> ParseTree
    TreeBuilder --> SynErrors
    ParseTree --> Analyzer
    TypeChecker --> AnnotatedTree
    SymbolTable --> SymbolDump
    Analyzer --> SemErrors
    
    LexErrors --> Report
    SynErrors --> Report
    SemErrors --> Report
    SymbolDump --> Report
    AnnotatedTree --> Report
    
    style SQL fill:#e1f5e1
    style Tokens fill:#fff9c4
    style ParseTree fill:#fff9c4
    style AnnotatedTree fill:#fff9c4
    style Report fill:#c8e6c9
    style LexErrors fill:#ffcdd2
    style SynErrors fill:#ffcdd2
    style SemErrors fill:#ffcdd2
```

---

## Error Handling Flow

```mermaid
flowchart TD
    Start[Start Compilation] --> Phase1[Phase 01:<br/>Lexical Analysis]
    
    Phase1 --> Lex{Lexical<br/>Errors?}
    Lex -->|Yes| LexReport[Report Lexical Errors<br/>- Invalid characters<br/>- Unclosed comments<br/>- Invalid strings]
    Lex -->|No| Phase2[Phase 02:<br/>Syntax Analysis]
    
    Phase2 --> Syn{Syntax<br/>Errors?}
    Syn -->|Yes| SynReport[Report Syntax Errors<br/>- Missing tokens<br/>- Unexpected tokens<br/>- Grammar violations]
    Syn -->|No| Phase3[Phase 03:<br/>Semantic Analysis]
    
    Phase3 --> Sem{Semantic<br/>Errors?}
    Sem -->|Yes| SemReport[Report Semantic Errors<br/>- Table not found<br/>- Column not found<br/>- Type mismatch<br/>- Redeclaration]
    Sem -->|No| ValidQuery[ Valid Query]
    
    LexReport --> Summary[Compilation Summary]
    SynReport --> Summary
    SemReport --> Summary
    ValidQuery --> Success[Display Results:<br/>- Symbol Table<br/>- Annotated Tree<br/>- Success Message]
    
    Success --> Summary
    Summary --> End[End]
    
    style Start fill:#e1f5e1
    style ValidQuery fill:#c8e6c9
    style Success fill:#c8e6c9
    style LexReport fill:#ffcdd2
    style SynReport fill:#ffcdd2
    style SemReport fill:#ffcdd2
    style End fill:#e1f5e1
```

### Error Message Format

```mermaid
graph LR
    Error[Error Detected] --> Type[Error Type]
    Type --> Location[Line & Column]
    Location --> Description[Detailed Description]
    Description --> Context[Expected vs Found]
    Context --> Output[Formatted Error Message]
    
    style Error fill:#ffcdd2
    style Output fill:#ffcdd2
```

**Example Error Messages:**

```
Lexical Error: Unexpected character '@' at 5:12
Syntax Error at 7:15 - Expected 'INTO', found 'FORM'
Semantic Error: Table 'Users' not found (Line 10, Column 14)
Semantic Error: Type mismatch at line 15, position 24. Column 'age' is defined as INT, but a TEXT literal was provided for insertion (Line 15, Column 24)
```

---

## Symbol Table Management

### Symbol Table Structure

```mermaid
graph TD
    SymbolTable[Symbol Table]
    
    SymbolTable --> Table1[Table: Students]
    SymbolTable --> Table2[Table: Courses]
    SymbolTable --> TableN[Table: ...]
    
    Table1 --> T1Info[Metadata]
    T1Info --> T1Line[Line: 5]
    T1Info --> T1Col[Column: 14]
    T1Info --> T1Cols[Columns List]
    
    T1Cols --> Col1[name: TEXT]
    T1Cols --> Col2[age: INT]
    T1Cols --> Col3[gpa: FLOAT]
    
    Table2 --> T2Info[Metadata]
    T2Info --> T2Line[Line: 13]
    T2Info --> T2Col[Column: 14]
    T2Info --> T2Cols[Columns List]
    
    T2Cols --> Col4[course_name: TEXT]
    T2Cols --> Col5[credits: INT]
    
    style SymbolTable fill:#d1c4e9
    style Table1 fill:#e1bee7
    style Table2 fill:#e1bee7
    style Col1 fill:#c8e6c9
    style Col2 fill:#c8e6c9
    style Col3 fill:#c8e6c9
    style Col4 fill:#c8e6c9
    style Col5 fill:#c8e6c9
```

### Symbol Table Operations

```mermaid
sequenceDiagram
    participant Parser as Parse Tree
    participant Analyzer as Semantic Analyzer
    participant SymTable as Symbol Table
    participant Errors as Error List
    
    Parser->>Analyzer: Process CREATE TABLE
    Analyzer->>SymTable: table_exists("Students")?
    SymTable-->>Analyzer: False
    Analyzer->>SymTable: add_table("Students", [...])
    SymTable-->>Analyzer: Success
    
    Parser->>Analyzer: Process INSERT INTO Students
    Analyzer->>SymTable: table_exists("Students")?
    SymTable-->>Analyzer: True
    Analyzer->>SymTable: get_table("Students")
    SymTable-->>Analyzer: {columns: [(name, TEXT), (age, INT)], ...}
    Analyzer->>Analyzer: Type Check Values
    
    alt Type Mismatch
        Analyzer->>Errors: Add Error: Type Mismatch
    else Types Valid
        Analyzer->>Parser: Annotate with Types
    end
    
    Parser->>Analyzer: Process SELECT FROM Students
    Analyzer->>SymTable: column_exists("Students", "name")?
    SymTable-->>Analyzer: True
    Analyzer->>SymTable: get_column_type("Students", "name")
    SymTable-->>Analyzer: TEXT
    Analyzer->>Parser: Annotate name with TEXT
```

---

## Complete Compilation Sequence

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant Lexer
    participant Parser
    participant Semantic
    participant SymTable
    
    User->>Main: python main.py file.sql
    Main->>Lexer: tokenize(source_code)
    
    Lexer->>Lexer: Read characters
    Lexer->>Lexer: Apply DFAs
    Lexer->>Lexer: Classify tokens
    Lexer-->>Main: tokens[], errors[]
    
    alt Lexical Errors
        Main->>User: Display Lexical Errors
        Main->>Main: STOP
    else No Errors
        Main->>Parser: Parser(tokens)
        Parser->>Parser: parse_query()
        Parser->>Parser: Build parse tree
        Parser-->>Main: parse_tree, errors[]
        
        alt Syntax Errors
            Main->>User: Display Syntax Errors
            Main->>Main: STOP
        else No Errors
            Main->>Semantic: SemanticAnalyzer(parse_tree)
            Semantic->>Semantic: analyze()
            
            loop For each statement
                Semantic->>SymTable: Check/Add tables
                Semantic->>SymTable: Verify columns
                Semantic->>Semantic: Type checking
            end
            
            Semantic-->>Main: success, errors[], symbol_table
            
            alt Semantic Errors
                Main->>User: Display Semantic Errors
                Main->>User: Display Symbol Table
            else No Errors
                Main->>User: SUCCESS
                Main->>User: Display Symbol Table
                Main->>User: Display Annotated Tree
            end
        end
    end
    
    Main->>User: Compilation Summary
```

---

## Module Interactions

```mermaid
graph TB
    subgraph "Phase 01 Modules"
        DFA[dfa_definitions.py<br/>- Character Classification<br/>- DFA Definitions]
        Runner[dfa_runner.py<br/>- DFA Simulation Engine]
        Lexer[lexer.py<br/>- Tokenization Logic]
        
        DFA --> Lexer
        Runner --> Lexer
    end
    
    subgraph "Phase 02 Modules"
        Parser[parser.py<br/>- ParseNode Class<br/>- Parser Class<br/>- Grammar Rules]
    end
    
    subgraph "Phase 03 Modules"
        Semantic[semantic_analyzer.py<br/>- SymbolTable Class<br/>- SemanticAnalyzer Class<br/>- Type Checking]
    end
    
    subgraph "Integration"
        Main[main.py<br/>- Entry Point<br/>- Phase Coordination<br/>- Output Display]
    end
    
    Lexer -->|tokens, errors| Main
    Main -->|tokens| Parser
    Parser -->|parse_tree, errors| Main
    Main -->|parse_tree| Semantic
    Semantic -->|results, errors| Main
    
    style DFA fill:#bbdefb
    style Runner fill:#bbdefb
    style Lexer fill:#bbdefb
    style Parser fill:#c5cae9
    style Semantic fill:#d1c4e9
    style Main fill:#fff9c4
```

---

## Summary

This architecture document provides complete visual representations of:

- **Overall Flow**: Three-phase compilation process
- **Phase 01**: DFA-based lexical analysis with token generation
- **Phase 02**: Recursive descent parsing with parse tree construction
- **Phase 03**: Symbol table management and semantic verification
- **Data Flow**: How information passes between phases
- **Error Handling**: Comprehensive error detection and reporting
- **Symbol Table**: Structure and operations for metadata management

