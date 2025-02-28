#!/usr/bin/env python3
import sys
import re
import readline
import atexit
import os

from BanterADT import *
import banterlang
from interpreter import eval_program

# Global state
variables = {}
context = []
program_history = []  # Store only valid commands

HISTORY_FILE = os.path.expanduser('~/.banter_history')

def init_readline():
    if not os.path.exists(HISTORY_FILE):
        try:
            open(HISTORY_FILE, 'w').close()
        except IOError:
            pass

    try:
        readline.read_history_file(HISTORY_FILE)
    except IOError:
        pass

    readline.set_history_length(1000)
    atexit.register(readline.write_history_file, HISTORY_FILE)

def concrete2abstract(s: str, parser) -> Program:
    try:
        parser.parse(s)
        return banterlang.global_ast
    except Exception as e:
        print("Syntax error in input")
        return None

def process_input(input_string, filename=None):
    """Process the input and evaluate, maintaining program context."""

    try:
        ast = concrete2abstract(input_string, banterlang.parser)
        
        if ast is None:
            return False  # Indicate parsing failure
        
        if isinstance(ast, list):
            program = ast
        else:
            program = [ast]
            
        try:
                
            # Update program context
            if not context:
                context.insert(0, program)
                
            # Now evaluate the full program
            result = eval_program(program, variables, context)

            if result is not None:
                print(result)
                # If evaluation succeeded, add to program history

            if isinstance(ast, list):
                program_history.extend(ast)
            else:
                program_history.append(ast)

            return True
            
        except Exception as e:
            print(f"Execution error: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def start_repl(first=True, filename=None):
    init_readline()

    if first:
        print("Welcome to the Banter Interpreter!\n")
        print("Type 'exit' to quit.")
        print("Type 'clear' to reset program context.")
        print("Type 'history' to view valid command history.\n")
    
    if filename:
        try:
            with open(filename, 'r') as file:
                content = file.read()
                process_input(content, filename)
            if '-i' in sys.argv:
                print()
                start_repl(first=False)
            return
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            return

    while True:
        try:
            input_lines = []
            indent_level = 0
            in_conditional = False
            
            while True:
                prompt = "... " if in_conditional else "--[ "
                
                try:
                    line = input(prompt)
                    if line.strip():
                        readline.add_history(line)
                except EOFError:
                    print("\n\nExiting Banter.")
                    exit()
                
                # Handle special commands
                if line.strip().lower() == 'exit':
                    print("\nExiting Banter.")
                    exit()
                elif line.strip().lower() == 'clear':
                    program_history.clear()
                    context.clear()
                    variables.clear()
                    print("Program context cleared.")
                    break
                elif line.strip().lower() == 'history':
                    print("\nValid command history:")
                    for i, cmd in enumerate(program_history, 1):
                        print(f"{i}.{(lambda x: "  " if x < 10 else " ")(i)}{cmd}")
                    break
                
                if line.strip() == "":
                    if input_lines:
                        break
                    continue
                
                if 'then' in line.strip():
                    indent_level += 1
                    in_conditional = True
                elif not in_conditional:
                    success = process_input(line)
                    if not success:
                        break

                input_lines.append(line)
            
            if input_lines:
                input_string = '\n'.join(input_lines)
                process_input(input_string)
        
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            print("\nExiting Banter.")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    if '-i' in sys.argv:
        if len(sys.argv) > 2:
            filename = sys.argv[2]
            start_repl(first=False, filename=filename)
        else:
            start_repl(first=True)
    else:
        if len(sys.argv) > 1:
            filename = sys.argv[1]
            start_repl(first=False, filename=filename)
        else:
            start_repl(first=True)
