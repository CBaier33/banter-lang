import ply.lex as lex
import ply.yacc as yacc
from SudoLangADT import *

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
t_STRING = r'\"([^\\\n]|(\\.))*?\"'

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

t_LP = r'\('
t_RP = r'\)'
t_COMMA = r','

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

# Define the precedence of operators
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'COMP_OP'),
)

global_ast = ""

# Grammar rules
# Change the program rule to also accept expressions
def p_program(p):
    '''program : statement
               | program statement
               | expression'''  # Add this line to allow expressions as valid programs
    global global_ast
    if len(p) == 2:
        if isinstance(p[1], list):  # Multiple statements
            global_ast = p[1]
        else:
            global_ast = [p[1]]  # Single statement or expression, create a list
    else:
        global_ast = p[1] + [p[2]]  # Multiple statements, concatenate lists
    p[0] = global_ast

# Statements
def p_statement_let(p):
    '''statement : LET MNEUMONIC BE expression'''
    p[0] = LetStatement(mneumonic=p[2], value=p[4])

def p_statement_if(p):
    '''statement : IF comparison COMMA THEN statement'''
    p[0] = IfStatement(expr=p[2], do=p[5])

def p_statement_if_else(p):
    '''statement : IF comparison COMMA THEN statement ELSE statement'''
    p[0] = IfElseStatement(expr=p[2], do=p[5], alternate=p[7])

def p_statement_return(p):
    '''statement : RETURN expression'''
    p[0] = ReturnStatement(value=p[2])

# Expressions
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    p[0] = Operation(operator=p[2], operands=[p[1], p[3]])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = p[1]  # Literal number

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = p[1]  # Literal string

def p_expression_mneumonic(p):
    '''expression : MNEUMONIC'''
    p[0] = Mneumonic(name=p[1], value=None)

def p_expression_group(p):
    '''expression : LP expression RP'''
    p[0] = p[2]  # Return the expression inside parentheses

def p_expression_comparison(p):
    '''expression : comparison'''
    p[0] = Comparison(p[1])  # Return the comparison

def p_comparison(p):
    '''comparison : expression COMP_OP expression'''
    p[0] = Comparison(operator=p[2], operands=[p[1], p[3]])

# Error handling
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")
    raise Exception

# Build the parser
parser = yacc.yacc()
