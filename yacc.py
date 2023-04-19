import os
from lex import MyLexer
from ply.yacc import yacc
import sys

lexer = MyLexer()
lexer.build()
tokens = lexer.tokens

def p_codigo(p):
    '''
    codigo : funcion codigoP
    | estatuto codigoP
    '''
    p[0] = 'CORRECTO'

def p_codigoP(p):
    '''
    codigoP : codigo
    | empty
    '''
    p[0] = ''

def p_funcion(p):
    '''
    funcion : FUNCTION ID args tipoFuncion bloque
    '''
    p[0] = ''

def p_tipoFuncion(p):
    '''
    tipoFuncion : DOTS tipo 
    | empty
    '''
    p[0] = ''

def p_args(p):
    '''
    args : LPAREN argsS RPAREN
    '''
    p[0] = ''

def p_argsS(p):
    '''
    argsS : argsP 
    | empty
    '''
    p[0] = ''

def p_argsP(p):
    '''
    argsP : arg argsPP
    '''
    p[0] = ''

def p_argsPP(p):
    '''
    argsPP : COMMA arg 
    | empty
    '''
    p[0] = ''

def p_arg(p):
    '''
    arg : tipo ID argP
    '''
    p[0] = ''

def p_argP(p):
    '''
    argP : LSQBRACKET RSQBRACKET argPP 
    | empty
    '''
    p[0] = ''

def p_argPP(p):
    '''
    argPP : LSQBRACKET RSQBRACKET  
    | empty
    '''
    p[0] = ''

def p_estatuto(p):
    '''
    estatuto : condicion
    | ciclo
    | asignacion
    | declarar
    | estado
    | llamar
    '''
    p[0] = ''

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
    declarar : tipo declararS declararP
    '''
    p[0] = ''

def p_declararP(p):
    '''
    declararP : COMMA declararS declararP
    | empty
    '''
    p[0] = ''

def p_declararS(p):
    '''
    declararS : ID declararSOpciones
    '''
    p[0] = ''

def p_declararSOpciones(p):
    '''
    declararSOpciones : EQUAL expresion 
    | declararArray 
    | empty
    '''
    p[0] = ''

def p_declararArray(p):
    '''
    declararArray : LSQBRACKET ICTE RSQBRACKET declararArrayP
    '''
    p[0] = ''

def p_declararArrayP(p):
    '''
    declararArrayP : LSQBRACKET ICTE RSQBRACKET declararArrayPP 
    | inicializaArray 
    | empty
    '''
    p[0] = ''

def p_declararArrayPP(p):
    '''
    declararArrayPP : inicializaArray 
    | empty
    '''
    p[0] = ''

def p_inicializaArray(p):
    '''
    inicializaArray : EQUAL acte 
    | empty
    '''
    p[0] = ''

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
    p[0] = ''

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
    | ID LPAREN llamarP RPAREN 
    '''
    p[0] = ''

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
    p[0] = ''

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

def p_empty(p):
    '''
    empty : 
    '''
    p[0] = ''

# Build the parser
parser = yacc()

files = sys.argv[1:] if len(sys.argv) > 1 else os.listdir('examples')

for fileName in files:
    with open("examples/" + fileName) as file:
        print(fileName)
        print('---')
        data = file.read()
        ast = parser.parse(data)
        print(ast)
        print('---')

