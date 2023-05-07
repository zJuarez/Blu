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
    STATE = 5

class Color(Enum):
    WHITE = "#FFFFFF"
    BLACK = "#000000"

class Tipo(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    CHAR = "CHAR"
    BOOL = "BOOL"
    NOT_DECLARED = "NOT_DECLARED"

class Error(Enum):
    REDECLARED_VARIABLE = 1
    VARIABLE_NOT_DECLARED = 2
    DUPLICATED_ARGS = 3
    TYPE_MISMATCH = 4
    EXPRESSION_WENT_WRONG = 5
    IF_EXPRESSION_MUST_BE_BOOL = 6
    INTERNAL_STACKS = 7
    FOR_EXPRESSION_MUST_BE_BOOL = 8
    ALL_ARRAY_ELEMENTS_MUST_BE_SAME_TYPE = 9
    ALL_MATRIX_ARRAYS_MUST_BE_SAME_LENGTH = 10
    ALL_MATRIX_ARRAYS_MUST_BE_SAME_TYPE = 11
    BAD_ARRAY_DECLARATION_INDEX = 12
    WRONG_ARRAY_SIZE_DECLARATION_DIM1 = 13
    WRONG_ARRAY_SIZE_DECLARATION_DIM2 = 14
    TYPE_MISMATCH_IN_ARRAY_DECLARATION = 15
    ID_IS_NOT_ITERABLE = 16

def get_error_message(error, var = '', type_mism = {}):
    if error == Error.REDECLARED_VARIABLE:
        return "Error : " + f"Variable '{var}' already declared"
    elif error == Error.VARIABLE_NOT_DECLARED:
         return "Error : " + f"Variable '{var}' not declared before"
    elif error == Error.DUPLICATED_ARGS:
        return "Error : Duplicated Args"
    elif error == Error.TYPE_MISMATCH:
        return "Error :  Type Mismatch " + f"Using '{type_mism['operator']}' with var '{type_mism['left']['val']}' of type '{type_mism['left']['tipo']}' and '{type_mism['right']['val']}' of type '{type_mism['right']['tipo']}'"
    elif error == Error.EXPRESSION_WENT_WRONG:
        return "Error : Expression went wrong"
    elif error == Error.IF_EXPRESSION_MUST_BE_BOOL:
        return "Error : If Expression must be bool"
    elif error == Error.INTERNAL_STACKS:
        return "Internal Error involving STACKS"
    elif error == Error.FOR_EXPRESSION_MUST_BE_BOOL:
        return "Error : For Expression must be bool"
    elif error == Error.ALL_ARRAY_ELEMENTS_MUST_BE_SAME_TYPE:
        return "Error : All array elemnts must be same type"
    elif error == Error.ALL_MATRIX_ARRAYS_MUST_BE_SAME_LENGTH:
        return "Error : All matrix's arrays must be same length"
    elif error == Error.ALL_MATRIX_ARRAYS_MUST_BE_SAME_TYPE:
        return "Error : All matrix's arrays must be same type"
    elif error == Error.BAD_ARRAY_DECLARATION_INDEX:
        return "Error : Bad array declaration index"
    elif error == Error.WRONG_ARRAY_SIZE_DECLARATION_DIM1:
        return "Error : Wrong array size declaration dimention 1"
    elif error == Error.WRONG_ARRAY_SIZE_DECLARATION_DIM2:
        return "Error : Wrong array size declaration dimention 2"
    elif error == Error.TYPE_MISMATCH_IN_ARRAY_DECLARATION:
        return "Error : Type mismatch in array declaration"
    elif error == Error.ID_IS_NOT_ITERABLE:
        return"Error : " + f"Variable '{var}' is not iterable"
    else:
        return "Error not found"
    
def initialStateSymbols(w = 800,h = 700): 
    return {
        'GET_POS_X' : {Var.ID : 'GET_POS_X' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : w/2},
        'GET_POS_Y' : {Var.ID : 'GET_POS_Y' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : h/2},
        'GET_BG' : {Var.ID : 'GET_BG' , Var.TIPO : Tipo.STRING, Var.KIND : Kind.STATE, Var.VAL : Color.WHITE},
        'GET_COLOR' : {Var.ID : 'GET_COLOR' , Var.TIPO : Tipo.STRING, Var.KIND : Kind.STATE, Var.VAL : Color.BLACK},
        'IS_PENDOWN' : {Var.ID : 'IS_PENDOWN' , Var.TIPO : Tipo.BOOL, Var.KIND : Kind.STATE, Var.VAL : False},
        'IS_PENUP' : {Var.ID : 'IS_PENDOWN' , Var.TIPO : Tipo.BOOL, Var.KIND : Kind.STATE, Var.VAL : True},
        'GET_WIDTH' : {Var.ID : 'GET_WIDTH' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : 1},
        'GET_ORIENTATION' : {Var.ID : 'GET_ORIENTATION' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : 0},
    }

def get_tipo(tipo):
    if tipo == "INT":
        return Tipo.INT
    elif tipo == "FLOAT":
        return Tipo.FLOAT
    elif tipo == "CHAR":
        return Tipo.CHAR
    elif tipo == "BOOL":
        return Tipo.BOOL
    elif tipo == "STRING":
        return Tipo.STRING
    else:
        return Tipo.NOT_DECLARED