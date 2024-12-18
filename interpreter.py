import sudolang
from SudoLangADT import *

returned = False

def eval_program(program, variables=None, context=None):
    if variables is None:
        variables = {}

    if context is None:
        context = []
        
    # Add program to context if not already present
    if not context or context[0] != program:
        context.insert(0, program)
        
    global returned
    returned = False
    
    return eval_statement(program, variables, context)

def find_marker_position(node, label, path=None):
    """Recursively find the position of a marker in the syntax tree."""
    if path is None:
        path = []

    if isinstance(node, list):
        for i, stmt in enumerate(node):
            result = find_marker_position(stmt, label, path + [i])
            if result:
                return result
    elif isinstance(node, MarkerStatement) and node.label == label:
        return path
    elif hasattr(node, 'do'):  # Handle IfStatement and IfElseStatement
        do = find_marker_position(node.do, label, path + ['do'])
        if do:
            return do
        if hasattr(node, 'alternate'):
            alt = find_marker_position(node.alternate, label, path + ['alternate'])
            if alt:
                return alt
    elif hasattr(node, 'alternate'):  # Handle IfElseStatement alternate branch
        result = find_marker_position(node.alternate, label, path + ['alternate'])
        if result:
            return result

    return None


def get_subtree_at_path(tree, path):
    """Get the subtree at the specified path"""
    current = tree
    for p in path:
        if isinstance(p, str):  # For 'do' or 'alternate'
            current = getattr(current, p)
        else:
            current = current[p]
    return current

def eval_statement(statement, variables, context):
    if isinstance(statement, LetStatement):
        return eval_let_statement(statement, variables, context)
    elif isinstance(statement, IfStatement):
        return eval_if_statement(statement, variables, context)
    elif isinstance(statement, IfElseStatement):
        return eval_if_else_statement(statement, variables, context)
    elif isinstance(statement, ReturnStatement):
        return eval_return_statement(statement, variables, context)
    elif isinstance(statement, PrintStatement):
        return eval_print_statement(statement, variables, context)
    elif isinstance(statement, GotoStatement):
        # Get the full program from context
        program = context[0]
        # Find the marker's position in the tree
        marker_path = find_marker_position(program, statement.label)
        if marker_path:
            # Get the parent of the marker
            parent_path = marker_path[:-1]
            parent = get_subtree_at_path(program, parent_path)
            marker_index = marker_path[-1]

            # Ensure we skip the marker itself and resume from the next statement
            if isinstance(parent, list):
                remaining_statements = parent[marker_index + 1:]
                return eval_statement(remaining_statements, variables, context)
            else:
                raise ValueError("Marker's parent is not a list")
        else:
            raise ValueError(f"Marker {statement.label} not found")

    elif isinstance(statement, MarkerStatement):
        return None
    elif isinstance(statement, (Mneumonic, Operation, Comparison, bool, int, str)): 
        return eval_expression(statement, variables, context)
    elif isinstance(statement, list):
        result = None
        for stmt in statement:
            result = eval_statement(stmt, variables, context)
            if returned:  # Stop evaluation if a return occurs
                break
            if isinstance(stmt, GotoStatement):  # Restart context after a goto
                break
        return result

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

    global returned
    returned = True

    return eval_expression(statement.value, variables, context)

def eval_print_statement(statement, variables, context):

    res = eval_expression(statement.value, variables, context)

    print(res)

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
        if isinstance(operands[0], str):
            return operands[0][:-1] + operands[1][1:]
        return operands[0] + operands[1]
    elif operation.operator == '-':
        return operands[0] - operands[1]
    elif operation.operator == '*':
        return operands[0] * operands[1]
    elif operation.operator == '/':
        if operands[1] == 0:
            raise ValueError("Division by zero")
        return operands[0] / operands[1]
    elif operation.operator == '-':
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
