from dataclasses import dataclass, field
from typing import Union, List, Optional

@dataclass
class Mneumonic:
    name: str
    value: any

    def __repr__(self):
        return self.name

@dataclass
class Operation:
    operator: str  # The operator symbol, e.g., '+', '-', '*', '/'
    operands: List[Union[int, float, 'Operation']] = field(default_factory=list)

    def __post_init__(self):
        # Validate the number of operands for binary operations
        if self.is_binary() and len(self.operands) != 2:
            raise ValueError("Binary operations must have exactly two operands.")

        if self.is_unary() and len(self.operands) != 1:
            raise ValueError("Unary operations must have exactly one operand.")

    def is_binary(self) -> bool:
        """Determine if the operation is binary based on the operator."""
        return self.operator in {'+', '-', '*', '/'}

    def is_unary(self) -> bool:
        """Determine if the operation is unary (e.g., negation)."""
        return self.operator in {'neg'}

    def __repr__(self):
      if self.operator == '-' and self.is_unary():  # Unary operator
         return f"{self.operator}{self.operands[0]}"
      else:  # Binary operators
         return f"({f' {self.operator} '.join(map(str, self.operands))})"

@dataclass
class Comparison:
    operator: str  # The comparison operator, e.g., '==', '!=', '>', '<', '>=', '<='
    operands: List[Union[int, float, bool, 'Comparison']] = field(default_factory=list)

    def __post_init__(self):
        # Validate that comparisons always have exactly two operands
        if len(self.operands) != 2:
            raise ValueError("Comparisons must have exactly two operands.")
        
        # Ensure the operator is valid
        if not self.is_valid_operator():
            raise ValueError(f"Invalid operator: {self.operator}")

    def is_valid_operator(self) -> bool:
        """Checks if the operator is a valid comparison operator."""
        return self.operator in {'==', '!=', '>', '<', '>=', '<='}

    def __repr__(self):
        return f"{self.operands[0]} {self.operator} {self.operands[1]}"

@dataclass
class LetStatement:
    mneumonic: str
    value: Union[Operation, int, float, bool, str]

    def __repr__(self):
        return f"let {self.mneumonic} be {self.value}"

@dataclass
class IfStatement:
    expr: Comparison
    do: 'Statement'

    def __repr__(self):
        return f"if {self.expr}, then\n      {self.do}\n"

@dataclass
class IfElseStatement:
    expr: Comparison  # The condition to evaluate
    do: 'Statement'       # Statement to execute if the condition is True
    alternate: Optional['Statement'] = None  # Statement to execute if False (optional)

    def __repr__(self):
        alternate_part = f"else\n   {self.alternate}" if self.alternate else ""
        return f"if {self.expr}, then\n   {self.do}\n{alternate_part}"

@dataclass
class ReturnStatement:
    value: Union[Operation, Mneumonic, int, float, bool, str]

    def __repr__(self):
        return f"return {self.value}"

@dataclass 
class PrintStatement:
    value: Union[Operation, Mneumonic, int, float, bool, str]

    def __repr__(self):
        return f"print {self.value}"

@dataclass
class GotoStatement:
    label: Union[int, float]

    def __repr__(self):
        return f"goto instruction {self.label}"

@dataclass
class MarkerStatement:
    label: Union[int, float]

    def __str__(self):
        return f"@{self.label}"

Statement = Union[ReturnStatement, IfStatement, IfElseStatement, LetStatement, GotoStatement, MarkerStatement]

Program = Union[Statement, Operation, Comparison]
