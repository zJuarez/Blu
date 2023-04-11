import ply.lex as lex

class MyLexer(object):
    # --- Tokenizer
    reserved = {
    'FUNCTION' : 'FUNCTION',
    'IF' : 'IF',
    'ELSE' : 'ELSE',
    'FOR' : 'FOR',
    'POS': 'POS',
    'BG' : 'BG',
    'COLOR': 'COLOR',
    'PENDOWN': 'PENDOWN',
    'PENUP': 'PENUP',
    'WIDTH' : 'WIDTH',
    'GO' : 'GO',
    'RIGHT' : 'RIGHT',
    'LEFT' : 'LEFT',
    'PRINT': 'PRINT',
    'INT' : 'INT',
    'FLOAT' : 'FLOAT',
    'STRING' : 'STRING',
    'BOOL' : 'BOOL',
    'CHAR' : 'CHAR',
    'true': 'true',
    'false' : 'false'
    }

    # All tokens must be named in advance.
    tokens = ( 'EQUAL', 'PLUS', 'MINUS', 'TIMES', 
          'DIVIDE', 'LPAREN', 'RPAREN', 'LCOMP', 'RCOMP', 'COMMA', 
          'DOTS', 'LBRACKET', 'RBRACKET', 'LSQBRACKET', 
          'RSQBRACKET', 'AMPERSON', 'BAR', 'ICTE', 'FCTE', 'SCTE', 
          'CCTE', 'BCTE', 'ID') + tuple(reserved.values())
    
    # Regular expression rules for simple tokens
    t_EQUAL = r'\='
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LCOMP = r'\<'
    t_RCOMP = r'\>'
    t_COMMA = r'\,'
    t_DOTS = r'\:'
    t_LBRACKET = r'\{'
    t_RBRACKET = r'\}'
    t_LSQBRACKET = r'\['
    t_RSQBRACKET = r'\]'
    t_AMPERSON = r'\&'
    t_BAR = r'\|'

    # Token matching rules are written as regexs
    t_SCTE = r'\".*\"'
    t_CCTE = r'\'[a-z]\''
    t_BCTE = r'true|false'


    # A regular expression rule with some action code
    # Note addition of self parameter since we're in a class    
    def t_FCTE(self,t):
        r'[0-9]+\.[0-9]+'
        t.value = float(t.value)    
        return t
    
    def t_ICTE(self,t):
        r'[0-9]+'
        t.value = int(t.value)    
        return t
    
    def t_ID(self,t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value,'ID')    # Check for reserved words
        return t

    # Define a rule so we can track line numbers
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
    
    # Test it output
    def test(self,data):
        self.lexer.input(data)
        while True:
             tok = self.lexer.token()
             if not tok: 
                 break
             print(tok)