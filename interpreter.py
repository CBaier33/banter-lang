import sudolang
from SudoLangADT import *

def eval_program(program, context=None):
    if context is None:
        context = {}  # Initialize an empty context (a dictionary) for variable values

    if isinstance(program, list):
        # If the program is a list of statements, evaluate them one by one
        result = None
        for stmt in program:
            result = eval_statement(stmt, context)
        return result
    else:
        # If it's a single statement, evaluate it
        return eval_statement(program, context)

def eval_statement(statement, context):
    if isinstance(statement, LetStatement):
        return eval_let_statement(statement, context)
    elif isinstance(statement, IfStatement):
        return eval_if_statement(statement, context)
    elif isinstance(statement, IfElseStatement):
        return eval_if_else_statement(statement, context)
    elif isinstance(statement, ReturnStatement):
        return eval_return_statement(statement, context)
    elif isinstance(statement, (Mneumonic, Operation, Comparison)):
        return eval_expression(statement, context)
    else:
        raise ValueError(f"Unknown statement type: {type(statement)}")

def eval_let_statement(statement, context):
    # Assign the evaluated value of the expression to the variable (mnemonic)
    value = eval_expression(statement.value, context)
    context[statement.mneumonic] = value
    return #value

def eval_if_statement(statement, context):
    # Evaluate the comparison expression
    if eval_comparison(statement.expr, context):
        return eval_statement(statement.do, context)
    return None

def eval_if_else_statement(statement, context):
    # Evaluate the comparison expression
    if eval_comparison(statement.expr, context):
        return eval_statement(statement.do, context)
    elif statement.alternate:
        return eval_statement(statement.alternate, context)
    return None

def eval_return_statement(statement, context):
    # Simply return the value of the return expression
    return eval_expression(statement.value, context)

def eval_expression(expression, context):
    if isinstance(expression, (int, float, bool, str)):
        # Literal values (numbers or booleans)
        return expression
    elif isinstance(expression, Mneumonic):
        # Mnemonic refers to a variable, look it up in the context
        if expression.name in context:
            return context[expression.name]
        else:
            raise ValueError(f"Variable {expression.name} not defined")
    elif isinstance(expression, Operation):
        # Perform the operation based on the operator
        return eval_operation(expression, context)
    elif isinstance(expression, Comparison):
        # Evaluate the comparison expression
        return eval_comparison(expression, context)
    else:
        raise ValueError(f"Unknown expression type: {type(expression)}")

def eval_operation(operation, context):
    # Evaluate the operands first
    operands = [eval_expression(operand, context) for operand in operation.operands]

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

def eval_comparison(comparison, context):
    # Evaluate the operands of the comparison
    operand1 = eval_expression(comparison.operands[0], context)
    operand2 = eval_expression(comparison.operands[1], context)

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
