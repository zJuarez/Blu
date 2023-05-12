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
    DIR_VIR = 8

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
    VOID = "VOID"
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
    FUNCTION_PARAMS_DIFF = 17
    FUNCTION_PARAM_TYPE_MISMATCH = 18
    VOID_IN_EXPRESION = 19
    FUNCTION_MUST_HAVE_RETURN = 20
    FUNTION_RETURN_TYPE_MISMATCH = 21

class QOp(Enum):
    EQUAL = 0
    PLUS = 1
    MINUS = 2
    TIMES = 3
    DIVIDE = 4
    LCOMP = 5
    RCOMP = 6
    LCOMP_EQUAL = 7
    RCOMP_EQUAL = 8
    EQUAL_EQUAL = 9
    EXC_EQUAL = 10
    AND = 11
    OR = 12
    GOTO = 13
    GOTOF = 14
    POS = 15
    BG = 16
    COLOR = 17
    PENDOWN = 18
    PENUP = 19
    WIDTH = 20
    CIRCLE = 21
    GO = 22
    RIGHT = 23
    LEFT = 24
    ORIENTATION = 25
    PRINT = 26
    ERA = 27
    GOSUB = 28
    PARAM = 29
    ENDFUNC = 30
    RETURN = 31
    END = 32

operator_to_quadop = {
    "=" : QOp.EQUAL,
    "+" : QOp.PLUS,
    "-" : QOp.MINUS,
    "*" : QOp.TIMES,
    "/" : QOp.DIVIDE,
    "<" : QOp.LCOMP,
    ">" : QOp.RCOMP,
    "<=" : QOp.LCOMP_EQUAL,
    ">=" : QOp.RCOMP_EQUAL,
    "==" : QOp.EQUAL_EQUAL,
    "!=" : QOp.EXC_EQUAL,
    "&&" : QOp.AND,
    "||" : QOp.OR
}

state_toquadop = {
    "BG" : QOp.BG,
    "COLOR" : QOp.COLOR,
    "PENDOWN" : QOp.PENDOWN,
    "PENUP" : QOp.PENUP,
    "WIDTH" : QOp.WIDTH,
    "CIRCLE" : QOp.CIRCLE,
    "GO" : QOp.GO,
    "RIGHT" : QOp.RIGHT,
    "LEFT" : QOp.LEFT,
    "ORIENTATION" : QOp.ORIENTATION,
}

def get_quad_operation_from_operator(operator):
    return operator_to_quadop[operator]

def get_quad_operation_from_state(state):
    return state_toquadop[state]

def get_error_message(error, var = '', type_mism = {}, n_expected_args = 0, fun_type_mism = {}, ret_type_mism = {} , msg = ""):
    if error == Error.REDECLARED_VARIABLE:
        return "Error : " + f"Variable '{var}' already declared"
    elif error == Error.VARIABLE_NOT_DECLARED:
         return "Error : " + f"Variable '{var}' not declared before"
    elif error == Error.DUPLICATED_ARGS:
        return "Error : Duplicated Args"
    elif error == Error.TYPE_MISMATCH:
        return "Error :  Type Mismatch " + f"Using '{type_mism['operator']}' with exp of type '{type_mism['left']}' and exp of type '{type_mism['right']}'"
    elif error == Error.EXPRESSION_WENT_WRONG:
        return "Error : Expression went wrong"
    elif error == Error.IF_EXPRESSION_MUST_BE_BOOL:
        return "Error : If Expression must be bool"
    elif error == Error.INTERNAL_STACKS:
        return "Internal Error involving STACKS " + msg
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
        return "Error : " + f"Variable '{var}' is not iterable"
    elif error == Error.FUNCTION_PARAMS_DIFF:
        return "Error : " + f"Function '{var}' was expecting {n_expected_args} params"
    elif error == Error.FUNCTION_PARAM_TYPE_MISMATCH:
        return "Error : " + f"Function '{fun_type_mism['id']}' was expecting on param '{fun_type_mism['param']}' type '{fun_type_mism['param_type']}' but got type '{fun_type_mism['arg_type']}'"
    elif error == Error.VOID_IN_EXPRESION:
        return f"Error : Can't use void function {var} on expresions"
    elif error == Error.FUNCTION_MUST_HAVE_RETURN:
        return f"Error : Function '{var}' must have return statement at the end"
    elif error == Error.FUNTION_RETURN_TYPE_MISMATCH:
        return f"Error : Type mismatch on function '{ret_type_mism['var']}' of type {ret_type_mism['type']} is not the same as return : QOp.BG, of type {ret_type_mism['ret_type']}"
    else:
        return "Error not found"
    
def initialStateSymbols(w = 800,h = 700): 
    return {
        'GET_POS_X' : {Var.ID : 'GET_POS_X' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : w/2, Var.DIR_VIR: 0},
        'GET_POS_Y' : {Var.ID : 'GET_POS_Y' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : h/2, Var.DIR_VIR: 1},
        'GET_BG' : {Var.ID : 'GET_BG' , Var.TIPO : Tipo.STRING, Var.KIND : Kind.STATE, Var.VAL : Color.WHITE, Var.DIR_VIR: 2},
        'GET_COLOR' : {Var.ID : 'GET_COLOR' , Var.TIPO : Tipo.STRING, Var.KIND : Kind.STATE, Var.VAL : Color.BLACK, Var.DIR_VIR: 3},
        'IS_PENDOWN' : {Var.ID : 'IS_PENDOWN' , Var.TIPO : Tipo.BOOL, Var.KIND : Kind.STATE, Var.VAL : False, Var.DIR_VIR: 4},
        'IS_PENUP' : {Var.ID : 'IS_PENDOWN' , Var.TIPO : Tipo.BOOL, Var.KIND : Kind.STATE, Var.VAL : True, Var.DIR_VIR: 5},
        'GET_WIDTH' : {Var.ID : 'GET_WIDTH' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : 1, Var.DIR_VIR: 6},
        'GET_ORIENTATION' : {Var.ID : 'GET_ORIENTATION' , Var.TIPO : Tipo.FLOAT, Var.KIND : Kind.STATE, Var.VAL : 0, Var.DIR_VIR: 7},
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
    elif tipo == "VOID":
        return Tipo.VOID
    else:
        return Tipo.NOT_DECLARED