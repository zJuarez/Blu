from ply.lex import lex
from ply.yacc import yacc
from lex import MyLexer
from SymbolTable import SymbolTable
from State import *

class MyParser:
    def __init__(self):
        self.lexer = MyLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc(module=self)

    def clear_state(self):
        self.errores = 0
        self.curr_symbol_table = SymbolTable()
        self.curr_state = State()

    def p_codigo(self, p):
        '''
        codigo : funcion codigoP
        | estatuto codigoP
        '''
        p[0] = ('CORRECTO' if self.errores == 0  else "INCORRECTO" , [p[1]] + [p[2]])

    def p_codigoP(self, p):
        '''
        codigoP : codigo
        | empty
        '''
        p[0] = () if p[1] == 'empty' else p[1]

    def p_funcion(self, p):
        '''
        funcion : tipoFuncion idFun args bloquefun
        '''
        p[0] = ''

    def p_idFun(self, p):
        '''
        idFun : ID
        '''
        # poner en el estado el id de la funcion
        self.curr_state.add_info(Var.ID, p[1])

    def p_tipoFuncion(self, p):
        '''
        tipoFuncion :  tipo 
        | VOID
        '''
        # 1 almacenar el tipo de la funcion
        self.curr_state.add_info(Var.TIPO, p[1])

    def p_args(self, p):
        '''
        args : LPAREN argsS RPAREN
        '''
        # traer el id de la funcion que acabamos de guardar
        id = self.curr_state.get_info(Var.ID)
        # traer el tipo de la funcion que acabamos de guardar
        tipo = self.curr_state.get_info(Var.TIPO)
        # crear los atributos de la funcion con sus args y su tipo funcion
        function_attrs = {Var.ID : id, Var.TIPO : tipo, Var.ARGS : p[2], Var.KIND : Kind.FUNCTION}

        # añadir a la tabla de simbolos actual para que pueda ser usada despues
        self.curr_symbol_table.add_symbol(id, function_attrs)
        # crear nueva tabla para el bloque de funcion con padre la tabla actual
        self.curr_symbol_table = SymbolTable(parent=self.curr_symbol_table)
        # los args deben de vivir dentro de este bloque -> añadir
        for id, symbol_attrs in p[2].items():
            self.curr_symbol_table.add_symbol(id, symbol_attrs)

        # devolver args si acaso sirve
        p[0] = p[2]

    def p_argsS(self, p):
        '''
        argsS : argsP 
        | empty
        '''
        p[0] = {} if p[1] == 'empty' else p[1]

    def p_argsP(self, p):
        '''
        argsP : arg argsPP
        '''
        repeated_keys = set(p[1].keys()) & set(p[2].keys())
        if(repeated_keys):
            self.p_error(Error.DUPLICATED_ARGS)
        
        p[0] = p[1] | p[2]

    def p_argsPP(self, p):
        '''
        argsPP : COMMA arg 
        | empty
        '''
        p[0] = {} if p[1] == 'empty' else p[2]

    def p_arg(self, p):
        '''
        arg : tipo ID argP
        '''
        var = {Var.ID : p[2], Var.TIPO : p[1]} | p[3]
        p[0] = {p[2] : var}

    def p_argP(self, p):
        '''
        argP : LSQBRACKET RSQBRACKET argPP 
        | empty
        '''
        p[0] = {Var.KIND : Kind.SINGLE} if(len(p) <4) else p[3]

    def p_argPP(self, p):
        '''
        argPP : LSQBRACKET RSQBRACKET  
        | empty
        '''
        p[0] = {Var.KIND : Kind.ARRAY} if(len(p) <3) else {Var.KIND : Kind.MATRIX}

    def p_bloquefun(self, p):
        '''
        bloquefun : LBRACKET bloquefunP RBRACKET
        '''
        p[0] = ''

    def p_bloquefunP(self, p):
        '''
        bloquefunP : estatuto bloquefunP 
        | empty
        '''
        p[0] = ''

    def p_lbracketfun(self, p):
        '''
        lbracketfun : LBRACKET
        '''
        # add function var to current block

        # create new block
        self.curr_symbol_table = SymbolTable(parent=self.curr_symbol_table)
        p[0] = ''

    def p_rbracketfun(self, p):
        '''
        rbracketfun : RBRACKET
        '''
        # destroy block
        self.curr_symbol_table = self.curr_symbol_table.get_parent() 
        p[0] = ''

    def p_bloqueifP(self, p):
        '''
        bloqueifP : estatuto bloqueifP 
        | empty
        '''
        p[0] = []

    def p_estatuto(self, p):
        '''
        estatuto : condicion
        | ciclo
        | asignacion
        | declarar
        | estado
        | llamar
        '''
        p[0] = p[1]

    def p_condicion(self, p):
        '''
        condicion : IF LPAREN expresion RPAREN bloqueif condicionElse
        '''
        p[0] = ''

    def p_condicionElse(self, p):
        '''
        condicionElse : ELSE condicionElseP 
        | empty
        '''
        p[0] = ''

    def p_condicionElseP(self, p):
        '''
        condicionElseP : IF LPAREN expresion RPAREN bloqueif condicionElse
        | bloqueif
        '''
        p[0] = ''

    def p_ciclo(self, p):
        '''
        ciclo : forr LPAREN cicloCont RPAREN bloqueCiclo
        '''
        p[0] = ''

    def p_bloqueCiclo(self, p):
        '''
        bloqueCiclo : LBRACKET bloqueCicloP RBRACKET
        '''
        # finalizar el ciclo acaba las variables del bloque del ciclo
        self.curr_symbol_table = self.curr_symbol_table.get_parent()
        p[0] = ''

    def p_bloqueCicloP(self, p):
        '''
        bloqueCicloP : estatuto bloqueCicloP 
        | empty
        '''
        p[0] = ''

    def p_forr(self, p):
        '''
        forr : FOR
        '''
        # start new block
        self.curr_symbol_table = SymbolTable(parent=self.curr_symbol_table)
        p[0] = ''

    def p_cicloCont(self, p):
        '''
        cicloCont : ICTE
        | ID COMMA ICTE COMMA ICTE
        | decSimple COMMA expresion COMMA asignacionS
        | ID IN cicloArray
        '''
        if(len(p) == 4):
            # deducir que tipo de variable es id y que kind y agregarla
            # usar p[3] para deducr esto
            # TODO: por ahora solo mete el id en el bloque
            self.curr_symbol_table.add_symbol(p[1], {Var.ID : p[1]})
        elif(len(p) > 4):
            if  type(p[1]) is str:
                # is an id
                symbol = {p[1] : {Var.ID: p[2], Var.TIPO : "INT", Var.KIND : Kind.SINGLE, Var.VAL : p[3]}}
                # adding id as cont in block
                self.curr_symbol_table.add_symbol_object(symbol)
        p[0] = ''

    def p_decSimple(self, p):
        '''
        decSimple : tipo ID EQUAL expresion
        '''
        # TODO check type mismatch
        symbol = {p[2] : {Var.ID: p[2], Var.TIPO : p[1], Var.KIND : Kind.SINGLE, Var.VAL : p[4]}}
        # adding dec simple to table
        self.curr_symbol_table.add_symbol_object(symbol)

        p[0] = symbol

    def p_cicloArray(self, p):
        '''
        cicloArray : expresion
        | acte
        '''
        # devuelve que tipo de array es
        p[0] = {}

    def p_asignacion(self, p):
        '''
        asignacion : asignacionS asignacionP
        '''
        p[0] = ''

    def p_asignacionP(self, p):
        '''
        asignacionP : COMMA asignacion
        | empty
        '''
        p[0] = ''

    def p_asignacionS(self, p):
        '''
        asignacionS : idAS asignacionSA EQUAL expresion
        '''
        p[0] = ''

    def p_idAS(self, p):
        '''
        idAS : ID
        '''
        # id debe de existir
        if(self.curr_symbol_table.get_symbol(p[1]) is None):
            # not found
            self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
        p[0] = p[1]
    def p_asignacionSA(self, p):
        '''
        asignacionSA : LSQBRACKET expresion RSQBRACKET asignacionSM
        | empty
        '''
        p[0] = ''

    def p_asignacionSM(self, p):
        '''
        asignacionSM : LSQBRACKET expresion RSQBRACKET 
        | empty
        '''
        p[0] = ''

    def p_declarar(self, p):
        '''
        declarar : tipo declararSimple declararP
        '''
        
        # 11 limpiar curr state ?
        self.curr_state.clear()
        p[0] = ('DECLARAR' , [p[2]] + p[3])

    def p_declararP(self, p):
        '''
        declararP : COMMA declararSimple declararP
        | empty
        '''
        p[0] = [] if (p[1] == 'empty') else [p[2]] + p[3]

    def p_declararSimple(self, p):
        '''
        declararSimple : ID declararSimpleOpciones
        '''
        # 2 almacenar el id
        id = p[1]
        var = {}
        # 3 el id ya existe ?
        if(self.curr_symbol_table.is_declarated_in_block(id)):
            self.p_error(get_error_message(Error.REDECLARED_VARIABLE, id))
        else : 
            # 10 añadir la variable a la tabla de variables
            var = {Var.ID : id, Var.TIPO : self.curr_state.get_info(Var.TIPO)} | p[2]
            self.curr_symbol_table.add_symbol(id, var)
            print("añadiendo a la tabla " + str(id))
        p[0] = var

    def p_declararSimpleOpciones(self, p):
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

    def p_declararArray(self, p):
        '''
        declararArray : LSQBRACKET ICTE RSQBRACKET declararArrayP
        '''
        # 4 La primera dimension del arreglo o matriz es de tamaño p[2]
        p[0] = {Var.DIM1: p[2]} | p[4]

    def p_declararArrayP(self, p):
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

    def p_declararArrayPP(self, p):
        '''
        declararArrayPP : inicializaArray 
        | empty
        '''
        p[0] = p[1] if p[1] != 'empty' else {}

    def p_inicializaArray(self, p):
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

    def p_cte(self, p):
        '''
        cte : ICTE 
        | FCTE
        | SCTE
        | CCTE
        | bcte
        '''
        p[0] = ''

    def p_bcte(self, p):
        '''
        bcte : TRUE
        | FALSE
        '''
        p[0] = ''

    def p_ascte(self, p):
        '''
        ascte : LSQBRACKET ascteP RSQBRACKET
        '''
        p[0] = ''

    def p_ascteP(self, p):
        '''
        ascteP : cte asctePP
        '''
        p[0] = ''

    def p_asctePP(self, p):
        '''
        asctePP : COMMA ascteP 
        | empty
        '''
        p[0] = ''

    def p_acte(self, p):
        '''
        acte : LSQBRACKET acteP RSQBRACKET
        '''
        p[0] = p[1]

    def p_acteP(self, p):
        '''
        acteP : cte actePP
        | ascte actePP
        '''
        p[0] = ''

    def p_actePP(self, p):
        '''
        actePP : COMMA acteP 
        | empty
        '''
        p[0] = ''


    def p_estado(self, p):
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

    def p_print(self, p):
        '''
        print : PRINT expresion printP 
        '''
        p[0] = ''

    def p_printP(self, p):
        '''
        printP : expresion printP
        | empty 
        '''
        p[0] = ''

    def p_llamar(self, p):
        '''
        llamar : drawFunc
        | idllamar LPAREN llamarP RPAREN 
        '''
        p[0] = ''

    def p_idllamar(self, p):
        '''
        idllamar : ID
        '''
        # function exists -> its declared before in any other higher block
        if (self.curr_symbol_table.get_symbol(p[1])):
            self.curr_state.add_info(Var.ID, p[1])
        else:
            self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
        p[0] = p[1]

    def p_llamarP(self, p):
        '''
        llamarP : expresion llamarPP
        | empty 
        '''
        p[0] = ''

    def p_llamarPP(self, p):
        '''
        llamarPP : COMMA expresion llamarPP
        | empty 
        '''
        p[0] = ''

    def p_drawFunc(self, p):
        '''
        drawFunc : CURVE_C expresion expresion expresion expresion
        | CURVE_Q expresion expresion expresion expresion expresion expresion
        | CIRCLE expresion
        '''
        p[0] = ''

    def p_tipo(self, p):
        '''
        tipo : INT 
        | FLOAT
        | STRING
        | CHAR
        | BOOL
        '''
        # 1 almacenar el tipo de la variable
        self.curr_state.add_info(Var.TIPO, p[1])
        p[0] = p[1]

    def p_bloqueif(self, p):
        '''
        bloqueif : lbracketif bloqueP rbracketif
        '''
        p[0] = ''

    def p_bloqueifP(self, p):
        '''
        bloqueifP : estatuto bloqueifP 
        | empty
        '''
        p[0] = ''

    def p_lbracketif(self, p):
        '''
        lbracketif : LBRACKET
        '''
        # create new block
        self.curr_symbol_table = SymbolTable(parent=self.curr_symbol_table)
        p[0] = ''

    def p_rbracketif(self, p):
        '''
        rbracketif : RBRACKET
        '''
        # destroy block
        self.curr_symbol_table = self.curr_symbol_table.get_parent() 
        
        p[0] = ''



    def p_expresion(self, p):
        '''
        expresion : expresionA expresionP
        '''
        p[0] = ''

    def p_expresionP(self, p):
        '''
        expresionP : BAR BAR expresionA expresionP 
        | empty
        '''
        p[0] = ''

    def p_expresionA(self, p):
        '''
        expresionA : expresionB expresionAP
        '''
        p[0] = ''

    def p_expresionAP(self, p):
        '''
        expresionAP : AMPERSON AMPERSON expresionB expresionAP
        | empty
        '''
        p[0] = ''

    def p_expresionB(self, p):
        '''
        expresionB : exp op exp
        | exp
        '''
        p[0] = ''

    def p_op(self, p):
        '''
        op : LCOMP
        | RCOMP
        | LCOMP EQUAL
        | RCOMP EQUAL
        | EQUAL EQUAL
        | EXC EQUAL
        '''
        p[0] = ''

    def p_exp(self, p):
        '''
        exp : termino expP 
        '''
        p[0] = ''

    def p_expP(self, p):
        '''
        expP : PLUS exp
        | MINUS exp 
        | empty
        '''
        p[0] = ''

    def p_termino(self, p):
        '''
        termino : factor terminoP 
        '''
        p[0] = ''

    def p_terminoP(self, p):
        '''
        terminoP : TIMES termino
        | DIVIDE termino 
        | empty
        '''
        p[0] = ''

    def p_getEstado(self, p):
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

    def p_factor(self, p):
        '''
        factor : cte
        | var
        | getEstado
        | LPAREN expresion RPAREN
        '''
        p[0] = ''

    def p_var(self, p):
        '''
        var : ID varP
        '''
        # 1 si el id no existe error
        symbol = self.curr_symbol_table.get_symbol(p[1])
        if (symbol is None):
            self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
        
        # devolver algo interesante
        p[0] = ''

    def p_varP(self, p):
        '''
        varP : varPFuncion
        | varPArray
        | empty
        '''
        p[0] = ''

    def p_varPFuncion(self, p):
        '''
        varPFuncion : LPAREN varPFuncionCont RPAREN
        '''
        p[0] = ''

    def p_varPFuncionCont(self, p):
        '''
        varPFuncionCont : expresion varPFuncionContP
        | empty
        '''
        p[0] = ''

    def p_varPFuncionContP(self, p):
        '''
        varPFuncionContP : COMMA expresion varPFuncionContP
        | empty
        '''
        p[0] = ''

    def p_varPArray(self, p):
        '''
        varPArray : LSQBRACKET expresion RSQBRACKET varPArrayP
        '''
        p[0] = ''

    def p_varPArrayP(self, p):
        '''
        varPArrayP : LSQBRACKET expresion RSQBRACKET 
        | empty
        '''
        p[0] = ''

    def p_bloque(self, p):
        '''
        bloque : LBRACKET bloqueP RBRACKET
        '''
        p[0] = ''

    def p_bloqueP(self, p):
        '''
        bloqueP : estatuto bloqueP 
        | empty
        '''
        p[0] = ''

    def p_empty(self, p):
        '''
        empty : 
        '''
        p[0] = 'empty'

    def p_error(self, p):
        self.errores = self.errores + 1
        print(p)

    def parse(self, text):
        self.clear_state()
        result = self.parser.parse(text, lexer=self.lexer.lexer)
        return result