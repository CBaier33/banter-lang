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
    'True': 'BOOL',
    'False': 'BOOL'
}

# Token list
tokens = [

    # Identifiers and Literals
    'MNEUMONIC', 'STRING', 'NUMBER',

    # Operators
    'PLUS', 'MINUS', 'DIVIDE', 'TIMES', 'COMP_OP',

    # Punctuations
    'COMMA', 'LP', 'RP', 'MARKER',
        
    'INDENT', 'DEDENT', 'NEWLINE', 'WS'] + list(set(reserved.values()))

t_LET = r'let'
t_BE = r'be'
t_RETURN = r'return'
t_GOTO = r'goto'
t_INSTRUCTION = r'instruction'
t_MARKER = r'@'
t_STRING = r'\"([^\\\n]|(\\.))*?\"'

t_BOOL = r'True|False'
t_IF = r'if'
t_ELSE = r'else'
t_THEN = r'then'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

t_COMP_OP = r'<=|>=|==|!=|<|>'

t_COMMA = r','

t_ignore_COMMENT = r'\#[^\n]*'

t_ignore = '\n'

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
    #r' [ ]+ '
    r' +|\t+'
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
    # check for underflow?  should be the job of the parser
    t.lexer.paren_count -= 1
    return t

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))
    print("Skipping", repr(t.value[0]))
    t.lexer.skip(1)

# I implemented INDENT / DEDENT generation as a post-processing filter

# The original lex token stream contains WS and NEWLINE characters.
# WS will only occur before any other tokens on a line.

# I have three filters.  One tags tokens by adding two attributes.
# "must_indent" is True if the token must be indented from the
# previous code.  The other is "at_line_start" which is True for WS
# and the first non-WS/non-NEWLINE on a line.  It flags the check so
# see if the new line has changed indication level.

# Python's syntax has three INDENT states
#  0) no colon hence no need to indent
#  1) "if 1: go()" - simple statements have a COLON but no need for an indent
#  2) "if 1:\n  go()" - complex statements have a COLON NEWLINE and must indent
NO_INDENT = 0
MAY_INDENT = 1
MUST_INDENT = 2

# only care about whitespace at the start of a line

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
            # A real token; only indent after COLON NEWLINE
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False
            indent = NO_INDENT

        yield token
        lexer.at_line_start = at_line_start


def _new_token(type, lineno, lexpos):
    tok = lex.LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    tok.lexpos = lexpos
    return tok

# Synthesize a DEDENT tag
def DEDENT(lineno):
    return _new_token("DEDENT", lineno, 0)

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
        # if 1:
        # print "Process", token,
        # if token.at_line_start:
        # print "at_line_start",
        # if token.must_indent:
        # print "must_indent",
        # print

        # WS only occurs at the start of the line
        # There may be WS followed by NEWLINE so
        # only track the depth here.  Don't indent/dedent
        # until there's something real.
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

    ### Finished processing ###

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
#    for token in tokens:
#        print(f"TOKEN -> {token.value}\nTYPE -> {token.type}\nATSTART -> {token.at_line_start}\nMUSTINDENT -> {token.must_indent}\n\n")
#
    for token in indentation_filter(tokens):
        yield token

    #if add_endmarker:
    #    lineno = 1
    #    if token is not None:
    #        lineno = token.lineno
    #    yield _new_token("ENDMARKER", lineno, token.lexpos if token else 0)

# Combine Ply and my filters into a new lexer


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



#################### END Lexer/Scanner Specification ####################

# Build the lexer

lexer = IndentLexer()

#sample_input = """
#let wrong be 3
#let right be 7
#
#if wrong + wrong == right, then
#    return "Yes"
#else 
#    return "No"
#"""
#lexer.input(sample_input)
#
## Process tokens
#for token in lexer.token_stream:
#    print(token)

#exit()

#################### BEGIN Grammar Pattern-Action Rules ####################

# Define the precedence of operators
precedence = (
    ('nonassoc', 'THEN'),
    ('nonassoc', 'ELSE'),
    ('left', 'COMP_OP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
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
        global_ast = p[1] + [p[2]] # Multiple statements, concatenate lists

    p[0] = global_ast

# Statements
def p_statements(p):
    '''statements : statement
                  | statement statements'''
    if len(p) == 2:
        p[0] = [p[1]]  # Single statement
    else:
        p[0] = [p[1]] + p[2]  # Multiple statements

def p_block(p):
    '''block : statement
             | NEWLINE INDENT statements NEWLINE DEDENT'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]  # Return the list of statements

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

def p_expression_bool(p):
    '''expression : BOOL'''
    if p[1] == 'True':
        p[0] = True
    elif p[1] == 'False':
        p[0] = False

def p_expression_group(p):
    '''expression : LP expression RP'''
    p[0] = p[2]  # Return the expression inside parentheses

def p_expression_comparison(p):
    '''expression : comparison'''
    p[0] = p[1]

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
#parser = yacc.yacc()
class SudoLangParser:

    def __init__(self, lexer=None):
        if lexer is None:
            lexer = IndentLexer()
        self.lexer = lexer
        self.parser = yacc.yacc(start="program")

    def parse(self, code):
        self.lexer.input(code)
        result = self.parser.parse(lexer=self.lexer, debug=False)
        return result

parser = SudoLangParser(lexer)
