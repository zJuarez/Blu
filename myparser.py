from ply.lex import lex
from ply.yacc import yacc
from lex import MyLexer
from SymbolTable import SymbolTable
from SemanticCube import SemanticCube
from Memoria import Memoria, Section
from MaquinaVirtual import MaquinaVirtual
from State import *

# clase del parser
# necesita el lexer 
# su funcion principal es parse que devuelve 
# una lista de quads, tabla de funciones y la
# memoria constante
# tambien puede lanzar errores de sintaxis en compilacion
class MyParser:
    def __init__(self, width = 800 , height = 700, canvas = None):
        self.lexer = MyLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc(module=self)
        self.width = width
        self.height = height
        self.canvas = canvas
        self.state = initialStateSymbols(width, height)
    
    # reiniciar estructuras cada que cambia el codigo a parsear
    def clear_state(self):
        # tabla de variables
        self.curr_symbol_table = SymbolTable()
        # tabla de funciones
        self.func_table = SymbolTable()
        # cubo semantico
        self.Cube = SemanticCube()
        # memoria de compilacion
        self.memoria = Memoria()
        # añadir valores inicales del width, color, pos, etc.
        for key,value in self.state.items():
            self.curr_symbol_table.add_symbol(key, value)
        # estructuras para algoritmos
        self.PilaO = []
        self.POper = []
        self.Quad = []
        self.PTypes = []
        self.PArgsCont = []
        self.PIdLlamar = []
        self.PSaltosFor = []
        self.PSaltosFunc = []
        self.PGoto = []
        self.PGotoF = []
        self.PTiposDec = []
        self.FuncionID = ""
    
    # using stacks and creating quads
    def handle_expresion_type(self):
        if self.PilaO and self.PTypes and self.POper:   
            # pop operandos
            right_operand= self.PilaO.pop() 
            left_operand= self.PilaO.pop() 
            # pop tipos
            right_Type= self.PTypes.pop()
            left_Type= self.PTypes.pop()
            # pop operator
            operator= self.POper.pop()
            # get the result type according to semnatic cube
            res_type = self.Cube.get_type(left_Type, operator, right_Type)
            op = {
                'operator' : operator,
                'left' :  str(left_Type.value),
                'right' :  str(right_Type.value)
            }
            if res_type is None :
                self.p_error(get_error_message(Error.TYPE_MISMATCH, type_mism=op))
            else:
                temp_var = self.memoria.add(Section.TEMP, res_type)
                # create and push the quad
                quad = (get_quad_operation_from_operator(operator), left_operand, right_operand, temp_var)
                self.Quad.append(quad)
                self.PilaO.append(temp_var) 
                self.PTypes.append(res_type)
    
    # dado el objeto que devuelve la funcion p_acte regresar mas info
    def get_acte_info(self, acte):
        res = {}
        if(isinstance(acte, list)):
            if(acte and isinstance(acte[0], list)):
                tipo = acte[0][0][1]
                val=[[t[0] for t in sublist] for sublist in acte] # matrix
                kind = Kind.MATRIX
                dim1 = len(val)
                dim2 = len(val[0])
                res = {Var.VAL: val, Var.KIND : kind, Var.TIPO : tipo, Var.DIM1: dim1, Var.DIM2: dim2}
            elif acte and not isinstance(acte[0], list):
                tipo = acte[0][1]
                val = [t[0] for t in acte]  #array
                kind = Kind.ARRAY
                dim1 = len(val)
                res = {Var.VAL: val, Var.KIND : kind, Var.TIPO : tipo, Var.DIM1: dim1}
        return res
    
    # gramatica principal
    def p_blu(self,p):
        '''
        blu : codigo
        '''
        # end
        self.Quad.append((QOp.END, -1,-1,-1 ))
        p[0]=p[1]

    # puede tener funciones o estatutos
    def p_codigo(self, p):
        '''
        codigo : funcion codigoP
        | estatuto codigoP
        '''
        p[0] = 'CODIGO'
    
    def p_codigoP(self, p):
        '''
        codigoP : codigo
        | empty
        '''
        p[0] = () if p[1] == 'empty' else p[1]
    
    # gramatica de funcion
    def p_funcion(self, p):
        '''
        funcion : FUNCTION tipoFuncion idFun args bloquefun
        '''
        # 2 crear end func
        self.Quad.append((QOp.ENDFUNC, -1,-1,-1))
        # 2.1 rellenar goto de func
        if self.PSaltosFunc:
            self.Quad[self.PSaltosFunc.pop()]+= (len(self.Quad),)
        else:
            self.p_error(get_error_message(Error.INTERNAL_STACKS), msg = "PSaltosFun en p_funcion esta vacia")
        
        vars_used = self.memoria.end_mod()
        symbol = self.func_table.get_symbol(self.FuncionID)
        self.func_table.add_symbol(self.FuncionID, symbol | {Var.ERA : vars_used})
        p[0] = self.FuncionID
        self.FuncionID = '' # to know we are not longer in a function, aka global section

    def p_idFun(self, p):
        '''
        idFun : ID
        '''
        self.FuncionID = p[1]

    def p_tipoFuncion(self, p):
        '''
        tipoFuncion :  tipo 
        | VOID
        '''
        # 1 almacenar el tipo de la funcion
        if isinstance(p[1],str):
            self.PTiposDec.append(Tipo.VOID)
        # 1 crear goto
        self.Quad.append((QOp.GOTO,))
        # 1.1 push en psaltosfunc
        self.PSaltosFunc.append(len(self.Quad)-1)

    def p_args(self, p):
        '''
        args : LPAREN argsS RPAREN
        '''
        # traer el id de la funcion que acabamos de guardar
        id = self.FuncionID
        # traer el tipo de la funcion que acabamos de guardar
        tipo = self.PTiposDec[-1]
        # crear los atributos de la funcion con sus args y su tipo funcion
        function_attrs = {Var.ID : id, Var.TIPO : tipo, Var.ARGS : p[2], Var.KIND : Kind.FUNCTION, Var.QUAD : len(self.Quad)}
        # guardar en memoria global si no es void
        glo = {Var.DIR_VIR : self.memoria.add(Section.GLOBAL, tipo)} if tipo != Tipo.VOID else {}

        function_attrs|=glo

        # añadir a la tabla de simbolos actual para que pueda ser usada despues
        self.curr_symbol_table.add_symbol(id, function_attrs)
        # añadir a la tabla de funciones NEW
        self.func_table.add_symbol(id, function_attrs)

        # crear nueva tabla para el bloque de funcion con padre la tabla actual
        self.curr_symbol_table = SymbolTable(parent=self.curr_symbol_table)
        # los args deben de vivir dentro de este bloque -> añadir
        for symbol in p[2]:
            self.curr_symbol_table.add_symbol(symbol[Var.ID], symbol)
        # devolver args si acaso sirve
        p[0] = p[2]

    def p_argsS(self, p):
        '''
        argsS : argsP 
        | empty
        '''
        p[0] = [] if p[1] == 'empty' else p[1]

    def p_argsP(self, p):
        '''
        argsP : arg argsPP
        '''
        args = p[1] + p[2]
        seen_keys = set()
        duplicated_keys = set()
        # ver si hay variables repetidas
        for dictionary in args:
                if dictionary[Var.ID] in seen_keys:
                    duplicated_keys.add(dictionary[Var.ID])
                else:
                    seen_keys.add(dictionary[Var.ID])

        if len(duplicated_keys) > 0:
            self.p_error(get_error_message(Error.DUPLICATED_ARGS))
        
        p[0] = p[1] + p[2]

    def p_argsPP(self, p):
        '''
        argsPP : COMMA arg argsPP
        | empty
        '''
        p[0] = [] if p[1] == 'empty' else p[2] + p[3]

    def p_arg(self, p):
        '''
        arg : tipo ID 
        '''
        self.PTiposDec.pop()
        # va en la memoria local el arg
        var = {Var.ID : p[2], Var.TIPO : p[1], Var.KIND : Kind.SINGLE, Var.DIR_VIR : self.memoria.add(Section.LOCAL, p[1])}
        p[0] = [var]

    def p_bloquefun(self, p):
        '''
        bloquefun : LBRACKET bloquefunP returnX RBRACKET
        '''
        # destroy block, regresar a tabla de variables anterior
        self.curr_symbol_table = self.curr_symbol_table.get_parent() 
        p[0] = ''
    
    def p_returnX(self,p):
        '''
        returnX : RETURN expresion
        | empty
        '''
        if not self.PTiposDec:
            self.p_error(get_error_message(Error.INTERNAL_STACKS, msg= "returnX ptiposdec"))

        if p[1] == "empty" and self.PTiposDec[-1] != Tipo.VOID:
            # DOT HAVE RETURN
            self.p_error(get_error_message(Error.FUNCTION_MUST_HAVE_RETURN, var=self.FuncionID))

        if p[1] != "empty" and self.PTiposDec[-1] != Tipo.VOID:
            if not self.PilaO or not self.PTypes:
                self.p_error(get_error_message(Error.INTERNAL_STACKS, msg= "returnX pilao o ptypes"))
            type_of_return = self.PTypes.pop()
            var_to_return = self.PilaO.pop()
            type_of_fun = self.PTiposDec.pop()
            # type mismatch error en el return
            if type_of_fun != type_of_return:
                self.p_error(get_error_message(Error.FUNTION_RETURN_TYPE_MISMATCH, ret_type_mism={"var" : self.FuncionID, "type" : type_of_fun.value, "ret_type" : type_of_return.value}))
            # meter el quad de return
            self.Quad.append((QOp.RETURN, var_to_return, -1, -1))

    def p_bloquefunP(self, p):
        '''
        bloquefunP : estatuto bloquefunP 
        | empty
        '''
        p[0] = ''

    # gramatica de un estatuto
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
    
    # gramatica de una condicion
    def p_condicion(self, p):
        '''
        condicion : IF LPAREN expresion RPAREN checkExp bloqueif condicionElse
        '''
        # punto 4
        # Al final de un acabaIf o acabaElseIf
        if p[7] != "acaboElse":
             # GOTOF pendiente
            if self.PGotoF :
                # 1 pop pgotof
                # 2 rellenar gotof con cont
                self.Quad[self.PGotoF.pop()] +=  (len(self.Quad),)
            else :
                # weird mistake. should have pending gotof if not ending on else
                self.p_error(get_error_message(Error.INTERNAL_STACKS))
        p[0] = ''
    
    # ayuda para checar la expresion del if
    def p_checkExp(self,p):
        '''
        checkExp : empty
        '''
         # verificar que la expresion que acabamos de pasar es booleana
        if self.PTypes and self.PTypes.pop() != Tipo.BOOL:
            self.p_error(get_error_message(Error.IF_EXPRESSION_MUST_BE_BOOL))
        # punto 1
        # if R paren
        if self.PilaO : 
            # quad with exp
            # 1 crear gotof
            self.Quad.append((QOp.GOTOF, self.PilaO.pop()))
            # 2 guardar cont -1 en PGotoF
            self.PGotoF.append(len(self.Quad) -1)
        else :
            # some weird mistake. should have an bool exp on PilaO
            self.p_error(get_error_message(Error.INTERNAL_STACKS))

        p[0] = ''

    # gramatica de un else
    def p_condicionElse(self, p):
        '''
        condicionElse : myElse condicionElseP 
        | empty
        '''
        # acaboIf, acaboElse, acaboElseIf

        p[0] = "acaboIf" if len(p) < 3 else p[2]

    def p_myElse(self,p):
        '''
        myElse : ELSE 
        '''
        # punto 5
        # ELSE 
        # 1 hacer goto
        self.Quad.append((QOp.GOTO,))
        # 2 push Pgoto cont -1
        self.PGoto.append(len(self.Quad) - 1)
        # 3 pop Pgotof
        # 4 rellenar gotof con cont
        if self.PGotoF:
            self.Quad[self.PGotoF.pop()] +=  (len(self.Quad),)
        else:
            # some weird mistake. should have a gotof waiting to be filled
            self.p_error(get_error_message(Error.INTERNAL_STACKS))

        p[0] = p[1]

    def p_condicionElseP(self, p):
        '''
        condicionElseP : IF LPAREN expresion RPAREN checkExp bloqueElse condicionElse
        | bloqueElse
        '''
        # acaboIf, acaboElse, acaboElseIf
        if (len(p) < 3):
            p[0] = "acaboElse"
        else:
            p[0] = "acaboElseIf" if p[7] == "acaboIf" else p[7]

    def p_bloqueif(self, p):
        '''
        bloqueif : lbracketif bloqueP rbracketif
        '''
        p[0] = ''
    
    def p_bloqueElse(self, p):
        '''
        bloqueElse : lbracketif bloqueP rbracketelse
        '''
        p[0] = ''
    
    def p_rbracketelse(self, p):
        '''
        rbracketelse : rbracketif
        '''
        # punto 6
        # rbracket de un else o else if
        # 1 pop pgoto y rellenar con cont
        if self.PGoto:
            self.Quad[self.PGoto.pop()] +=  (len(self.Quad),)
        else:
            # some weird mistake. should have a goto waiting to be filled
            self.p_error(get_error_message(Error.INTERNAL_STACKS))
        
        p[0] = p[1]

    def p_bloqueifP(self, p):
        '''
        bloqueifP : estatuto bloqueifP 
        | empty
        '''
        p[0] = ''

        # crear nuevo bloque de variables
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
        
    # gramatica de los ciclos
    def p_ciclo(self, p):
        '''
        ciclo : myFor LPAREN cicloCont RPAREN bloqueCiclo
        | WHILE LPAREN whileExp RPAREN bloqueCiclo
        '''
        # una vez se acabo, meter los quads de asign
        asigQuads = p[3]
        self.Quad = self.Quad + asigQuads

        if len(self.PSaltosFor) < 2 :
            self.p_error(get_error_message(Error.INTERNAL_STACKS))

        gotof = self.PSaltosFor.pop()
        migaja = self.PSaltosFor.pop()

        # crear goto a la migaja de pan para evaluar exp tra vez
        self.Quad.append((QOp.GOTO, migaja))

        # al final del ciclo tienes que rellenar gotof al proximo quad a generar
        self.Quad[gotof]+=(len(self.Quad),)
        p[0] = ''
    
    def p_whileExp(self,p):
        '''
        whileExp : forExp
        '''
        # start new block
        self.curr_symbol_table = SymbolTable(parent=self.curr_symbol_table)
        p[0] = []

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

    def p_myFor(self, p):
        '''
        myFor : FOR
        '''
        # start new block
        self.curr_symbol_table = SymbolTable(parent=self.curr_symbol_table)
        p[0] = ''
    
    # los distintos tipos de for que se aceptan por la gramatica
    def p_cicloCont(self, p):
        '''
        cicloCont : intExpresion
        | ID COMMA intExpresion COMMA intExpresion
        | decSimple COMMA forExp COMMA asignacionS
        | ID IN cicloArray
        '''
        asigQuads = []
        # loop X times
        if len(p) == 2:
            invisible_var = self.memoria.add(Section.TEMP, Tipo.INT)
            self.Quad.append((QOp.EQUAL, self.memoria.add(Section.CONST, Tipo.INT, 1), -1, invisible_var))
            # dejar migaja de pan para volver despues a asignar y evaluar
            self.PSaltosFor.append(len(self.Quad))

            temp_var_suma = self.memoria.add(Section.TEMP, Tipo.INT)

            # Guardar los quads de asig
            asigQuads.append((QOp.PLUS, invisible_var, self.memoria.add(Section.CONST, Tipo.INT, 1), temp_var_suma))
            asigQuads.append((QOp.EQUAL, temp_var_suma, '', invisible_var))

            temp_var_bool = self.memoria.add(Section.TEMP, Tipo.INT)

            # generar quad de expresion
            sup_limit = p[1]
            self.Quad.append((QOp.LCOMP_EQUAL, invisible_var, sup_limit, temp_var_bool))

            # generar gotof, luego rellenamos
            self.Quad.append((QOp.GOTOF, temp_var_bool))
            # pushear gotof que despues se rellenara con el final del for
            self.PSaltosFor.append(len(self.Quad) - 1)

        # loop from [x,y] usig id
        # p[1] is a string = id
        if len(p) == 6 and not isinstance(p[1], dict):
            id = p[1]
            id_dir = self.memoria.add(Section.LOCAL, Tipo.INT)
            self.Quad.append((QOp.EQUAL, p[3], -1, id_dir))
            symbol = {id : {Var.ID: id, Var.TIPO : Tipo.INT, Var.KIND : Kind.SINGLE, Var.DIR_VIR : id_dir}}
            # adding id as cont in block
            self.curr_symbol_table.add_symbol_object(symbol)
            # dejar migaja de pan para volver despues de asignar a evaluar
            self.PSaltosFor.append(len(self.Quad))
            
            temp_var_suma = self.memoria.add(Section.TEMP, Tipo.INT)

            # Guardar los quads de asig
            asigQuads.append((QOp.PLUS, id_dir, self.memoria.add(Section.CONST, Tipo.INT, 1), temp_var_suma))
            asigQuads.append((QOp.EQUAL, temp_var_suma, '',id_dir))

            temp_var_bool = self.memoria.add(Section.TEMP, Tipo.BOOL)

            # generar quad de expresion
            sup_limit = p[5]
            self.Quad.append((QOp.LCOMP_EQUAL, id_dir, sup_limit, temp_var_bool))
            # generar gotof, luego rellenamos
            self.Quad.append((QOp.GOTOF, temp_var_bool))
            # pushear gotof que despues se rellenara con el final del for
            self.PSaltosFor.append(len(self.Quad) - 1)
        
        # trad loop: (dec, exp, asg)
        if len(p) == 6 and isinstance(p[1], dict):
            first_asg_quad = p[3]
            n_elem_of_asig = len(self.Quad) - first_asg_quad 
            # get the asig quads
            asigQuads = self.Quad[-n_elem_of_asig:]
            # remover quads from global stack to be pushed after for block ends
            del self.Quad[-n_elem_of_asig:]
        
        # MATRIXES ARE GETTING HARD
        # KEEP ONLY ARRAYS FOR NOW
        # looping arrays LETS ASSUME 
        if(len(p) == 4):
            # deducir que tipo de variable es id y que kind y agregarla
            # usar p[3] para deducr esto
            id = p[1]
            is_array = p[3][Var.KIND] == Kind.ARRAY
            if is_array == False:
                self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_ARRAY))

            size = 1 if is_array else p[3][Var.DIM2]
            # memory for the var who is going to iterate the iterable_var
            id_dir = self.memoria.add(Section.LOCAL, p[3][Var.TIPO]) 

            self.curr_symbol_table.add_symbol(id, {Var.ID : id, Var.TIPO : p[3][Var.TIPO], 
                                                     Var.KIND : Kind.SINGLE, Var.DIR_VIR : id_dir})
            
            # no tiene id cuando esta creando el array ahi ej ["RED", "BLUE", "GREEN"]
            iterable_id_dir = None
            if Var.ID in p[3]:
                iterable_id_dir = p[3][Var.DIR_VIR]  
            else:
                iterable_id_dir = self.memoria.add(Section.TEMP, p[3][Var.TIPO], size = p[3][Var.DIM1])
                self.Quad.append((QOp.SET_ARRAY, p[3][Var.VAL], -1, iterable_id_dir))

            # starts at iterable id address
            invisible_var = self.memoria.add(Section.TEMP, Tipo.INT)
            self.Quad.append((QOp.EQUAL, self.memoria.add(Section.CONST, Tipo.INT, iterable_id_dir), -1, invisible_var))

            exp_bool = self.memoria.add(Section.TEMP, Tipo.BOOL)
            sup_limit = self.memoria.add(Section.TEMP, Tipo.INT)
            self.Quad.append((QOp.EQUAL, self.memoria.add(Section.CONST, Tipo.INT, iterable_id_dir + p[3][Var.DIM1]),-1, sup_limit))
            # dejar migaja de pan para volver despues de asignar a evaluar
            self.PSaltosFor.append(len(self.Quad))
            # exp quad till the size of the iterable id is over
            self.Quad.append((QOp.LCOMP, invisible_var, sup_limit, exp_bool))
            # generar gotof, luego rellenamos
            self.Quad.append((QOp.GOTOF, exp_bool))
            # pushear gotof que despues se rellenara con el final del for
            self.PSaltosFor.append(len(self.Quad) - 1)
            # asign id to the ith element
            # equal to the value of the pointer instead of int
            self.Quad.append((QOp.EQUALP,invisible_var, '',id_dir))
            temp_var_suma = self.memoria.add(Section.TEMP, Tipo.INT)
             # Guardar los quads de asig 
            asigQuads.append((QOp.PLUS, invisible_var, self.memoria.add(Section.CONST, Tipo.INT, 1), temp_var_suma))
            asigQuads.append((QOp.EQUAL, temp_var_suma, '',invisible_var))
            
        p[0] = asigQuads
    
    def p_forExp(self, p):
        '''
        forExp : beforeExpJump expresion
        '''
        # exp esta en PilaO y debe de ser bool
        if self.PilaO and self.PTypes:
            if self.PTypes.pop() != Tipo.BOOL:
                self.p_error(get_error_message(Error.FOR_EXPRESSION_MUST_BE_BOOL))
            # crear GOTOF con exp
            self.Quad.append((QOp.GOTOF, self.PilaO.pop()))
            self.PSaltosFor.append(len(self.Quad)-1)
        else:
             self.p_error(get_error_message(Error.INTERNAL_STACKS))
        # nos servira mas tarde para mover los quads de asign al final
        p[0] = len(self.Quad)
    
    def p_beforeExpJump(self,p):
        '''
        beforeExpJump : empty
        '''
        # antes de EVALUAR exp guardar migaja de pan
        # dejar migaja de pan para volver DESPUES de asignar A evaluar
        self.PSaltosFor.append(len(self.Quad))
        p[0] = '' 

    # used in regular for
    def p_decSimple(self, p):
        '''
        decSimple : tipo ID EQUAL expresion
        '''
        if self.PTypes and self.PilaO:
            tipo_exp = self.PTypes.pop()
            # check type mismatch
            if p[1] != tipo_exp:
                 self.p_error(get_error_message(Error.TYPE_MISMATCH))
            val = self.PilaO.pop()
            id_dir = self.memoria.add(Section.LOCAL, p[1])
            symbol = {p[2] : {Var.ID: p[2], Var.TIPO : p[1], Var.KIND : Kind.SINGLE, Var.VAL : val, Var.DIR_VIR : id_dir}}
            self.Quad.append((QOp.EQUAL, val, -1, id_dir))
            # adding dec simple to table
            self.curr_symbol_table.add_symbol_object(symbol)
            p[0] = symbol
        else:
            # weird mistake. should have type at the top of the expression
            self.p_error(get_error_message(Error.INTERNAL_STACKS))
            p[0] = "error"
       
    def p_cicloArray(self, p):
        '''
        cicloArray : ID
        | acte
        '''
        #is id
        if isinstance(p[1], str):
            id = p[1]
            info = self.curr_symbol_table.get_symbol(id)
            if info == None:
                self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, id))
            if info[Var.KIND] != Kind.ARRAY and info[Var.KIND] != Kind.MATRIX:
                self.p_error(get_error_message(Error.ID_IS_NOT_ITERABLE, id))
            p[0] = info
        # traer info de acte
        else:
            p[0] = self.get_acte_info(p[1])
    
    # gramatica de asignacion
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
        var_id = p[1]
        var_symbol = self.curr_symbol_table.get_symbol(var_id)
        # should be idAS checks for vars not declared
        if(var_symbol is not None):
            var_type = var_symbol[Var.TIPO]
            var_kind = var_symbol[Var.KIND]
            if var_kind != p[2]:
                self.p_error(get_error_message(Error.ASSIGNATION_WENT_WRONG, ass = {'var' : var_id, 'kind' : var_kind, 'kind_ass' : p[2]}))
            # expression type should be in the top of the stack of expressions
            if self.PTypes and self.PilaO:
                exp_type = self.PTypes.pop()
                dir_vir_of_exp = self.PilaO.pop()
                var_dir = var_symbol[Var.DIR_VIR]
                if p[2] == Kind.ARRAY:
                    if self.PTypes and self.PilaO:
                        index_dir = self.PilaO.pop()
                        index_type = self.PTypes.pop()
                        # expression inside square brackets must be int
                        if(index_type != Tipo.INT):
                            self.p_error(get_error_message(Error.EXPRESSION_INSIDE_SQUARE_BRACKETS_MUST_BE_INT))
                        var_dir = (var_dir, index_dir, var_symbol[Var.DIM1])
                    else:
                        self.p_error(get_error_message(Error.INTERNAL_STACKS))
                elif p[2] == Kind.MATRIX:
                    if len(self.PTypes) > 1 and len(self.PilaO)>1:
                        index_dir_2 = self.PilaO.pop()
                        index_type_2 = self.PTypes.pop()
                        index_dir_1 = self.PilaO.pop()
                        index_type_1 = self.PTypes.pop()
                        # expression inside square brackets must be int
                        if index_type_1 != Tipo.INT or index_type_2 != Tipo.INT:
                            self.p_error(get_error_message(Error.EXPRESSION_INSIDE_SQUARE_BRACKETS_MUST_BE_INT))
                        var_dir = (var_dir, index_dir_1, var_symbol[Var.DIM1], index_dir_2, var_symbol[Var.DIM2])
                    else:
                        self.p_error(get_error_message(Error.INTERNAL_STACKS))
                if(var_type == exp_type):
                    # same type! create quad
                    self.Quad.append((QOp.EQUAL, dir_vir_of_exp, -1,var_dir))
                elif(var_type == Tipo.INT and exp_type == Tipo.FLOAT):
                    self.Quad.append((QOp.EQUAL, dir_vir_of_exp, -1,var_dir))
                elif(var_type == Tipo.FLOAT and exp_type == Tipo.INT):
                    # Ask about casts
                    self.Quad.append((QOp.EQUAL, dir_vir_of_exp, -1,var_dir))
                else:
                    # asignation type mismatch
                    self.p_error(get_error_message(Error.TYPE_MISMATCH, type_mism={
                        "operator" : "=",
                        "left" : var_type,
                        "right" : exp_type
                    }))
            else:
                self.p_error(get_error_message(Error.EXPRESSION_WENT_WRONG))
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
        asignacionSA : lbracketArray expresion rbracketArray asignacionSM
        | empty
        '''
        p[0] = Kind.SINGLE if len(p) < 3 else p[4]

    def p_asignacionSM(self, p):
        '''
        asignacionSM : lbracketArray expresion rbracketArray 
        | empty
        '''
        p[0] = Kind.MATRIX if len(p) > 2 else Kind.ARRAY

    # gramatica de declarar
    def p_declarar(self, p):
        '''
        declarar : tipo declararSimple declararP
        '''
        self.PTiposDec.pop()
        p[0] = ('DECLARAR' , [p[2]] + p[3])
    
    # multiples declaraciones en linea
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
            var = {Var.ID : id, Var.TIPO : self.PTiposDec[-1]} | p[2]
            section = Section.GLOBAL if self.curr_symbol_table.is_declarated_in_block("GET_POS_X") else Section.LOCAL
            tipo = self.PTiposDec[-1]
            size = 1 if var[Var.KIND] == Kind.SINGLE else var[Var.DIM1] if var[Var.KIND] == Kind.ARRAY else var[Var.DIM1] * var[Var.DIM2]
            val = None if Var.VAL not in var else var[Var.VAL]
            dir_vir = self.memoria.add(section, tipo, size=size)
            self.curr_symbol_table.add_symbol(id, var | {Var.DIR_VIR : dir_vir})
            if var[Var.KIND] == Kind.SINGLE and val != None:
                self.Quad.append((QOp.EQUAL, val, -1, dir_vir))
            elif var[Var.KIND] != Kind.SINGLE and val != None:
                self.Quad.append((QOp.SET_ARRAY, val, -1, dir_vir))
            # print("añadiendo a la tabla " + str(id))
        p[0] = var
    
    def p_declararSimpleOpciones(self, p):
        '''
        declararSimpleOpciones : EQUAL expresion 
        | declararArray 
        | empty
        '''
        # esta inicializando la variable SIMPLE
        if len(p) > 2:
            # 9 guardar el valor de la variable declarada
            # el valor de la exp debe de vivir en PilaO
            if self.PilaO and self.PTypes:
                p[0] = {Var.VAL : self.PilaO.pop(), Var.KIND : Kind.SINGLE}
                l_type = self.PTiposDec[-1]
                r_type = self.PTypes.pop()
                if l_type != r_type:
                    if (l_type == Tipo.INT and r_type == Tipo.FLOAT) or (l_type == Tipo.FLOAT and r_type == Tipo.INT):
                        x = 1
                    else:
                        op = {
                                'operator' : "=",
                                'left' : str(l_type),
                                'right' :  str(r_type),
                            }
                        self.p_error(get_error_message(Error.TYPE_MISMATCH, type_mism=op))
            else:
                # mistake of stacks
                self.p_error(get_error_message(Error.INTERNAL_STACKS))
        # declaro array o no declaro nada mas
        else:
            p[0] = p[1] if(p[1] != 'empty') else {Var.KIND : Kind.SINGLE}

    # ayuda para declarar array
    def p_declararArray(self, p):
        '''
        declararArray : LSQBRACKET icteC RSQBRACKET declararArrayP
        '''
        if p[2][0] < 1:
            self.p_error(get_error_message(Error.BAD_ARRAY_DECLARATION_INDEX))
        # 4 La primera dimension del arreglo o matriz es de tamaño p[2][0]
        p[0] = {Var.DIM1: p[2][0]} | p[4]
        symbol = p[0]
        if symbol and Var.VAL in symbol:
            val = symbol[Var.VAL]
            if len(val) != symbol[Var.DIM1]:
                self.p_error(get_error_message(Error.WRONG_ARRAY_SIZE_DECLARATION_DIM1))
            if Var.DIM2 in symbol and len(val[0]) != symbol[Var.DIM2]:
                self.p_error(get_error_message(Error.WRONG_ARRAY_SIZE_DECLARATION_DIM2))

    def p_declararArrayP(self, p):
        '''
        declararArrayP : LSQBRACKET icteC RSQBRACKET declararArrayPP 
        | inicializaArray 
        | empty
        '''
        var = {}
        # esta declarando una matriz
        if(len(p) > 2):
            # 5 La segunda dimension de la matriz es de tamaño p[2]
            var|={Var.DIM2 : p[2][0]}
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
        # esta inicializando el array o mat
        if len(p) > 2:
            acte = self.get_acte_info(p[2])
            p[0] = {Var.VAL : acte[Var.VAL]}
            if(self.PTiposDec[-1] != acte[Var.TIPO]):
                self.p_error(get_error_message(Error.TYPE_MISMATCH_IN_ARRAY_DECLARATION))
        else:
            p[0] = {}
    
    def p_icteC(self,p):
        '''
        icteC : ICTE
        '''
        # crear const en memoria
        dir_vir = self.memoria.add(Section.CONST, p[1][1], p[1][0])
        p[0] = p[1] + (dir_vir,)

    def p_bcte(self, p):
        '''
        bcte : TRUE
        | FALSE
        '''
        p[0] = (p[1] == "TRUE", Tipo.BOOL)
    
    # gramatica para acte : los arrays constantes ej [1,1,2,3]
    def p_acte(self, p):
        '''
        acte : LSQBRACKET acteC
        '''
        p[0] = p[2]
    
    # solo se pueden arrays y matrices
    def p_acteC(self, p):
        '''
        acteC :  acteP RSQBRACKET
        | ascteC RSQBRACKET
        '''
        p[0] = p[1]

    def p_acteP(self, p):
        '''
        acteP : expresionSingle actePP
        '''
        if p[2] and p[1][1] != p[2][0][1]:
            # type checking
            self.p_error(get_error_message(Error.ALL_ARRAY_ELEMENTS_MUST_BE_SAME_TYPE))
        p[0] = [p[1]] + p[2]
    
    # tiene que ser un valor atomico.
    def p_expresionSingle(self,p):
        '''
        expresionSingle : expresion
        '''
        if self.PilaO and self.PTypes:
            val_dir = self.PilaO.pop()
            val_type = self.PTypes.pop()
            # tuples with 3,5,2 means single var of array, of matrix and array of values respectively
            if isinstance(val_dir, tuple):
                if len(val_dir) == 2:
                    #error since we only want single values
                    self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_ATOMIC_VALUE))
            p[0] = (val_dir, val_type)
        else:
            self.p_error(get_error_message(Error.INTERNAL_STACKS))

    def p_actePP(self, p):
        '''
        actePP : COMMA acteP 
        | empty
        '''
        p[0] = [] if len(p) == 2 else p[2]
    
    def p_ascteC(self,p):
        '''
        ascteC : ascte ascteCC
        '''
        # checar que todos los arreglos sean del mismo length
        if p[2] and p[2][0] and len(p[1]) != len(p[2][0]):
             self.p_error(get_error_message(Error.ALL_MATRIX_ARRAYS_MUST_BE_SAME_LENGTH))
        # checar que todos los arreglos sean del mismo tipo
        if p[2] and p[2][0] and p[1] and p[1][0][1] != p[2][0][0][1]:
             self.p_error(get_error_message(Error.ALL_MATRIX_ARRAYS_MUST_BE_SAME_TYPE))
        if p[2] != [[]]:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = [p[1]]
    
    def p_ascteCC(self,p):
        '''
        ascteCC : COMMA ascteC
        | empty
        '''
        p[0] = [[]] if len(p) == 2 else p[2]

    def p_ascte(self, p):
        '''
        ascte : LSQBRACKET acteP RSQBRACKET
        '''
        p[0] = p[2]
    
    # usado en los fors, checa que la expresion sea de tipo entero
    def p_intExpresion(self, p):
        '''
        intExpresion : expresion 
        '''
        if len(self.PilaO) > 0 and len(self.PTypes) > 0:
            first_type = self.PTypes.pop()
            if (first_type != Tipo.INT):
                    self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_INT_VALUE, ""))
            dir_vir = self.PilaO.pop()
            if isinstance(dir_vir, tuple) and len(dir_vir) == 2:
                 self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_INT_VALUE, ""))
            p[0] = dir_vir
        else:
            self.p_error(get_error_message(Error.INTERNAL_STACKS))
    
    # usado para POS, checa que ambas expresiones sean de tipo numerico
    def p_twoExpNum(self,p):
        '''
        twoExpNum : expresion COMMA expresion
        '''
        if len(self.PilaO) > 1 and len(self.PTypes) > 1:
            first_type = self.PTypes.pop()
            second_type = self.PTypes.pop()
            if (first_type != Tipo.INT and first_type != Tipo.FLOAT) or (second_type != Tipo.INT and second_type != Tipo.FLOAT):
                    self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_NUMERIC, ""))
            p[0] = [self.PilaO[-2], self.PilaO[-1]]
            self.PilaO.pop()
            self.PilaO.pop()
        else:
            self.p_error(get_error_message(Error.INTERNAL_STACKS))
    
    # gramatica del estado
    def p_estado(self, p):
        '''
        estado : POS twoExpNum
        | BG expresion
        | POLYGON polygonOp
        | COLOR expresion
        | PENDOWN
        | PENUP
        | WIDTH expresion
        | CIRCLE expresion COMMA  expresion COMMA expresion COMMA expresion fillOp
        | GO expresion
        | RIGHT expresion
        | LEFT expresion
        | ORIENTATION expresion
        | print
        | readP
        '''
        # cada unaa crea un quad diferente.
        if p[1] == 'POS':
            self.Quad.append((QOp.POS, p[2][0], p[2][1], -1))
        elif p[1] == 'POLYGON':
            x = 1
        elif p[1] == 'PENDOWN' or p[1] == 'PENUP':
            self.Quad.append((get_quad_operation_from_state(p[1]),))
        elif p[1] == "CIRCLE":
            if len(self.PilaO) < 4 and len(self.PTypes) < 4:
                self.p_error(get_error_message(Error.INTERNAL_STACKS))
            types = [self.PTypes.pop(), self.PTypes.pop(), self.PTypes.pop(), self.PTypes.pop()]
            for ty in types:
                if ty != Tipo.INT and ty != Tipo.FLOAT:
                    self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_NUMERIC, "Circle" ))
            y1 = self.PilaO.pop()
            x1 = self.PilaO.pop()
            y0 = self.PilaO.pop()
            x0 = self.PilaO.pop()
            self.Quad.append((QOp.CIRCLE, x0,y0,x1,y1, p[9]))
        elif p[1] != 'PRINT' and p[1] != 'READ':
            first_type = self.PTypes.pop()
            if p[1] != "BG" and p[1] != "COLOR" and first_type != Tipo.INT and first_type != Tipo.FLOAT:
                     self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_NUMERIC, p[1]))
            if (p[1] == "BG" or p[1] == "COLOR") and first_type != Tipo.STRING:
                     self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_STRING, p[1]))
            if self.PilaO:
                self.Quad.append((get_quad_operation_from_state(p[1]), self.PilaO.pop()))
            else:
                self.p_error(get_error_message(Error.INTERNAL_STACKS))
        p[0] = ''
    
    # gramatica para el read
    def p_readP(self,p):
        '''
        readP : READ expresionVarID readPP
        '''
        reads = [p[2]] + p[3]
        for read in reads:
            self.Quad.append((QOp.READ, read[0], read[1]))
        p[0] = p[1]

    def p_readPP(self,p):
        '''
        readPP : expresionVarID readPP
        | empty
        '''
        if p[1] != 'empty':
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []
    
    # crear quad de polygono
    def p_polygonOp(self,p):
        '''
        polygonOp : polygon1p fillOp
        '''
        # p[1] es array de direcciones
        self.Quad.append((QOp.POLYGON, p[1], p[2]))

    def p_polygon1p(self,p):
        '''
        polygon1p : ID 
        | acte
        '''
        #its an id
        if isinstance(p[1], str):
            id = p[1]
            info = self.curr_symbol_table.get_symbol(id)
            if info == None:
                self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, id))
            if info[Var.KIND] != Kind.ARRAY:
                self.p_error(get_error_message(Error.ID_IS_NOT_ITERABLE, id))
            if info[Var.TIPO] != Tipo.INT and info[Var.TIPO] != Tipo.FLOAT:
                self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_NUMERIC, var="Polygon points "))
            # var getting all array
            #special tuple with 2 length: ( base_dir_vir,dim1 )
            p[0] = (info[Var.DIR_VIR], info[Var.DIM1])
        else:
            acte_info = self.get_acte_info(p[1])
            if acte_info[Var.TIPO] != Tipo.INT and acte_info[Var.TIPO] != Tipo.FLOAT:
                 self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_NUMERIC, var="Polygon points "))
            p[0] = acte_info[Var.VAL] # should be array of nums
        
    # string opcional final para CIRCLE y POLYGON
    def p_fillOp(self,p):
        '''
        fillOp : COMMA expresion
        | empty
        '''
        if "empty" == p[1]:
            p[0] = "empty"
        else:
            tipo_exp = self.PTypes.pop()
            if tipo_exp != Tipo.STRING:
                self.p_error(get_error_message(Error.EXPRESSION_MUST_BE_STRING, var="Fill Color "))
            p[0] = self.PilaO.pop()

    # gramatica para PRINT
    def p_print(self, p):
        '''
        print : PRINT printN
        '''
        c = 0
        exp_num = p[2][0]
        exp = []
        while c<exp_num:
            exp.append((self.PilaO.pop(), self.PTypes.pop()))
            c+=1
        c=0
        while c<exp_num:
            self.Quad.append((QOp.PRINT,) +(exp.pop()) + (c == (exp_num-1) and p[2][1],))
            c+=1
        if p[2] == (0, True):
            self.Quad.append((QOp.PRINT,-1,-1,True))
        p[0] = 'PRINT'
    
    def p_printN(self,p):
        '''
        printN : expresion printP
        | ENDL
        '''
        p[0] = (0, True) if p[1] == "ENDL" else (1 + p[2][0], p[2][1])

    def p_printP(self, p):
        '''
        printP : COMMA expresion printP
        | ENDL
        | empty
        '''
        if p[1] == "empty":
            p[0] = (0, False)
        elif p[1] == "ENDL":
            p[0] = (0, True)
        else:
            p[0] = (1 + p[3][0], p[3][1])
    
    # gramatica para llamar funciones propias
    def p_llamar(self, p):
        '''
        llamar : idllamar llamarRest
        '''
        p[0] = ''

    def p_idllamar(self, p):
        '''
        idllamar : ID
        '''
        # function exists -> its declared before in any other higher block
        if (self.func_table.get_symbol(p[1])):
            # needed?
            # self.curr_state.add_info(Var.ID, p[1])
            # needed
            self.PIdLlamar.append(p[1])
            self.Quad.append((QOp.ERA, p[1]))
            self.PArgsCont.append(0)
        else:
            self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
        p[0] = p[1]
    
    # ayuda a llamar
    def p_llamarRest(self,p):
        '''
        llamarRest : lparenLlamar llamarP rparenLlamar 
        '''
        if not self.PArgsCont or not self.PIdLlamar:
            self.p_error(get_error_message(Error.INTERNAL_STACKS))
        
        id = self.PIdLlamar.pop()
        params_len = len(self.func_table.get_symbol(id)[Var.ARGS])

        # ver si se llamo con el numero de params correctos
        if self.PArgsCont.pop() != params_len:
            self.p_error(get_error_message(Error.FUNCTION_PARAMS_DIFF,  id, {}, params_len))
        
        # crear quad de gosub
        self.Quad.append((QOp.GOSUB, id))
        p[0] = ''
    
    def p_lparenLlamar(self,p):
        '''
        lparenLlamar : LPAREN
        '''
        # meter fondo falso!
        self.POper.append('[') 

    def p_rparenLlamar(self,p):
        '''
        rparenLlamar : RPAREN
        '''
        # quitar fondo falso!
        self.POper.pop()

    def p_llamarP(self, p):
        '''
        llamarP : expresion postExpLlamar llamarPP
        | empty 
        '''
        if not self.PIdLlamar:
            self.p_error(get_error_message(Error.INTERNAL_STACKS))
        id = self.PIdLlamar[-1]
        if(len(p)==2):
            params_len = len(self.func_table.get_symbol(id)[Var.ARGS])
            if( params_len > 0):
                self.p_error(get_error_message(Error.FUNCTION_PARAMS_DIFF,  id, {}, params_len))
        p[0] = ''

    def p_llamarPP(self, p):
        '''
        llamarPP : COMMA expresion postExpLlamar llamarPP
        | empty 
        '''
        p[0] = ''
    
    # ir sumando los argumentos y verificar los tipos de cada uno
    def p_postExpLlamar(self,p):
        ''' 
        postExpLlamar : empty
        '''
        if not self.PArgsCont or not self.PIdLlamar or not self.PTypes or not self.PilaO:
            self.p_error(get_error_message(Error.INTERNAL_STACKS))
        
        id = self.PIdLlamar[-1]
        params_len = len(self.func_table.get_symbol(id)[Var.ARGS])

        if self.PArgsCont[-1] == params_len:
            self.p_error(get_error_message(Error.FUNCTION_PARAMS_DIFF,  id, {}, params_len))

        tipo_param = self.func_table.get_symbol(id)[Var.ARGS][self.PArgsCont[-1]][Var.TIPO]

        tipo_arg = self.PTypes.pop()
        if tipo_arg != tipo_param:
            fun_type_mism = {
                "id": id,
                "param" : self.PArgsCont[-1] + 1,
                "param_type": tipo_param,
                "arg_type" : tipo_arg
            }
            self.p_error(get_error_message(Error.FUNCTION_PARAM_TYPE_MISMATCH, fun_type_mism=fun_type_mism))

        self.PArgsCont[-1] = self.PArgsCont[-1] + 1
        self.Quad.append((QOp.PARAM, self.PilaO.pop(), "param" + str(self.PArgsCont[-1])))
        p[0] = p[1]
    
    # gramatica de los tipos
    def p_tipo(self, p):
        '''
        tipo : INT 
        | FLOAT
        | STRING
        | CHAR
        | BOOL
        '''
        # 1 almacenar el tipo de la variable
        tipo = get_tipo(p[1])
        self.PTiposDec.append(tipo)
        p[0] = tipo
    
    # la super expresion
    def p_expresion(self, p):
        '''
        expresion : expresionA expresionP
        '''
        if self.POper and (self.POper[-1] == '||'):
           self.handle_expresion_type()
        p[0] = ''

    def p_expresionP(self, p):
        '''
        expresionP : orOp expresionA expresionP 
        | empty
        '''
        p[0] = ''
    
    def p_orOp(self,p):
        '''
        orOp : BAR BAR
        '''
        if self.POper and (self.POper[-1] == '||'):
           self.handle_expresion_type()
        self.POper.append('||')
        p[0] = p[1]

    def p_expresionA(self, p):
        '''
        expresionA : expresionB expresionAP
        '''
        if self.POper and (self.POper[-1] == '&&'):
           self.handle_expresion_type()
        p[0] = ''

    def p_expresionAP(self, p):
        '''
        expresionAP : andOp expresionB expresionAP
        | empty
        '''
        p[0] = ''
    
    def p_andOp(self, p):
        '''
        andOp : AMPERSON AMPERSON
        '''
        if self.POper and (self.POper[-1] == '&&'):
           self.handle_expresion_type()
        self.POper.append('&&')
        p[0] = p[1]

    def p_expresionB(self, p):
        '''
        expresionB : exp expresionBP
        '''
        p[0] = ''
    
    def p_expresionBP(self, p):
        '''
        expresionBP : relOp exp
        | empty
        '''
        if(len(p)> 2):
            self.POper.append(p[1])
            self.handle_expresion_type()
        p[0] = ''

    def p_relOp(self, p):
        '''
        relOp : LCOMP
        | RCOMP
        | LCOMP EQUAL
        | RCOMP EQUAL
        | EQUAL EQUAL
        | EXC EQUAL
        '''
        op = p[1]
        if(len(p) == 3):
            op = p[1] + p[2]
        p[0] = op

    def p_exp(self, p):
        '''
        exp : termino expP 
        '''
        p[0] = ''

    def p_expP(self, p):
        '''
        expP : terminoOp exp 
        | empty
        '''
        p[0] = ''
    
    def p_terminoOp(self,p):
        '''
        terminoOp : PLUS 
        | MINUS 
        '''
        self.POper.append(p[1])
        p[0] = p[1]

    def p_termino(self, p):
        '''
        termino : factor terminoP 
        '''
        if self.POper and (self.POper[-1] == '+' or self.POper[-1] == '-'):
           self.handle_expresion_type()
        p[0] = ''

    def p_terminoP(self, p):
        '''
        terminoP : factorOp termino
        | empty
        '''
        p[0] = ''
    
    def p_factorOp(self,p):
        '''
        factorOp : TIMES 
        | DIVIDE
        '''
        self.POper.append(p[1])
        p[0] = p[1]
    
    def p_factor(self, p):
        '''
        factor : mod factorP
        '''
        if self.POper and (self.POper[-1] == '*' or self.POper[-1] == '/'):
            self.handle_expresion_type()
        p[0] = ''
    
    def p_factorP(self, p):
        '''
        factorP : percentP mod
        | empty
        '''
        p[0] = ''
    
    def p_percentP(self,p):
        '''
        percentP : PERCENT
        '''
        self.POper.append(p[1])
    
    # lo importante de las expresiones 
    def p_mod(self, p):
        '''
        mod : cteE
        | var 
        | getEstado
        | lparenExp expresion rparenExp
        '''
        if self.POper and (self.POper[-1] == '%'):
            self.handle_expresion_type()
        p[0] = ''

    def p_lparenExp (self, p):
        '''
        lparenExp : LPAREN
        '''
        self.POper.append("(")

    def p_rparenExp (self, p):
        '''
        rparenExp : RPAREN
        '''
        self.POper.pop()

    def p_cteE(self, p):
        '''
        cteE : ICTE 
        | FCTE
        | SCTE
        | CCTE
        | bcte
        '''
        # crear const en memoria
        dir = self.memoria.add(Section.CONST, p[1][1], p[1][0])
                # forma (Var.Val, Var.Tipo)
        # append el id de la expresion a la pila 
        self.PilaO.append(dir)
        # append el tipo
        self.PTypes.append(p[1][1])
        p[0] = p[1] 
    
    # es un id de un valor atomico
    # y que puede venir de una variable simple ej x
    # de un arreglo ej x[0]
    # o de una matriz ej x[0][0]
    # se usa en read y en expresiones
    # porque no tengo operaciones con arreglos ni mat
    def p_expresionVarID(self,p):
        '''
        expresionVarID : ID varP
        '''
        symbol = self.curr_symbol_table.get_symbol(p[1])
        dir_vir = 0
        if (symbol is None):
            self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
        if symbol[Var.KIND] == Kind.SINGLE:
            # lo usaste como array [] error
            if p[2] != Kind.SINGLE:
                self.p_error(get_error_message(Error.ID_IS_NOT_ITERABLE, var = p[1]))
            # add single var dir to PilaO
            # self.PilaO.append(symbol[Var.DIR_VIR])
            dir_vir = symbol[Var.DIR_VIR]
        # is array o matrix
        else:
            # using arrays and matrix as they are not.
            if p[2] == Kind.SINGLE or (p[2] == Kind.ARRAY and symbol[Var.KIND] == Kind.MATRIX) or (p[2] == Kind.MATRIX and symbol[Var.KIND] == Kind.ARRAY):
                self.p_error(get_error_message(Error.ID_NEEDS_SQUARE_BRACKETS, var = p[1], type=symbol[Var.KIND].name))
            if p[2] == Kind.ARRAY:
                if self.PilaO and self.PTypes:
                    index_type = self.PTypes.pop()
                    index_dir_vir = self.PilaO.pop()
                    if index_type != Tipo.INT:
                        self.p_error(get_error_message(Error.EXPRESSION_INSIDE_SQUARE_BRACKETS_MUST_BE_INT))
                    dir_vir_array_start= symbol[Var.DIR_VIR]
                    dir_vir_array_indexed = (dir_vir_array_start, index_dir_vir, symbol[Var.DIM1])
                    # self.PilaO.append(dir_vir_array_indexed)
                    dir_vir = dir_vir_array_indexed
                else:
                    self.p_error(get_error_message(Error.INTERNAL_STACKS))
            else:
                if len(self.PilaO)>1 and len(self.PTypes)>1:
                    index_type_dim2 = self.PTypes.pop()
                    index_dir_vir_dim2 = self.PilaO.pop()
                    index_type_dim1 = self.PTypes.pop()
                    index_dir_vir_dim1 = self.PilaO.pop()
                    if index_type_dim2 != Tipo.INT or index_type_dim1 != Tipo.INT:
                        self.p_error(get_error_message(Error.EXPRESSION_INSIDE_SQUARE_BRACKETS_MUST_BE_INT))
                    dir_vir_array_start= symbol[Var.DIR_VIR]
                    dir_vir_array_indexed = (dir_vir_array_start, index_dir_vir_dim1, symbol[Var.DIM1], index_dir_vir_dim2, symbol[Var.DIM2])
                    # self.PilaO.append(dir_vir_array_indexed)
                    dir_vir = dir_vir_array_indexed
                else:
                    self.p_error(get_error_message(Error.INTERNAL_STACKS))
        p[0] = (dir_vir, symbol[Var.TIPO])
    
    # las variables establecidas por el usuario
    # se usa en expresion
    # puede ser una variable o funcion
    def p_var(self, p):
        '''
        var : expresionVarID
        | idllamar llamarRest
        '''
        # llamar rest
        if isinstance(p[1], str):
            # 1 si el id no existe error
            symbol = self.curr_symbol_table.get_symbol(p[1])
            if (symbol is None):
                self.p_error(get_error_message(Error.VARIABLE_NOT_DECLARED, p[1]))
            elif symbol[Var.TIPO] == Tipo.VOID:
                self.p_error(get_error_message(Error.VOID_IN_EXPRESION, var = p[1]))
            elif symbol[Var.KIND] == Kind.FUNCTION:
                # global to PilaO
                # todo
                temp_res = self.memoria.add(Section.TEMP, symbol[Var.TIPO])
                self.Quad.append((QOp.EQUAL, symbol[Var.DIR_VIR] ,-1,temp_res))
                self.PilaO.append(temp_res)
                self.PTypes.append(symbol[Var.TIPO])
        else:
            #expresionVarID
            self.PilaO.append(p[1][0])
            self.PTypes.append(p[1][1])
        # devolver algo interesante
        p[0] = ''
    
    # accesar variables del estado y random
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
        | CANVAS_WIDTH
        | CANVAS_HEIGHT
        | RANDOM randomOp
        '''
        if p[1] == "RANDOM":
            tipo = Tipo.FLOAT if p[2] == "empty" else Tipo.INT
            random_dir_vir = self.memoria.add(Section.TEMP, tipo)
            self.Quad.append((QOp.RANDOM, p[2], random_dir_vir))
            self.PilaO.append(random_dir_vir)
            self.PTypes.append(tipo)
        else:
            # append el id de la expresion a la pila 
            self.PilaO.append(self.state[p[1]][Var.DIR_VIR])
            # append el tipo
            self.PTypes.append(self.state[p[1]][Var.TIPO])
        p[0] = p[1]

    def p_randomOp(self,p):
        '''
        randomOp : twoExpNum
        | empty
        '''
        p[0] = p[1]
    
    # ayudan a expresionVarID
    def p_varP(self, p):
        '''
        varP : varPArray
        | empty
        '''
        p[0] = Kind.SINGLE if p[1] == "empty" else p[1]

    def p_varPArray(self, p):
        '''
        varPArray : lbracketArray expresion rbracketArray varPArrayP
        '''
        p[0] = p[4]
    
    def p_lbracketArray(self,p):
        '''
        lbracketArray : LSQBRACKET
        '''
        self.POper.append("[")

    def p_rbracketArray(self,p):
        '''
        rbracketArray : RSQBRACKET
        '''
        self.POper.pop()

    def p_varPArrayP(self, p):
        '''
        varPArrayP : lbracketArray expresion rbracketArray 
        | empty
        '''
        p[0] = Kind.MATRIX if len(p) > 3 else Kind.ARRAY
    
    # bloque normal que contiene estatutos y esta entre llaves
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
    # tirar excepcion cuando haya un error en compilacion
    def p_error(self, p):
        raise Exception(p)
    # funcion principal que recibe codigo
    # y lo devuelve parseado en una lista de quads de operacion
    # tabla de funciones y memoria constante
    # tambien puede lanzar errores
    def parse(self, text):
        # reinicia las estructuras ed datos
        self.clear_state()
        try: 
            self.parser.parse(text, lexer=self.lexer.lexer)
            debug = True
            # imprimir resultados de compilacion
            if(debug):
                   print("FUNC TABLE : ")
                   self.func_table.print()
                   print()
                   print("C MEMORY : ")
                   print(self.memoria.get_const_map())
                   print()
                   print("QUADS : ")
                   for idx, v in enumerate(self.Quad):
                    print(str(idx) + "." + str(v))
                   print()
                   print("RESULT: ")
            # devolver resultados de compilacion
            return (self.Quad, self.func_table, self.memoria.get_const_map())
        except Exception as e:
            return ("ERROR", e)

        