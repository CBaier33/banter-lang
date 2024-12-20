import ply.lex as lex
from ply.lex import LexToken
import ply.yacc as yacc
from BanterADT import *

#################### BEGIN Lexer/Scanner Specification ####################

# Reserved Words
reserved = {
    'let': 'LET',
    'be': 'BE',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'return': 'RETURN',
    'goto': 'GOTO',
    'instruction': 'INSTRUCTION',
    'True': 'BOOL',
    'False': 'BOOL',
    'print': 'PRINT'
}

# Token list
tokens = [

    # Identifiers and Literals
    'MNEUMONIC', 'STRING', 'NUMBER',

    # Operators
    'PLUS', 'MINUS', 'DIVIDE', 'TIMES', 'COMP_OP',

    # Punctuations
    'COMMA', 'LP', 'RP', 'MARKER', 'ENDMARKER',
        
    # Indentation
    'INDENT', 'DEDENT', 'NEWLINE', 'WS'] + list(set(reserved.values()))

t_LET = r'let'
t_BE = r'be'
t_IF = r'if'
t_COMMA = r','
t_THEN = r'then'
t_ELSE = r'else'
t_RETURN = r'return'
t_GOTO = r'goto'
t_INSTRUCTION = r'instruction'
t_MARKER = r'@'
t_PRINT = r'print'

t_STRING = r'\"([^\\\n]|(\\.))*?\"'
t_BOOL = r'True|False'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

t_COMP_OP = r'<=|>=|==|!=|<|>'

t_ignore_COMMENT = r'\#[^\n]*'

def t_MNEUMONIC(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'MNEUMONIC')
    return t

def t_NUMBER(t):
    r'\d+\.\d+|\d+'  # Match both floating-point and integer numbers
    if '.' in t.value:
        t.value = float(t.value)  # Convert to float if it contains a decimal point
    else:
        t.value = int(t.value)  # Otherwise, convert to integer
    return t

# Whitespace
def t_WS(t):
    r' +|\t+' # this appears to work conditionally on different systems??
    if t.lexer.at_line_start and t.lexer.paren_count == 0:
        return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = "NEWLINE"
    if t.lexer.paren_count == 0:
        return t

def t_LP(t):
    r'\('
    t.lexer.paren_count += 1
    return t

def t_RP(t):
    r'\)'
    t.lexer.paren_count -= 1
    return t

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))
    print("Skipping", repr(t.value[0]))
    t.lexer.skip(1)


### Indentation Post-Processing Filtration 
### This has been adapted from the GardenSnake language implementation found in the ply repository.

NO_INDENT = 0
MAY_INDENT = 1
MUST_INDENT = 2

def track_tokens_filter(lexer, tokens):
    lexer.at_line_start = at_line_start = True
    indent = NO_INDENT
    for token in tokens:

        token.at_line_start = at_line_start

        if token.type == "THEN" or token.type == "ELSE":
            at_line_start = False
            indent = MAY_INDENT
            token.must_indent = False

        elif token.type == "NEWLINE":
            at_line_start = True
            if indent == MAY_INDENT:
                indent = MUST_INDENT
            token.must_indent = False

        elif token.type == "WS":
            assert token.at_line_start == True
            at_line_start = True
            token.must_indent = False

        else:
            # A real token; only indent after COMMA THEN
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False
            indent = NO_INDENT

        yield token
        lexer.at_line_start = at_line_start

def _new_token(type, lineno, lexpos):
    tok = LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    tok.lexpos = lexpos
    return tok

# Synthesize a DEDENT tag
def DEDENT(lineno):
    return _new_token("DEDENT", lineno, 0)

# Synthesize a INDENT tag
def INDENT(lineno):
    return _new_token("INDENT", lineno, 0)

# Track the indentation level and emit the right INDENT / DEDENT events.
def indentation_filter(tokens):
    # A stack of indentation levels; will never pop item 0
    levels = [0]
    token = None
    depth = 0
    prev_was_ws = False
    for token in tokens:
        if token.type == "WS":
            assert depth == 0
            depth += len(token.value)
            prev_was_ws = True
            # WS tokens are never passed to the parser
            continue

        if token.type == "NEWLINE":
            depth = 0
            if prev_was_ws or token.at_line_start:
                # ignore blank lines
                continue
            # pass the other cases on through
            yield token
            continue

        # then it must be a real token (not WS, not NEWLINE)
        # which can affect the indentation level

        prev_was_ws = False
        if token.must_indent:
            # The current depth must be larger than the previous level
            if not (depth > levels[-1]):
                raise IndentationError("expected an indented block")

            levels.append(depth)
            yield INDENT(token.lineno)

        elif token.at_line_start:
            # Must be on the same level or one of the previous levels
            if depth == levels[-1]:
                # At the same level
                pass
            elif depth > levels[-1]:
                raise IndentationError(
                    "indentation increase but not in new block")
            else:
                # Back up; but only if it matches a previous level
                try:
                    i = levels.index(depth)
                except ValueError:
                    raise IndentationError("inconsistent indentation")
                for _ in range(i + 1, len(levels)):
                    yield DEDENT(token.lineno)
                    levels.pop()

        yield token

    # Must dedent any remaining levels
    if len(levels) > 1:
        assert token is not None
        for _ in range(1, len(levels)):
            yield DEDENT(token.lineno)


