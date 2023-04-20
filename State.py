from enum import Enum

class State:
    def __init__(self):
        self.curr = {}

    def add_info(self, name, attributes):
        self.curr[name] = attributes

    def get_info(self, name):
        return self.curr.get(name)
    
    def clear(self):
        self.curr = {}
    
    def del_info(self, name):
        del self.curr[name]

    def get_curr(self):
        return self.curr
    
class Var(Enum):
    ID = 1
    KIND = 2
    TIPO = 3
    VAL = 4
    DIM1 = 5
    DIM2 = 6
    ARGS = 7

class Kind(Enum):
    SINGLE = 1
    ARRAY = 2
    MATRIX = 3
    FUNCTION = 4

class Error(Enum):
    REDECLARED_VARIABLE = 1
    VARIABLE_NOT_DECLARED = 2
    DUPLICATED_ARGS = 3

def get_error_message(error, var):
    if error == Error.REDECLARED_VARIABLE:
        return "Error : " + f"Variable '{var}' already declared"
    elif error == Error.VARIABLE_NOT_DECLARED:
         return "Error : " + f"Variable '{var}' not declared before"
    elif error == Error.DUPLICATED_ARGS:
        return "Error : Duplicated Args"
    else:
        return "Error not found"