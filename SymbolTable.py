from enum import Enum

# clase de tabla de variables que se usa en compilacion
# tambien se usa esta clase para tabla de funciones pero
# esta no usa el parent
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
    
    # añadir info sobre una variable con id name
    def add_symbol(self, name, attributes):
        self.symbols[name] = attributes
    
    # check before that the symbol doesn't exist
    def add_symbol_object(self, symbol_object):
        self.symbols|= symbol_object

    # regresar el padre o la tabla de variables previa a esta
    def get_parent(self):
        return self.parent
    
    # si esta declarado en el mismo bloque una variable
    # se usa para saber por ejemplo si estoy en el scope
    # global.
    def is_declarated_in_block(self, name):
        return name in self.symbols
    
    # lo use para imprimir la func_table y que se vea mas bonita
    def imprimir_diccionario(self, diccionario, nivel=0):
        indentacion = '  ' * nivel
        for clave, valor in diccionario.items():
            if isinstance(valor, dict):
                print(f"{indentacion}{clave}:")
                self.imprimir_diccionario(valor, nivel + 1)
            else:
                if isinstance(clave, Enum):
                    clave_nombre = clave.name
                else:
                    clave_nombre = clave

                if isinstance(valor, list):
                    print(f"{indentacion}{clave_nombre}:")
                    for elemento in valor:
                        self.imprimir_diccionario(elemento, nivel + 1)
                else:
                    print(f"{indentacion}{clave_nombre}: {valor}")
    # para debugear y casos de prueba
    def print(self):
        self.imprimir_diccionario(self.symbols)
    
    # get symbol information given its id
    # can look for variables in higher blocks
    def get_symbol(self, name):
        symbol_table = self
        while symbol_table:
            if name in symbol_table.symbols:
                return symbol_table.symbols[name]
            symbol_table = symbol_table.parent
        return None
