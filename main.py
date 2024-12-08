#!/usr/bin/env python3
import sys
import re
from SudoLangADT import *  # ADT definitions
import sudolang  # Import lexer and parser specifications from sudolang
from interpreter import eval_program  # Evaluation function

# A dictionary to store variables and their values
variables = {}

translated_string = ""

def concrete2abstract(s: str, parser) -> Program:
    """
    Convert a concrete program (string) into an abstract syntax tree (ADT).
    """
    pattern = re.compile("[^ \t]+")
    if pattern.search(s):
        try:
            # Use the parser to parse the string
            parser.parse(s)
            return sudolang.global_ast  # Assuming the parser stores the result in global_ast
        except Exception as e:
            print("Unknown Error occurred (this is normally caused by a syntax error)")
            raise e
    return None

lineNumber = 1

def start_repl():

    print("Welcome to the SudoLang Interpreter!")
    print("Type 'exit' to quit.")

    global lineNumber
    
    while True:
        try:
            # Get user input
            input_string = input(f"--[ {lineNumber}. ")
            
            # Exit condition
            if input_string.lower() == 'exit':
                print("Exiting SudoLang.")
                break
            
            # Parse the input string into the ADT
            ast = concrete2abstract(input_string, sudolang.parser)
            
            if ast:
                # Interpret the program and update variables
                result = eval_program(ast, variables)
                if result:
                    print(result)
                lineNumber += 1
            
            else:
                print(f'"{input_string}" is not a valid program.')
        
        except KeyboardInterrupt:
            # Handle Ctrl+C: Cancel current input and continue the loop
            print()
            continue
        
        except EOFError:
            # Handle Ctrl+D: Exit the REPL
            print("\nExiting SudoLang.")
            break
        
        except Exception as e:
            print(f"Error: {e}")

def main():
    """
    Main function to handle command-line arguments for the SudoLang interpreter.
    """
    iFlag = False
    args = sys.argv[1:]

    # Parse command-line arguments for -i option
    for arg in args:
        if arg == '-i':
            iFlag = True
        else:
            print(f"Invalid option: {arg}")
            sys.exit(1)

    if len(sys.argv) == 2 and sys.argv[1] == '-i':
        print('SudoLang> ', flush=True, end='')

    for line in sys.stdin:
        line = line.strip()  # Remove trailing newline
        try:
            # Parse the line into the ADT
            ast = concrete2abstract(line, sudolang.parser)
            
            if ast:
                # Interpret the program and update variables
                result = eval_program(ast, variables)
                if result:
                    print(result)
            else:
                print(f'"{line}" is not a program')

            # Keep the REPL prompt when in interactive mode (-i)
            if len(sys.argv) == 2 and sys.argv[1] == '-i':
                print('SudoLang> ', flush=True, end='')

        except SyntaxError:
            print(f'"{line}" contains lexical units which are not lexemes and is not a program.')
        except EOFError:
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(-1)

if __name__ == "__main__":
    # Call start_repl for interactive mode
    #if '-i' in sys.argv:
    #    start_repl()
    #else:
    #    # Call main function if not in interactive mode
    #    main()
    start_repl()
