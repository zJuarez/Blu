from tkinter import Tk
import tkinter
from State import QOp, Var, initialStateSymbols, get_error_message, Error, Tipo
import math
import time
import random
import re

class Memoria:
    def __init__(self, parent = None, fun_id = "_main"):
        self.parent = parent
        self.symbols = {}
        self.args = []
        self.fun_id = fun_id

    def get(self, dir_vir):
        return None if dir_vir not in self.symbols else self.symbols[dir_vir]
    
    def set(self, dir_vir, value):
        self.symbols[dir_vir] = value

    def add_arg(self, arg):
        self.args.append(arg)

    def get_args(self):
        return self.args
    
    def set_args(self, val):
        self.args = val
    
    def get_parent(self):
        return self.parent
    
    def print(self):
       print(self.fun_id)
       print(self.symbols)
       print(self.args)

class MaquinaVirtual:
    def __init__(self, quads, func_table, cmemory, w, h, canvas = None, result_text = None):
        self.quads = quads
        self.func_table = func_table
        self.gmemory = {}
        # load in gmemory state functions
        state_sym = initialStateSymbols(w,h)
        self.dir = {}
        # Iterating over both keys and values
        for key, value in state_sym.items():
            self.gmemory[value[Var.DIR_VIR]] = value[Var.VAL]
            self.dir[key] = value[Var.DIR_VIR]
        self.lmemory = Memoria()
        self.cmemory = cmemory
        self.args = []
        self.PIp = []
        self.logs = ""
        self.first_local = 10000
        self.first_const = 28000
        self.result_text = result_text
        if canvas is None:
            self.canvas = tkinter.Canvas(None, width=w, height=h, bd=0, bg="white")
        else:
            self.canvas = canvas
    
    def clear_canvas(self):
        self.canvas.delete("all")
    
    def update_arrow(self):
        self.canvas.configure(bg = self.read(self.dir["GET_BG"]))
        x, y = self.read(self.dir["GET_POS_X"]) , self.read(self.dir["GET_POS_Y"]) # Center coordinates of the canvas
        length = 20  # Length of the arrow
        orientation = self.read(self.dir["GET_ORIENTATION"]) +270 # Angle in degrees (assuming orientation is in degrees)

        # Calculate the end point based on the orientation and length
        end_x = x - length * math.cos(math.radians(orientation))
        end_y = y - length * math.sin(math.radians(orientation))

        # Draw the line
        line = self.canvas.create_line(end_x, end_y, x,y, arrow="last", fill="green", width = 3)

    # get the actual dir_vir when it's a tuple
    def get_dir_vir_array(self, dir_vir):
        my_dir_vir = []
        # is an array(3) or matrix(5)
        if len(dir_vir) == 3:
            index = self.read(dir_vir[1])
            if index < 0 or index >= dir_vir[2]:
                raise Exception(get_error_message(Error.OUT_OF_BOUNDS))
            my_dir_vir = [dir_vir[0]+index]
        elif len(dir_vir) == 5:
            index_1 = self.read(dir_vir[1])
            index_2 = self.read(dir_vir[3])
            if index_1 < 0 or index_1 >= dir_vir[2] or index_2 < 0 or index_2>= dir_vir[4]:
                raise Exception(get_error_message(Error.OUT_OF_BOUNDS))
            my_dir_vir = [dir_vir[0]+index_1*dir_vir[4] + index_2]
        elif len(dir_vir) == 2:
            # wanting an array of start_dir till size
            start_dir = dir_vir[0]
            size = dir_vir[1]
            end_dir = start_dir + size
            curr_dir = start_dir
            while curr_dir<end_dir:
                my_dir_vir.append(curr_dir)
                curr_dir+=1
        return my_dir_vir

    def read(self, dir_vir):
        my_dir_virs = []
        my_values_ret = []
        if isinstance(dir_vir, int):
            my_dir_virs = [dir_vir]
        else:
            # it's array or matrix
            my_dir_virs = self.get_dir_vir_array(dir_vir)
        for my_dir_vir in my_dir_virs:
            ret = 0
            if my_dir_vir < self.first_local:
                if my_dir_vir not in self.gmemory:
                    raise Exception(f"Var with {my_dir_vir} was read and is not in gmemory ")
                ret = self.gmemory[my_dir_vir]
                if ret is None:
                    raise Exception(f"Var with {my_dir_vir} was referenced before assignment ")
            elif my_dir_vir < self.first_const:
                if self.lmemory.get(my_dir_vir) is None:
                    raise Exception(f"Var with {my_dir_vir} was read and is not in lmemory ")
                ret = self.lmemory.get(my_dir_vir)
                if ret is None:
                    raise Exception(f"Var with {my_dir_vir} was referenced before assignment  ")
            else:
                if my_dir_vir not in self.cmemory:
                    raise Exception(f"Var with {my_dir_vir} was read and is not in cmemory ")
                ret = self.cmemory[my_dir_vir]
                if ret is None:
                    raise Exception(f"Var with {my_dir_vir} was referenced before assignment ")
            my_values_ret.append(ret)

        if len(my_values_ret) == 1:
            return my_values_ret[0]
        else:
            return my_values_ret
    
    def write(self, dir_vir, val = None):
        my_dir_vir = 0

        if isinstance(dir_vir, int):
            my_dir_vir = [dir_vir]
        else:
            # it's array or matrix
            my_dir_vir = self.get_dir_vir_array(dir_vir)
        
        for my_dir_virX in my_dir_vir:
            if my_dir_virX < self.first_local:
                self.gmemory[my_dir_virX] = val
            elif my_dir_virX < self.first_const:
                self.lmemory.set(my_dir_virX,val)
    
    def check_variable_type(self, val):
        if re.match(r'^[0-9]+\.[0-9]+$', val):
            return Tipo.FLOAT
        elif re.match(r'^[0-9]+$', val):
            return Tipo.INT
        elif re.match(r'^\'[a-z]\'$', val):
            return Tipo.CHAR
        elif re.match(r'^\".*?\"$', val):
            return Tipo.STRING
        elif val == "TRUE" or "FALSE":
            return Tipo.BOOL
        else:
            return "Unknown"
    
    def read_add(self, dir_vir, tipo, val):
        tipo_val = self.check_variable_type(val)
        if tipo_val != tipo:
           raise Exception(f"\nVar reading type mismatch")
        else:
            if tipo_val == Tipo.INT:
                self.write(dir_vir, int(val))
            elif tipo_val == Tipo.FLOAT:
                self.write(dir_vir, float(val))
            elif tipo_val == Tipo.BOOL:
                self.write(dir_vir, val == "TRUE")
            else:
                self.write(dir_vir,  val[1:-1])

    def execute(self, start = 0):
        # get the start time
        st = time.time()
        stack = []
        pc = start  # program counter
        self.clear_canvas()
        self.logs="\n"
        # self.result_text.configure(state="disabled")
        for idx, v in enumerate(self.quads):
            print(str(idx) + "." + str(v))
        while pc < len(self.quads):
            q = self.quads[pc]
            op = q[0]
            print(pc)
            # switch statement using QOp enumeration
            if op == QOp.EQUAL:
                self.write(q[3], None if q[1] is None else self.read(q[1]))
            elif op == QOp.EQUALP:
                self.write(q[3], self.read(self.read(q[1])))
            elif op == QOp.SET_ARRAY:
                for i, el in enumerate(q[1]):
                    if isinstance(el, list):
                        for j, e in enumerate(el):
                            self.write(q[3]+i*len(el)+j, self.read(e))
                    else:
                        self.write(q[3]+i, self.read(el))
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
            elif op == QOp.MOD:
                 self.write(q[3], self.read(q[1]) % self.read(q[2]))
            elif op == QOp.GOTO:
                pc = q[1]
                continue
            elif op == QOp.GOTOF:
                if self.read(q[1]) is False:
                    pc = q[2]
                    continue
            elif op == QOp.POS:
                self.write(self.dir["GET_POS_X"], self.read(q[1])) # GET_POS_X
                self.write(self.dir["GET_POS_Y"], self.read(q[2])) # GET_POS_Y
            elif op == QOp.BG:
                self.write(self.dir["GET_BG"], self.read(q[1]))
            elif op == QOp.COLOR:
                self.write(self.dir["GET_COLOR"], self.read(q[1]))
            elif op == QOp.PENDOWN:
                self.write(self.dir["IS_PENDOWN"], True)
            elif op == QOp.PENUP:
                self.write(self.dir["IS_PENDOWN"], False)
            elif op == QOp.WIDTH:
                self.write(self.dir["GET_WIDTH"], self.read(q[1]))
            elif op == QOp.CIRCLE:
                # TODO DRAW xd
                y1 = self.read(q[4])
                x1 = self.read(q[3])
                y0 = self.read(q[2])
                x0 = self.read(q[1])
                fill = q[5]
                if fill == "empty":
                    self.canvas.create_oval(x0,y0,x1,y1)
                else:
                    self.canvas.create_oval(x0,y0,x1,y1, fill=self.read(q[5]))
            elif op == QOp.POLYGON:
                # using id
                values = []
                # tupla de 2 por que le da un array
                if isinstance(q[1], tuple):
                    values = self.read(q[1])
                else:
                    # acte array
                    for dir in q[1]:
                        values.append(self.read(dir))
                if len(values)%2 == 1:
                    values.pop() # must be pair xd
                c = 0
                size = len(values)
                points = []
                while c<size:
                    points.append((values[c], values[c+1]))
                    c+=2
                if q[2] == "empty":
                    self.canvas.create_polygon(points)
                else:
                    self.canvas.create_polygon(points, fill = self.read(q[2]))
            elif op == QOp.RANDOM:
                val = 0
                if q[1] == "empty":
                    val = random.random()
                else:
                    val = random.randint(int(self.read(q[1][0])), int(self.read(q[1][1])))
                self.write(q[2], val)
            elif op == QOp.GO:
                # current position
                x = self.read(0)
                y = self.read(1)
                # direction in degrees, 0 is north, 90 is east
                direction = self.read(self.dir["GET_ORIENTATION"])
                # distance to move forward
                n = self.read(q[1])
                # calculate new position
                angle = math.radians(270 + direction)  # convert to radians and adjust for starting direction
                dx = n * math.cos(angle)
                dy = n * math.sin(angle)
                if(self.read(self.dir["IS_PENDOWN"])):
                    line = self.canvas.create_line(x, y, x+dx, y+dy, fill=self.read(self.dir["GET_COLOR"]), width = self.read(self.dir["GET_WIDTH"]))
                self.write(0, x + dx)
                self.write(1, y + dy)
            elif op == QOp.RIGHT:
                self.write(self.dir["GET_ORIENTATION"], (self.read(self.dir["GET_ORIENTATION"])%360 + self.read(q[1])%360)%360)
            elif op == QOp.LEFT:
                self.write(self.dir["GET_ORIENTATION"], (self.read(self.dir["GET_ORIENTATION"])%360 - self.read(q[1])%360)%360)
            elif op == QOp.ORIENTATION:
                self.write(self.dir["GET_ORIENTATION"], self.read(q[1])%360)
            elif op == QOp.PRINT:
                if(q[1] != -1):
                    self.logs+=(str(self.read(q[1])))
                if q[3] :
                    self.logs+= '\n'
                else :
                    self.logs+= " "
            elif op == QOp.READ:
                self.result_text.configure(state="normal")
                if self.result_text:
                    self.result_text.insert(self.result_text.index("end"), self.logs)
                return q + (pc + 1, )
            elif op == QOp.ERA:
                result = None
            elif op == QOp.GOSUB:
                stack.append((pc, q[1]))
                args = self.lmemory.get_args()
                # done using this list
                self.lmemory.set_args([])
                args_values = []
                # get args values before switching lmemory
                for arg_dir in args:
                    args_values.append(self.read(arg_dir))
                # switch lmemory REMEMBER current lmemory in parent of new one
                self.lmemory = Memoria(parent=self.lmemory, fun_id = q[1])
                fun_symbol = self.func_table.get_symbol(q[1])
                # fill new lmemory with args values
                for idx, arg in enumerate(fun_symbol[Var.ARGS]):
                    self.write(arg[Var.DIR_VIR], args_values[idx])
                # go to pc of fun
                pc = fun_symbol[Var.QUAD]
                continue
            elif op == QOp.PARAM:
                self.lmemory.add_arg(q[1])
            elif op == QOp.ENDFUNC:
                top = stack.pop()
                pc = top[0]
                self.lmemory = self.lmemory.get_parent()
            elif op == QOp.RETURN:
                fun_id = stack[-1][1]
                dir_vir_fun = self.func_table.get_symbol(fun_id)[Var.DIR_VIR]
                self.write(dir_vir_fun, self.read(q[1]))
            elif op == QOp.END:
                # get the end time
                et = time.time()
                elapsed_time = et - st
                self.logs+=f'\nExecution time: {elapsed_time} seconds'
                if self.result_text:
                    self.result_text.insert(self.result_text.index("end"), self.logs)
                    self.result_text.configure(state="disabled")
                self.update_arrow()
            pc += 1  # move to the next quad
        return self.logs
