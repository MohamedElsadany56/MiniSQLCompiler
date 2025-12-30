import sys
import os

# Import your actual main function
from main import main 

# List to store the timeline of execution (preserves order)
execution_timeline = []
# Set to keep track of what we've already seen so we don't record duplicates
seen_signatures = set()

def trace_calls(frame, event, arg):
    """This function is called by Python for every single step."""
    if event == 'call':
        code = frame.f_code
        func_name = code.co_name
        
        # Get the filename to ignore standard python libraries
        filename = code.co_filename
        
        # Filter: Only track files that belong to your project
        if "lexer.py" in filename or "parser.py" in filename or "semantic" in filename or "main.py" in filename:
            
            # Determine Class Name (if it's a method)
            class_name = None
            if 'self' in frame.f_locals:
                class_name = frame.f_locals['self'].__class__.__name__
            
            # Create a pretty string: "ClassName.FunctionName" or just "FunctionName"
            if class_name:
                full_signature = f"{class_name}.{func_name}"
            else:
                full_signature = func_name

            # LOGIC: Only add to the timeline if it's the FIRST time we see it
            # This gives you the "Order of Discovery" without listing 'classify_char' 1000 times.
            if full_signature not in seen_signatures:
                seen_signatures.add(full_signature)
                execution_timeline.append(full_signature)
                
    return trace_calls

if __name__ == "__main__":
    # 1. Start Tracing
    sys.settrace(trace_calls)
    
    # 2. Run your compiler
    # Make sure this file path exists on your computer!
    sys.argv = ["main.py", "samples\\test_semantic_valid.sql"] 
    
    try:
        main()
    except SystemExit:
        pass # Ignore exit calls
    except Exception as e:
        print(f"Runtime Error: {e}")
    
    # 3. Stop Tracing
    sys.settrace(None)

    # 4. Print Report by Order
    print("\n" + "="*40)
    print(" EXECUTION FLOW (Order of First Call)")
    print("="*40)
    
    for i, step in enumerate(execution_timeline):
        print(f"{i+1}. {step}")