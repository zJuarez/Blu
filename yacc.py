import os
from lex import MyLexer
from ply.yacc import yacc
import sys
from enum import Enum

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
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def add_symbol(self, name, attributes):
        self.symbols[name] = attributes
    
    def get_parent(self):
        return self.parent
    
    def is_declarated_in_block(self, name):
        return name in self.symbols
    
    def get_symbol(self, name):
        symbol_table = self
        while symbol_table:
            if name in symbol_table.symbols:
                return symbol_table.symbols[name]
            symbol_table = symbol_table.parent
        return None

class VarsState:
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

global curr_symbol_table, curr_state
global errores 
errores = False
curr_symbol_table = SymbolTable()
curr_state = VarsState()

lexer = MyLexer()
lexer.build()
tokens = lexer.tokens

def p_codigo(p):
    '''
    codigo : funcion codigoP
    | estatuto codigoP
    '''
    p[0] = ('CORRECTO' if errores == False  else "INCORRECTO" , [p[1]] + [p[2]])
def p_codigoP(p):
    '''
    codigoP : codigo
    | empty
    '''
    p[0] = () if p[1] == 'empty' else p[1]

def p_funcion(p):
    '''
    funcion : tipoFuncion idFun args bloquefun
    '''
    p[0] = ''

def p_idFun(p):
    '''
    idFun : ID
    '''
    # poner en el estado el id de la funcion
    curr_state.add_info(Var.ID, p[1])

def p_tipoFuncion(p):
    '''
    tipoFuncion :  tipo 
    | VOID
    '''
     # 1 almacenar el tipo de la funcion
    curr_state.add_info(Var.TIPO, p[1])

def p_args(p):
    '''
    args : LPAREN argsS RPAREN
    '''
    global curr_symbol_table
    # traer el id de la funcion que acabamos de guardar
    id = curr_state.get_info(Var.ID)
    # traer el tipo de la funcion que acabamos de guardar
    tipo = curr_state.get_info(Var.TIPO)
    # crear los atributos de la funcion con sus args y su tipo funcion
    function_attrs = {Var.ID : id, Var.TIPO : tipo, Var.ARGS : p[2], Var.KIND : Kind.FUNCTION}

    # añadir a la tabla de simbolos actual para que pueda ser usada despues
    curr_symbol_table.add_symbol(id, function_attrs)
    # crear nueva tabla para el bloque de funcion con padre la tabla actual
    curr_symbol_table = SymbolTable(parent=curr_symbol_table)
    # los args deben de vivir dentro de este bloque -> añadir
    for id, symbol_attrs in p[2].items():
        curr_symbol_table.add_symbol(id, symbol_attrs)

    # devolver args si acaso sirve
    p[0] = p[2]

def p_argsS(p):
    '''
    argsS : argsP 
    | empty
    '''
    p[0] = {} if p[1] == 'empty' else p[1]

def p_argsP(p):
    '''
    argsP : arg argsPP
    '''
    repeated_keys = set(p[1].keys()) & set(p[2].keys())
    if(repeated_keys):
        p_error(Error.DUPLICATED_ARGS)
    
    p[0] = p[1] | p[2]

def p_argsPP(p):
    '''
    argsPP : COMMA arg 
    | empty
    '''
    p[0] = {} if p[1] == 'empty' else p[2]

def p_arg(p):
    '''
    arg : tipo ID argP
    '''
    var = {Var.ID : p[2], Var.TIPO : p[1]} | p[3]
    p[0] = {p[2] : var}

def p_argP(p):
    '''
    argP : LSQBRACKET RSQBRACKET argPP 
    | empty
    '''
    p[0] = {Var.KIND : Kind.SINGLE} if(len(p) <4) else p[3]

def p_argPP(p):
    '''
    argPP : LSQBRACKET RSQBRACKET  
    | empty
    '''
    p[0] = {Var.KIND : Kind.ARRAY} if(len(p) <3) else {Var.KIND : Kind.MATRIX}

def p_bloquefun(p):
    '''
    bloquefun : LBRACKET bloquefunP RBRACKET
    '''
    p[0] = ''

def p_bloquefunP(p):
    '''
    bloquefunP : estatuto bloquefunP 
    | empty
    '''
    p[0] = ''