# The top-level filter adds an ENDMARKER, if requested.
# Python's grammar uses it.
def filter(lexer, add_endmarker=False):
    token = None
    tokens = iter(lexer.token, None)
    tokens = track_tokens_filter(lexer, tokens)
    for token in indentation_filter(tokens):
        yield token

    if add_endmarker:
        lineno = 1
        if token is not None:
            lineno = token.lineno
        yield _new_token("ENDMARKER", lineno, 0)

class IndentLexer(object):

    def __init__(self, debug=0, optimize=0, lextab='lextab', reflags=0):
        self.lexer = lex.lex(debug=debug, optimize=optimize,
                             lextab=lextab, reflags=reflags)
        self.token_stream = None

    def input(self, s, add_endmarker=True):
        self.lexer.paren_count = 0
        self.lexer.input(s)
        self.token_stream = filter(self.lexer, add_endmarker)

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None

lexer = IndentLexer()

#################### BEGIN Grammar Pattern-Action Rules ####################

# Define the precedence of operators
precedence = (
    ('left', 'COMP_OP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

global_ast = ""

# Grammar rules
# View parser.out for a more comprehensive understanding of the grammar
def p_input(p):
    '''input : program ENDMARKER'''
    p[0] = p[1]

def p_program(p):
    '''program : program NEWLINE
               | program command
               | command
               | expression'''  # Add this line to allow expressions as valid programs

    global global_ast
    if len(p) == 2:
        if isinstance(p[1], list):  # Multiple statements
            global_ast = p[1]
        else:
            global_ast = [p[1]]  # Single statement or expression, create a list
    else:
        global_ast = p[1] + [p[2]] # Multiple statements, concatenate lists

    p[0] = global_ast

def p_command(p):
    '''command : stmt'''
    p[0] = p[1]

# Statements
def p_stmt(p):
    '''stmt : statement NEWLINE
            | statement'''
    p[0] = p[1]

def p_stmts(p):
    '''stmts : stmts stmt
             | stmt'''
    if len(p) == 2:
        p[0] = p[1]
    #else:
    #    #p[0] = [p[1]] + [p[2]]
    #    p[0] = p[1] + [p[2]]
    elif isinstance(p[1], list):
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]] + [p[2]]


def p_block(p):
    '''block : NEWLINE INDENT stmts DEDENT
             | stmt'''
    if len(p) == 2:  # Single-line block
        #p[0] = [p[1]]
        p[0] = p[1]
    else:  # Multi-line block
        p[0] = p[3]

def p_statement_let(p):
    '''statement : LET MNEUMONIC BE expression'''
    p[0] = LetStatement(mneumonic=p[2], value=p[4])

def p_statement_if(p):
    '''statement : IF comparison COMMA THEN block
                 | IF comparison COMMA THEN block ELSE block'''
    if len(p) == 6:
        p[0] = IfStatement(expr=p[2], do=p[5])
    else:
        p[0] = IfElseStatement(expr=p[2], do=p[5], alternate=p[7])

def p_statement_return(p):
    '''statement : RETURN expression'''
    p[0] = ReturnStatement(value=p[2])

def p_statement_print(p):
    '''statement : PRINT expression
                 | PRINT'''
    if len(p) == 2:
        p[0] = PrintStatement(value=None)
    else:
        p[0] = PrintStatement(value=p[2])

def p_statement_goto(p):
    '''statement : GOTO INSTRUCTION NUMBER'''
    p[0] = GotoStatement(label=p[3])

def p_statement_marker(p):
    '''statement : MARKER NUMBER'''
    p[0] = MarkerStatement(label=p[2])

# Expressions
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | MINUS expression'''
    if len(p) == 3:
        p[0] = Operation(operator="*", operands=[-1, p[2]])
    else:
        p[0] = Operation(operator=p[2], operands=[p[1], p[3]])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = p[1] 

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = p[1]  

def p_expression_mneumonic(p):
    '''expression : MNEUMONIC'''
    p[0] = Mneumonic(name=p[1], value=None)

def p_expression_bool(p):
    '''expression : BOOL'''
    if p[1] == 'True':
        p[0] = True
    elif p[1] == 'False':
        p[0] = False

def p_expression_group(p):
    '''expression : LP expression RP'''
    p[0] = p[2]

def p_expression_comparison(p):
    '''expression : comparison'''
    p[0] = p[1]

def p_comparison(p):
    '''comparison : expression COMP_OP expression'''
    p[0] = Comparison(operator=p[2], operands=[p[1], p[3]])

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")
    raise Exception

class BanterParser:

    def __init__(self, lexer=None):
        if lexer is None:
            lexer = IndentLexer()
        self.lexer = lexer
        self.parser = yacc.yacc(start="input")

    def parse(self, code):
        self.lexer.input(code)
        result = self.parser.parse(lexer=self.lexer, debug=False)
        return result

parser = BanterParser(lexer)
