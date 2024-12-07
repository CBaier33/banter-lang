import ply.lex as lex
import ply.yacc as yacc

#################### BEGIN Lexer/Scanner Specification ####################

reserved = {
    'let': 'LET',
    'be': 'BE',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'return': 'RETURN',
    'goto': 'GOTO',
    'instruction': 'INSTRUCTION',
    'True': 'TRUE',
    'False': 'FALSE'
}

# Token list
tokens = [

    # Identifiers and Literals
    'MNEUMONIC', 'STRING', 'NUMBER',

    # Operators
    'PLUS', 'MINUS', 'DIVIDE', 'TIMES', 

    # Comparisions
    'COMP_OP',

    # Punctuations
    'COMMA', 'LP', 'RP'] + list(reserved.values())

# Ignored characters
t_ignore = ' \t'

t_LET = r'let'
t_BE = r'be'
t_RETURN = r'return'
t_GOTO = r'goto'
t_INSTRUCTION = r'instruction'
t_STRING = r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''
t_TRUE = r'True'
t_FALSE = r'False'
t_IF = r'if'
t_ELSE = r'else'
t_THEN = r'then'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

t_COMP_OP = r'<=|>=|==|!=|<|>'

t_COMMA = r','
t_LP = r'\('
t_RP = r'\)'

def t_MNEUMONIC(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'MNEUMONIC')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

#################### END Lexer/Scanner Specification ####################

# Build the lexer
lexer = lex.lex()

#################### BEGIN Grammar Pattern-Action Rules ####################

# Precedence rules for arithmetic operations
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('nonassoc', 'COMP_OP'), # Comparison operators
)

# Dictionary to hold variables (symbol table)
variables = {}

# Global flag to halt execution after return
execution_halted = False

def p_program(p):
    '''program : statement
               | statement program'''
    global execution_halted
    if execution_halted:
        return  # Skip further execution
    pass

def p_statement(p):
    '''statement : let_statement
                 | if_statement
                 | if_else_statement
                 | return_statement
                 | goto_statement'''

    global execution_halted
    if execution_halted:
        return  # Skip further execution
    p[0] = p[1]

def p_let_statement(p):
    '''let_statement : LET MNEUMONIC BE arithmetic_expression'''
    global execution_halted
    if execution_halted:
        return  # Skip further execution
    variables[p[2]] = p[4]
    print(f"Assigned {p[2]} to {p[4]}")

def p_if_statement(p):
    '''if_statement : IF comparison COMMA THEN block'''
    print("DEBUG "+str(p[2]))
    global execution_halted
    if execution_halted:
        return  # Skip further execution
    if p[2]:  # Evaluate the condition
        p[0] = p[5]  # Execute 'then' block

def p_if_else_statement(p):
    '''if_else_statement : IF comparison COMMA THEN block ELSE block'''
    global execution_halted
    if execution_halted:
        return  # Skip further execution
    if p[2]:  # Evaluate the condition
        p[0] = p[5]  # Execute 'then' block
    else:
        p[0] = p[7]  # Execute 'else' block

def p_return_statement(p):
    '''return_statement : RETURN MNEUMONIC
                        | RETURN NUMBER
                        | RETURN STRING'''

    global execution_halted
    if execution_halted:
        return  # Skip further execution

    if isinstance(p[2], int):
        print(p[2])
    elif isinstance(p[2], str) and p[2].startswith('"'):
        print(p[2][1:-1])  # Remove surrounding quotes
    else:
        print(variables.get(p[2], f"Undefined variable: {p[2]}"))

    execution_halted = True  # Halt execution after return

def p_goto_statement(p):
    '''goto_statement : GOTO INSTRUCTION NUMBER'''
    global execution_halted
    if execution_halted:
        return  # Skip further execution
    print(f"Goto instruction {p[3]}")

def p_block(p):
    '''block : statement
             | statement block'''
    pass

def p_arithmetic_expression(p):
    '''arithmetic_expression : term
                             | arithmetic_expression PLUS term
                             | arithmetic_expression MINUS term'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]

def p_term(p):
    '''term : factor
            | term TIMES factor
            | term DIVIDE factor'''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]

def p_factor(p):
    '''factor : MNEUMONIC
              | NUMBER
              | LP arithmetic_expression RP'''
    if len(p) == 2:
        if isinstance(p[1], int):
            p[0] = p[1]
        else:
            p[0] = variables.get(p[1], f"Undefined variable: {p[1]}")
    else:
        p[0] = p[2]

def p_comparison(p):
    '''comparison : arithmetic_expression COMP_OP arithmetic_expression'''
    left = p[1]
    operator = p[2]
    right = p[3]
    
    if operator == '>':
        p[0] = left > right
    elif operator == '<':
        p[0] = left < right
    elif operator == '>=':
        p[0] = left >= right
    elif operator == '<=':
        p[0] = left <= right
    elif operator == '==':
        p[0] = left == right
    elif operator == '!=':
        p[0] = left != right
    else:
        raise SyntaxError(f"Unknown operator: {operator}")

# Error rule for syntax errors
def p_error(p):
    print(f"Syntax error at '{p.value}'")

# Build the parser
parser = yacc.yacc()

####### TESTING

data = '''
let x be 4
let y be 3
let result be x + y
if result > 15, then
    return result
'''

# Tokenize and parse
lexer.input(data)

print("Tokens:")
for token in lexer:
    print(token)

print("\nParsing:")
parser.parse(data)
