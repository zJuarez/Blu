from State import Tipo, initialStateSymbols
from enum import Enum

class Section(Enum):
    GLOBAL = 1,
    LOCAL = 2,
    TEMP = 3,
    CONST = 4,
    STATE = 5,

class Memoria:
    def __init__(self):
        first = 1000
        gap = 9000
        glob = first
        loca = first + gap
        temp =  first + 2*gap
        cons = first + 3*gap

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
        self.initialMemoryValues = {
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
        self.memoryValues = self.initialMemoryValues

    # declarar variable (seccion, tipo) -> dar numero de dirVir
    def get_next_dir_vir(self, seccion, tipo):
        next_dir_vir = self.memoryValues[seccion][tipo]
        self.memoryValues[seccion][tipo]+=1 # prepare mempory for next var
        return next_dir_vir
    

    # end mod () -> resetear temp y local a inicial. returnear tamano de memoria que uso en el mod
    def end_mod(self):
        memoryUsedInMod = {
            Section.LOCAL : {
                Tipo.INT : self.get_dif(Section.LOCAL, Tipo.INT), 
                Tipo.FLOAT : self.get_dif(Section.LOCAL, Tipo.FLOAT), 
                Tipo.BOOL : self.get_dif(Section.LOCAL, Tipo.BOOL), 
                Tipo.CHAR : self.get_dif(Section.LOCAL, Tipo.CHAR), 
                Tipo.STRING : self.get_dif(Section.LOCAL, Tipo.STRING),
                },
            Section.TEMP : {
                Tipo.INT : self.get_dif(Section.TEMP, Tipo.INT), 
                Tipo.FLOAT : self.get_dif(Section.TEMP, Tipo.FLOAT), 
                Tipo.BOOL : self.get_dif(Section.TEMP, Tipo.BOOL), 
                Tipo.CHAR : self.get_dif(Section.TEMP, Tipo.CHAR), 
                Tipo.STRING : self.get_dif(Section.TEMP, Tipo.STRING),
                },
            }
        self.memoryValues[Section.LOCAL] =  self.memoryInitialValues[Section.LOCAL] 
        self.memoryValues[Section.TEMP] =  self.memoryInitialValues[Section.TEMP] 
        return memoryUsedInMod
    
    # helper fun to get memory used in scope
    def get_dif(self, seccion, tipo):
        return self.memoryValues[seccion][tipo] - self.initialMemoryValues[seccion][tipo]

    # TODO setear valor (dirVir, valor) -> poner el valor de dirvir

