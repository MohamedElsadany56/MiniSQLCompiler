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
        
        filename = code.co_filename
        
        # selectively trace only relevant files
        if "lexer.py" in filename or "parser.py" in filename or "semantic" in filename or "main.py" in filename:
            
            
            class_name = None
            if 'self' in frame.f_locals:
                class_name = frame.f_locals['self'].__class__.__name__
            
            # Create a pretty string: "ClassName.FunctionName"
            if class_name:
                full_signature = f"{class_name}.{func_name}"
            else:
                full_signature = func_name

            # only add to the timeline if it's the FIRST time we see it
            if full_signature not in seen_signatures:
                seen_signatures.add(full_signature)
                execution_timeline.append(full_signature)
                
    return trace_calls

if __name__ == "__main__":
    sys.settrace(trace_calls)
    sys.argv = ["main.py", "samples\\test_semantic_valid.sql"] 
    
    try:
        main()
    except SystemExit:
        pass # Ignore exit calls
    except Exception as e:
        print(f"Runtime Error: {e}")
    
    #  Stop 
    sys.settrace(None)


    print("\n" + "="*40)
    print(" Execution Flow (order of first call)")
    print("="*40)
    
    for i, step in enumerate(execution_timeline):
        print(f"{i+1}. {step}")