def p_lbracketfun(p):
    '''
    lbracketfun : LBRACKET
    '''
    # add function var to current block

    # create new block
    global curr_symbol_table
    curr_symbol_table = SymbolTable(parent=curr_symbol_table)
    p[0] = ''

def p_rbracketfun(p):
    '''
    rbracketfun : RBRACKET
    '''
    # destroy block
    global curr_symbol_table
    curr_symbol_table = curr_symbol_table.get_parent() 
    p[0] = ''

def p_bloqueifP(p):
    '''
    bloqueifP : estatuto bloqueifP 
    | empty
    '''
    p[0] = []

def p_estatuto(p):
    '''
    estatuto : condicion
    | ciclo
    | asignacion
    | declarar
    | estado
    | llamar
    '''
    p[0] = p[1]

def p_condicion(p):
    '''
    condicion : IF LPAREN expresion RPAREN bloque condicionElse
    '''
    p[0] = ''

def p_condicionElse(p):
    '''
    condicionElse : ELSE condicionElseP 
    | empty
    '''
    p[0] = ''

def p_condicionElseP(p):
    '''
    condicionElseP : IF LPAREN expresion RPAREN bloque condicionElse
    | bloque
    '''
    p[0] = ''

def p_ciclo(p):
    '''
    ciclo : FOR LPAREN cicloCont RPAREN bloque
    '''
    p[0] = ''

def p_cicloCont(p):
    '''
    cicloCont : ICTE
    | ID COMMA ICTE COMMA ICTE
    | decSimple COMMA expresion COMMA asignacionS
    | ID IN cicloArray
    '''
    p[0] = ''

def p_decSimple(p):
    '''
    decSimple : tipo ID EQUAL expresion
    '''
    p[0] = ''

def p_cicloArray(p):
    '''
    cicloArray : expresion
    | acte
    '''
    p[0] = ''

def p_asignacion(p):
    '''
    asignacion : asignacionS asignacionP
    '''
    p[0] = ''

def p_asignacionP(p):
    '''
    asignacionP : COMMA asignacion
    | empty
    '''
    p[0] = ''

def p_asignacionS(p):
    '''
    asignacionS : ID asignacionSA EQUAL expresion
    '''
    p[0] = ''

def p_asignacionSA(p):
    '''
    asignacionSA : LSQBRACKET expresion RSQBRACKET asignacionSM
    | empty
    '''
    p[0] = ''

def p_asignacionSM(p):
    '''
    asignacionSM : LSQBRACKET expresion RSQBRACKET 
    | empty
    '''
    p[0] = ''

def p_declarar(p):
    '''
    declarar : tipo declararSimple declararP
    '''
    
    # 11 limpiar curr state ?
    curr_state.clear()
    p[0] = ('DECLARAR' , [p[2]] + p[3])

def p_declararP(p):
    '''
    declararP : COMMA declararSimple declararP
    | empty
    '''
    p[0] = [] if (p[1] == 'empty') else [p[2]] + p[3]

def p_declararSimple(p):
    '''
    declararSimple : ID declararSimpleOpciones
    '''
    # 2 almacenar el id
    id = p[1]
    var = {}
     # 3 el id ya existe ?
    if(curr_symbol_table.is_declarated_in_block(id)):
       p_error(get_error_message(Error.REDECLARED_VARIABLE, id))
    else : 
        # 10 añadir la variable a la tabla de variables
        var = {Var.ID : id, Var.TIPO : curr_state.get_info(Var.TIPO)} | p[2]
        curr_symbol_table.add_symbol(id, var)
        print("añadiendo a la tabla " + str(id))
    p[0] = var

def p_declararSimpleOpciones(p):
    '''
    declararSimpleOpciones : EQUAL expresion 
    | declararArray 
    | empty
    '''
    # esta inicializando la variable
    if len(p) > 2:
        # 9 guardar el valor de la variable declarada
        p[0] = {Var.VAL : p[2]}
        # TODO : Verificar que el el tipo de la expresion y de la variable sean iguales TYPE_MISMATCH
    else:
        p[0] = p[1] if(p[1] != 'empty') else {}

