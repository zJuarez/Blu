class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def add_symbol(self, name, attributes):
        self.symbols[name] = attributes
    
    # know for a fact is not in current symbols dict
    def add_symbol_object(self, symbol_object):
        self.symbols|= symbol_object

    def get_parent(self):
        return self.parent
    
    def is_declarated_in_block(self, name):
        return name in self.symbols
    
    def print(self):
        print(self.symbols)
        
    # get symbol information given its id
    def get_symbol(self, name):
        symbol_table = self
        while symbol_table:
            if name in symbol_table.symbols:
                return symbol_table.symbols[name]
            symbol_table = symbol_table.parent
        return None
