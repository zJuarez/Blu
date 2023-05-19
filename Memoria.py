from State import Tipo
from enum import Enum

first_local = 10000
first_const = 28000
class Section(Enum):
    GLOBAL = 1,
    LOCAL = 2,
    TEMP = 3,
    CONST = 4,
    STATE = 5,

class Memoria:
    def __init__(self):
        self.default = {
            Tipo.INT : 0,
            Tipo.BOOL : False,
            Tipo.CHAR : '',
            Tipo.FLOAT : 0.0,
            Tipo.STRING : "",
        }
        self.constMap = {}
        self.cmemory = {}
        self.memoryValues = self.get_initial_memory_values()

    def get_initial_memory_values(self): 
        first = 1000
        gap = 9000
        glob = first # [1000, 10,000)
        loca = first + gap # [10000, 19,000)
        temp =  first + 2*gap # [19000, 28,000)
        cons = first + 3*gap # [28000, 37,000)
        size = {Tipo.INT : 2000, 
                Tipo.FLOAT : 2000, 
                Tipo.BOOL : 2500, 
                Tipo.CHAR : 1000, 
                Tipo.STRING : 1499} # sum must be equal to gap - 1
        start = {Tipo.INT : 0, 
                Tipo.FLOAT : size[Tipo.INT], 
                Tipo.BOOL : size[Tipo.INT] + size[Tipo.FLOAT], 
                Tipo.CHAR :  size[Tipo.INT] + size[Tipo.FLOAT] + size[Tipo.BOOL], 
                Tipo.STRING : size[Tipo.INT] + size[Tipo.FLOAT] + size[Tipo.BOOL] + size[Tipo.CHAR] }
        
        # STORES NEXT DIRVIR given its section and type
        return {
            Section.GLOBAL : {
                Tipo.INT : glob, 
                Tipo.FLOAT : glob + start[Tipo.FLOAT], 
                Tipo.BOOL : glob + start[Tipo.BOOL], 
                Tipo.CHAR : glob + start[Tipo.CHAR], 
                Tipo.STRING : glob + start[Tipo.STRING]},
            Section.LOCAL : {
                Tipo.INT : loca, 
                Tipo.FLOAT : loca + start[Tipo.FLOAT], 
                Tipo.BOOL : loca + start[Tipo.BOOL], 
                Tipo.CHAR : loca + start[Tipo.CHAR], 
                Tipo.STRING : loca + start[Tipo.STRING]},
            Section.TEMP : {
                Tipo.INT : temp, 
                Tipo.FLOAT : temp + start[Tipo.FLOAT], 
                Tipo.BOOL : temp + start[Tipo.BOOL], 
                Tipo.CHAR : temp + start[Tipo.CHAR], 
                Tipo.STRING : temp + start[Tipo.STRING]},
            Section.CONST : {
                Tipo.INT : cons, 
                Tipo.FLOAT : cons + start[Tipo.FLOAT], 
                Tipo.BOOL : cons + start[Tipo.BOOL], 
                Tipo.CHAR : cons + start[Tipo.CHAR], 
                Tipo.STRING : cons + start[Tipo.STRING]},
        }

    # declarar variable (seccion, tipo) -> dar numero de dirVir
    def add(self, seccion, tipo, val = False, size = 1):
        if seccion == Section.CONST:
            if str(val) in self.constMap:
                return self.constMap[str(val)]
            else:
                self.constMap[str(val)] = self.memoryValues[seccion][tipo]
                self.cmemory[self.memoryValues[seccion][tipo]] = val
        next_dir_vir = self.memoryValues[seccion][tipo]
        self.memoryValues[seccion][tipo]+=size # prepare mempory for next var
        # TODO how to store val ?
        val = val if val != False else self.default[tipo]
        return next_dir_vir
    
    # end mod () -> resetear temp y local a inicial. returnear tamano de memoria que uso en el mod
    def end_mod(self):
        memoryUsedInMod = self.get_dif_of_section(Section.LOCAL) | self.get_dif_of_section(Section.TEMP)
        self.memoryValues[Section.LOCAL] = self.get_initial_memory_values()[Section.LOCAL] 
        self.memoryValues[Section.TEMP] = self.get_initial_memory_values()[Section.TEMP] 
        return memoryUsedInMod
    
    def get_dif_of_section(self, section):
        return {
            section : {
                Tipo.INT : self.get_dif(section, Tipo.INT), 
                Tipo.FLOAT : self.get_dif(section, Tipo.FLOAT), 
                Tipo.BOOL : self.get_dif(section, Tipo.BOOL), 
                Tipo.CHAR : self.get_dif(section, Tipo.CHAR), 
                Tipo.STRING : self.get_dif(section, Tipo.STRING),
                },
            }
    
    # helper fun to get memory used in scope
    def get_dif(self, seccion, tipo):
        return self.memoryValues[seccion][tipo] - self.get_initial_memory_values()[seccion][tipo]
    
    def print(self):
        print(self.get_dif_of_section(Section.GLOBAL))
        print(self.get_dif_of_section(Section.LOCAL))
        print(self.get_dif_of_section(Section.TEMP))
        print(self.get_dif_of_section(Section.CONST))
        print(self.constMap)
    
    def get_const_map(self):
        return self.cmemory