def p_declararArray(p):
    '''
    declararArray : LSQBRACKET ICTE RSQBRACKET declararArrayP
    '''
    # 4 La primera dimension del arreglo o matriz es de tamaño p[2]
    p[0] = {Var.DIM1: p[2]} | p[4]

def p_declararArrayP(p):
    '''
    declararArrayP : LSQBRACKET ICTE RSQBRACKET declararArrayPP 
    | inicializaArray 
    | empty
    '''
    var = {}
    # esta declarando una matriz
    if(len(p) > 2):
        # 5 La segunda dimension de la matriz es de tamaño p[2]
        var|={Var.DIM2 : p[2]}
        # 7 establecer que se declara un MATRIX
        var|={Var.KIND : Kind.MATRIX}
        # puede tener valor
        var|=p[4]
    else:
        # 6 establecer que se declara un array
        var|={Var.KIND : Kind.ARRAY}
        # se inicializo el array
        if p[1] != 'empty':
            var|= p[1]

    p[0] = var

def p_declararArrayPP(p):
    '''
    declararArrayPP : inicializaArray 
    | empty
    '''
    p[0] = p[1] if p[1] != 'empty' else {}

def p_inicializaArray(p):
    '''
    inicializaArray : EQUAL acte 
    | empty
    '''
    # esta inicializando el array
    if p[1] != 'empty':
        # 8 guardar el valor del array o matriz TODO p[2]
        # por mientras guardar otra cosa
        p[0] = {Var.VAL: 'mi valor es un array o matriz'}
    else:
        p[0] = {}

def p_cte(p):
    '''
    cte : ICTE 
    | FCTE
    | SCTE
    | CCTE
    | bcte
    '''
    p[0] = ''

def p_bcte(p):
    '''
    bcte : TRUE
    | FALSE
    '''
    p[0] = ''

def p_ascte(p):
    '''
    ascte : LSQBRACKET ascteP RSQBRACKET
    '''
    p[0] = ''

def p_ascteP(p):
    '''
    ascteP : cte asctePP
    '''
    p[0] = ''

def p_asctePP(p):
    '''
    asctePP : COMMA ascteP 
    | empty
    '''
    p[0] = ''

def p_acte(p):
    '''
    acte : LSQBRACKET acteP RSQBRACKET
    '''
    p[0] = p[1]

def p_acteP(p):
    '''
    acteP : cte actePP
    | ascte actePP
    '''
    p[0] = ''

def p_actePP(p):
    '''
    actePP : COMMA acteP 
    | empty
    '''
    p[0] = ''


def p_estado(p):
    '''
    estado : POS expresion expresion
    |  BG expresion
    | COLOR expresion
    | PENDOWN
    | PENUP
    | WIDTH expresion
    | CIRCLE expresion
    | GO expresion
    | RIGHT expresion
    | LEFT expresion
    | ORIENTATION expresion
    | print
    '''
    p[0] = ''

def p_print(p):
    '''
    print : PRINT expresion printP 
    '''
    p[0] = ''

def p_printP(p):
    '''
    printP : expresion printP
    | empty 
    '''
    p[0] = ''

def p_llamar(p):
    '''
    llamar : drawFunc
    | idllamar LPAREN llamarP RPAREN 
    '''
    p[0] = ''

def p_idllamar(p):
    '''
    idllamar : ID
    '''
    # function exists -> its declared before in any other higher block
    if (curr_symbol_table.get_symbol(p[1])):
        curr_state.add_info(Var.ID, p[1])
    else:
        p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
    p[0] = p[1]
def p_llamarP(p):
    '''
    llamarP : expresion llamarPP
    | empty 
    '''
    p[0] = ''

def p_llamarPP(p):
    '''
    llamarPP : COMMA expresion llamarPP
    | empty 
    '''
    p[0] = ''

def p_drawFunc(p):
    '''
    drawFunc : CURVE_C expresion expresion expresion expresion
    | CURVE_Q expresion expresion expresion expresion expresion expresion
    | CIRCLE expresion
    '''
    p[0] = ''

def p_tipo(p):
    '''
    tipo : INT 
    | FLOAT
    | STRING
    | CHAR
    | BOOL
    '''
     # 1 almacenar el tipo de la variable
    curr_state.add_info(Var.TIPO, p[1])
    p[0] = p[1]

