import banterlang
from BanterADT import *
from collections import deque

prints = False

def eval_program(program, variables=None, context=None, returnPrints=False):
    if returnPrints:
        global prints
        prints = True

    # Setup for variables and context if not provided
    if variables is None:
        variables = {}
    if context is None:
        context = []

    if not context or context[0] != program:
        context.insert(0, program)

    # Convert program to a flat list of statements
    execution_queue = deque()
    if isinstance(program, list):
        execution_queue.extend(program)
    else:
        execution_queue.append(program)

    result = None
    captured_output = ""  # Variable to store captured prints
    while execution_queue:
        stmt = execution_queue.popleft()
        result = eval_statement_iter(stmt, variables, context, execution_queue, captured_output, returnPrints)
        if isinstance(result, ReturnValue):  # Special wrapper for return values
            captured_output += str(result)  # Accumulate the printed output
            break
        elif isinstance(result, str):
            captured_output += result  # Accumulate the printed output

    return captured_output if returnPrints else result

class ReturnValue:
    """Wrapper class to distinguish return values from regular evaluation results"""
    def __init__(self, value):
        self.value = value

def eval_statement_iter(statement, variables, context, execution_queue, captured_output, returnPrints):
    if isinstance(statement, LetStatement):
        value = eval_expression(statement.value, variables)
        variables[statement.mneumonic] = value
        return None

    elif isinstance(statement, IfStatement):
        if eval_comparison(statement.expr, variables):
            if isinstance(statement.do, list):
                execution_queue.extendleft(reversed(statement.do))
            else:
                execution_queue.appendleft(statement.do)
        return None

    elif isinstance(statement, IfElseStatement):
        if eval_comparison(statement.expr, variables):
            if isinstance(statement.do, list):
                execution_queue.extendleft(reversed(statement.do))
            else:
                execution_queue.appendleft(statement.do)
        elif statement.alternate:
            if isinstance(statement.alternate, list):
                execution_queue.extendleft(reversed(statement.alternate))
            else:
                execution_queue.appendleft(statement.alternate)
        return None

    elif isinstance(statement, ReturnStatement):
        value = eval_expression(statement.value, variables)
        return ReturnValue(value)  # Wrap return values

    elif isinstance(statement, PrintStatement):
        if statement.value is not None:
            res = eval_expression(statement.value, variables)
            global prints
            if prints:
                return str(res)+"\n"  # Capture the print value instead of printing
            else:
                print(res)  # Directly print if not capturing
        else:
            print()  # Empty print statement
            return "\n"

    elif isinstance(statement, GotoStatement):
        program = context[0]
        marker_path = find_marker_position(program, statement.label)
        if marker_path:
            parent_path = marker_path[:-1]
            parent = get_subtree_at_path(program, parent_path)
            marker_index = marker_path[-1]
            
            if isinstance(parent, list):
                # Clear the current queue and add remaining statements after marker
                execution_queue.clear()
                execution_queue.extend(parent[marker_index + 1:])
            else:
                raise ValueError("Marker's parent is not a list")
        else:
            raise ValueError(f"Marker {statement.label} not found")
        return None

    elif isinstance(statement, MarkerStatement):
        return None

    elif isinstance(statement, (Mneumonic, Operation, Comparison, bool, int, str)):
        return eval_expression(statement, variables)

    elif isinstance(statement, list):
        execution_queue.extendleft(reversed(statement))
        return None

# Keep the existing helper functions unchanged
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
    elif hasattr(node, 'do'):
        do = find_marker_position(node.do, label, path + ['do'])
        if do:
            return do
        if hasattr(node, 'alternate'):
            alt = find_marker_position(node.alternate, label, path + ['alternate'])
            if alt:
                return alt
    return None

def get_subtree_at_path(tree, path):
    """Get the subtree at the specified path"""
    current = tree
    for p in path:
        if isinstance(p, str):
            current = getattr(current, p)
        else:
            current = current[p]
    return current

def eval_expression(expression, variables):
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
        return eval_operation(expression, variables)
    elif isinstance(expression, Comparison):
        # Evaluate the comparison expression
        return eval_comparison(expression, variables)
    else:
        raise ValueError(f"Unknown expression type: {type(expression)}")

def eval_operation(operation, variables):
    # Evaluate the operands first
    operands = [eval_expression(operand, variables) for operand in operation.operands]

    types = set([type(op) for op in operands])

    if len(types) > 1:
        if len(types) == 2 and type(1) in types and type(1.0) in types:
            pass
        else:
            raise TypeError("Operands must have the same type.") # None of that!


    if operation.operator == '+':
        if isinstance(operands[0], str):
            return operands[0][:-1] + operands[1][1:] # string concat'n is a little jank
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

def eval_comparison(comparison, variables):
    # Evaluate the operands of the comparison
    operand1 = eval_expression(comparison.operands[0], variables)
    operand2 = eval_expression(comparison.operands[1], variables)

    operands = [eval_expression(operand, variables) for operand in comparison.operands]

    types = set([type(op) for op in operands])

    if len(types) > 1: 
        if bool in types and int in types:
            return False

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

