from State import QOp, Var, initialStateSymbols, get_error_message, Error
import math
import time

class MaquinaVirtual:
    def __init__(self, quads, func_table, cmemory):
        self.quads = quads
        self.func_table = func_table
        self.gmemory = {}
        # load in gmemory state functions
        state_sym = initialStateSymbols()
        # Iterating over both keys and values
        for key, value in state_sym.items():
            self.gmemory[value[Var.DIR_VIR]] = value[Var.VAL]
        self.lmemory = {}
        self.cmemory = cmemory
        self.args = []
        self.logs = ""
    
    def read(self, dir_vir):
        first_local = 10000
        first_const = 28000
        my_dir_vir = 0
        if isinstance(dir_vir, int):
            my_dir_vir = dir_vir
        else:
            # is an array(3) or matrix(5)
            if len(dir_vir) == 3:
                index = self.read(dir_vir[1])
                if index < 0 or index >= dir_vir[2]:
                    raise Exception(get_error_message(Error.OUT_OF_BOUNDS))
                my_dir_vir = dir_vir[0]+index
            elif len(dir_vir) == 5:
                index_1 = self.read(dir_vir[1])
                index_2 = self.read(dir_vir[3])
                if index_1 < 0 or index_1 >= dir_vir[2] or index_2 < 0 or index_2>= dir_vir[4]:
                    raise Exception(get_error_message(Error.OUT_OF_BOUNDS))
                my_dir_vir = dir_vir[0]+index_1*dir_vir[4] + index_2
                
        if my_dir_vir < first_local:
            if my_dir_vir not in self.gmemory:
                raise Exception(f"Var with {my_dir_vir} was read and is not in gmemory ")
            ret = self.gmemory[my_dir_vir]
            if ret is None:
                raise Exception(f"Var with {my_dir_vir} was referenced before assignment ")
            return ret
        elif my_dir_vir < first_const:
            if my_dir_vir not in self.lmemory:
                raise Exception(f"Var with {my_dir_vir} was read and is not in lmemory ")
            ret = self.lmemory[my_dir_vir]
            if ret is None:
                raise Exception(f"Var with {my_dir_vir} was referenced before assignment  ")
            return ret
        else:
            if my_dir_vir not in self.cmemory:
                raise Exception(f"Var with {my_dir_vir} was read and is not in cmemory ")
            ret = self.cmemory[my_dir_vir]
            if ret is None:
                raise Exception(f"Var with {my_dir_vir} was referenced before assignment ")
            return ret
    
    def write(self, dir_vir, val = None):
        first_local = 10000
        first_const = 28000
        if dir_vir < first_local:
           self.gmemory[dir_vir] = val
        elif dir_vir < first_const:
            self.lmemory[dir_vir] = val
        
    def execute(self):
        # get the start time
        st = time.time()
        stack = []
        pc = 0  # program counter
        while pc < len(self.quads):
            q = self.quads[pc]
            op = q[0]
            #print(pc)
           # switch statement using QOp enumeration
            if op == QOp.EQUAL:
                self.write(q[3], None if q[1] is None else self.read(q[1]))
            elif op == QOp.EQUALP:
                self.write(q[3], self.read(self.read(q[1])))
            elif op == QOp.SET_ARRAY:
                for i, el in enumerate(q[1]):
                    if isinstance(el, list):
                        for j, e in enumerate(el):
                            self.write(q[3]+i*len(el)+j, e)
                    else:
                        self.write(q[3]+i, el)
            elif op == QOp.PLUS:
                self.write(q[3], self.read(q[1]) + self.read(q[2]))
            elif op == QOp.MINUS:
                self.write(q[3], self.read(q[1]) - self.read(q[2]))
            elif op == QOp.TIMES:
                self.write(q[3], self.read(q[1])*self.read(q[2]))
            elif op == QOp.DIVIDE:
                self.write(q[3], self.read(q[1]) / self.read(q[2]))
            elif op == QOp.LCOMP:
                self.write(q[3], self.read(q[1]) < self.read(q[2]))
            elif op == QOp.RCOMP:
                self.write(q[3], self.read(q[1]) > self.read(q[2]))
            elif op == QOp.LCOMP_EQUAL:
                self.write(q[3], self.read(q[1]) <= self.read(q[2]))
            elif op == QOp.RCOMP_EQUAL:
                self.write(q[3], self.read(q[1]) >= self.read(q[2]))
            elif op == QOp.EQUAL_EQUAL:
                self.write(q[3], self.read(q[1]) == self.read(q[2]))
            elif op == QOp.EXC_EQUAL:
                self.write(q[3], self.read(q[1]) != self.read(q[2]))
            elif op == QOp.AND:
                self.write(q[3], self.read(q[1]) and self.read(q[2]))
            elif op == QOp.OR:
                self.write(q[3], self.read(q[1]) or self.read(q[2]))
            elif op == QOp.GOTO:
                pc = q[1]
                continue
            elif op == QOp.GOTOF:
                if self.read(q[1]) is False:
                    pc = q[2]
                    continue
            elif op == QOp.POS:
                self.write(0, self.read(q[1])) # GET_POS_X
                self.write(1, self.read(q[2])) # GET_POS_Y
            elif op == QOp.BG:
                self.write(3, self.read(q[1]))
            elif op == QOp.COLOR:
                self.write(4, self.read(q[1]))
            elif op == QOp.PENDOWN:
                self.write(5, True)
                self.write(6, False)
            elif op == QOp.PENUP:
                self.write(5, False)
                self.write(6, True)
            elif op == QOp.WIDTH:
                self.write(7, self.read(q[1]))
            elif op == QOp.CIRCLE:
                # TODO DRAW xd
                radius = self.read(q[1])
            elif op == QOp.GO:
                # TODO draw
                # current position
                x = self.read(0)
                y = self.read(1)

                # direction in degrees, 0 is north, 90 is east
                direction = self.read(8)

                # distance to move forward
                n = self.read(q[1])

                # calculate new position
                angle = math.radians(90 - direction)  # convert to radians and adjust for starting direction
                dx = n * math.cos(angle)
                dy = n * math.sin(angle)
                self.write(0, x + dx)
                self.write(1, y + dy)
            elif op == QOp.RIGHT:
                self.write(8, self.read(8) + self.read(q[1]))
            elif op == QOp.LEFT:
                self.write(8, self.read(8) - self.read(q[1]))
            elif op == QOp.ORIENTATION:
                self.write(8, self.read(q[1]))
            elif op == QOp.PRINT:
                self.logs+=(str(self.read(q[1])))
                if q[3] :
                    self.logs+= '\n'
                else :
                    self.logs+= " "
            elif op == QOp.ERA:
                result = None
            elif op == QOp.GOSUB:
                stack.append((pc, self.lmemory, q[1]))
                self.lmemory = {}
                fun_symbol = self.func_table.get_symbol(q[1])
                # fill l memory with args
                for idx, arg in enumerate(fun_symbol[Var.ARGS]):
                    self.write(arg[Var.DIR_VIR], self.read(self.args[-1][idx]))
                pc = fun_symbol[Var.QUAD]
                continue
            elif op == QOp.PARAM:
                if q[2] == 'param1':
                    self.args.append([q[1]])
                else:
                    self.args[-1].append(q[1])
            elif op == QOp.ENDFUNC:
                top = stack.pop()
                pc = top[0]
                self.lmemory = top[1]
            elif op == QOp.RETURN:
                fun_id = stack[-1][2]
                dir_vir_fun = self.func_table.get_symbol(fun_id)[Var.DIR_VIR]
                self.write(dir_vir_fun, self.read(q[1]))
            elif op == QOp.END:
                # get the end time
                et = time.time()
                elapsed_time = et - st
                self.logs+=f'Execution time: {elapsed_time} seconds'
            pc += 1  # move to the next quad
        return self.logs