def p_bloqueif(p):
    '''
    bloqueif : lbracketif bloqueP rbracketif
    '''
    p[0] = ''

def p_lbracketif(p):
    '''
    lbracketif : LBRACKET
    '''
    # create new block
    global curr_symbol_table
    curr_symbol_table = SymbolTable(parent=curr_symbol_table)
    p[0] = ''

def p_rbracketif(p):
    '''
    rbracketif : RBRACKET
    '''
    # destroy block
    global curr_symbol_table
    curr_symbol_table = curr_symbol_table.get_parent() 
    
    p[0] = ''

def p_bloqueifP(p):
    '''
    bloqueifP : estatuto bloqueifP 
    | empty
    '''
    p[0] = ''

def p_expresion(p):
    '''
    expresion : expresionA expresionP
    '''
    p[0] = ''

def p_expresionP(p):
    '''
    expresionP : BAR BAR expresionA expresionP 
    | empty
    '''
    p[0] = ''

def p_expresionA(p):
    '''
    expresionA : expresionB expresionAP
    '''
    p[0] = ''

def p_expresionAP(p):
    '''
    expresionAP : AMPERSON AMPERSON expresionB expresionAP
    | empty
    '''
    p[0] = ''

def p_expresionB(p):
    '''
    expresionB : exp op exp
    | exp
    '''
    p[0] = ''

def p_op(p):
    '''
    op : LCOMP
    | RCOMP
    | LCOMP EQUAL
    | RCOMP EQUAL
    | EQUAL EQUAL
    | EXC EQUAL
    '''
    p[0] = ''

def p_exp(p):
    '''
    exp : termino expP 
    '''
    p[0] = ''

def p_expP(p):
    '''
    expP : PLUS exp
    | MINUS exp 
    | empty
    '''
    p[0] = ''

def p_termino(p):
    '''
    termino : factor terminoP 
    '''
    p[0] = ''

def p_terminoP(p):
    '''
    terminoP : TIMES termino
    | DIVIDE termino 
    | empty
    '''
    p[0] = ''

def p_getEstado(p):
    '''
    getEstado : GET_POS_X
    | GET_POS_Y
    | GET_BG
    | GET_COLOR
    | IS_PENDOWN
    | IS_PENUP
    | GET_WIDTH
    | GET_ORIENTATION
    '''
    p[0] = ''

def p_factor(p):
    '''
    factor : cte
    | var
    | getEstado
    | LPAREN expresion RPAREN
    '''
    p[0] = ''

def p_var(p):
    '''
    var : ID varP
    '''
    # 1 si el id no existe error
    symbol = curr_symbol_table.get_symbol(p[1])
    if (symbol is None):
         p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
    
    # devolver algo interesante
    p[0] = ''

def p_varP(p):
    '''
    varP : varPFuncion
    | varPArray
    | empty
    '''
    p[0] = ''

def p_varPFuncion(p):
    '''
    varPFuncion : LPAREN varPFuncionCont RPAREN
    '''
    p[0] = ''

def p_varPFuncionCont(p):
    '''
    varPFuncionCont : expresion varPFuncionContP
    | empty
    '''
    p[0] = ''

def p_varPFuncionContP(p):
    '''
    varPFuncionContP : COMMA expresion varPFuncionContP
    | empty
    '''
    p[0] = ''

def p_varPArray(p):
    '''
    varPArray : LSQBRACKET expresion RSQBRACKET varPArrayP
    '''
    p[0] = ''

def p_varPArrayP(p):
    '''
    varPArrayP : LSQBRACKET expresion RSQBRACKET 
    | empty
    '''
    p[0] = ''

# TODO CHECK

def p_bloque(p):
    '''
    bloque : LBRACKET bloqueP RBRACKET
    '''
    p[0] = ''

def p_bloqueP(p):
    '''
    bloqueP : estatuto bloqueP 
    | empty
    '''
    p[0] = ''

def p_empty(p):
    '''
    empty : 
    '''
    p[0] = 'empty'

def p_error(p):
    global errores
    errores = True
    print(p)

# Build the parser
parser = yacc()

def run(code):
    return parser.parse(code)