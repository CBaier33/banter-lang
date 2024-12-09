import sudolang
from SudoLangADT import *

def eval_program(program, variables=None, context=None):
    if variables is None:
        variables = {}  # Initialize an empty variables (a dictionary) for variable values

    if context is None:
        context = {}

    if isinstance(program, list):
        # If the program is a list of statements, evaluate them one by one
        result = None
        for stmt in program:
            result = eval_statement(stmt, variables, context)
        return result
    else:
        # If it's a single statement, evaluate it
        return eval_statement(program, variables, context)

def eval_statement(statement, variables, context):
    if isinstance(statement, LetStatement):
        return eval_let_statement(statement, variables, context)
    elif isinstance(statement, IfStatement):
        return eval_if_statement(statement, variables, context)
    elif isinstance(statement, IfElseStatement):
        return eval_if_else_statement(statement, variables, context)
    elif isinstance(statement, ReturnStatement):
        return eval_return_statement(statement, variables, context)
    elif isinstance(statement, GotoStatement):
        return eval_goto_statement(statement, variables, context)
    elif isinstance(statement, GotoStatement):
        return eval_marker_statement(statement, variables, context)
    elif isinstance(statement, (Mneumonic, Operation, Comparison, bool, int, str)): 
        return eval_expression(statement, variables, context)
    else:
        raise ValueError(f"Unknown statement type: {type(statement)}")

def eval_let_statement(statement, variables, context):
    # Assign the evaluated value of the expression to the variable (mnemonic)
    value = eval_expression(statement.value, variables, context)
    variables[statement.mneumonic] = value
    return #value

def eval_if_statement(statement, variables, context):
    # Evaluate the comparison expression
    if eval_comparison(statement.expr, variables, context):
        return eval_statement(statement.do, variables, context)
    return None

def eval_if_else_statement(statement, variables, context):
    # Evaluate the comparison expression
    if eval_comparison(statement.expr, variables, context):
        return eval_statement(statement.do, variables, context)
    elif statement.alternate:
        return eval_statement(statement.alternate, variables, context)
    return None

def eval_return_statement(statement, variables, context):
    # Simply return the value of the return expression
    return eval_expression(statement.value, variables, context)

def eval_goto_statement(statement, variables, context):
    pass

def eval_marker_statement(statement, variables, context):
    pass

def eval_expression(expression, variables, context):
    if isinstance(expression, (int, float, bool, str)):
        # Literal values (numbers or booleans)
        return expression
    elif isinstance(expression, Mneumonic):
        # Mnemonic refers to a variable, look it up in the variables
        if expression.name in variables:
            return variables[expression.name]
        else:
            raise ValueError(f"Variable {expression.name} not defined")
    elif isinstance(expression, Operation):
        # Perform the operation based on the operator
        return eval_operation(expression, variables, context)
    elif isinstance(expression, Comparison):
        # Evaluate the comparison expression
        return eval_comparison(expression, variables, context)
    else:
        raise ValueError(f"Unknown expression type: {type(expression)}")

def eval_operation(operation, variables, context):
    # Evaluate the operands first
    operands = [eval_expression(operand, variables, context) for operand in operation.operands]

    types = set([type(op) for op in operands])

    if len(types) > 1:
        if len(types) == 2 and type(1) in types and type(1.0) in types:
            pass
        else:
            raise TypeError("Operands must have the same type.")


    if operation.operator == '+':
        return operands[0] + operands[1]
    elif operation.operator == '-':
        return operands[0] - operands[1]
    elif operation.operator == '*':
        return operands[0] * operands[1]
    elif operation.operator == '/':
        if operands[1] == 0:
            raise ValueError("Division by zero")
        return operands[0] / operands[1]
    elif operation.operator == 'neg':
        return -operands[0]
    else:
        raise ValueError(f"Unknown operator: {operation.operator}")

def eval_comparison(comparison, variables, context):
    # Evaluate the operands of the comparison
    operand1 = eval_expression(comparison.operands[0], variables, context)
    operand2 = eval_expression(comparison.operands[1], variables, context)

    if comparison.operator == '==':
        return operand1 == operand2
    elif comparison.operator == '!=':
        return operand1 != operand2
    elif comparison.operator == '>':
        return operand1 > operand2
    elif comparison.operator == '<':
        return operand1 < operand2
    elif comparison.operator == '>=':
        return operand1 >= operand2
    elif comparison.operator == '<=':
        return operand1 <= operand2
    else:
        raise ValueError(f"Unknown comparison operator: {comparison.operator}")
