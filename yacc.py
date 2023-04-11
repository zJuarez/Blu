from lex import MyLexer
from ply.yacc import yacc

lexer = MyLexer()
lexer.build()
tokens = lexer.tokens

def p_codigo(p):
    '''
    codigo : tipo ID EQUAL ID
    '''
    p[0] = 'CORRECTO '

def p_tipo(p):
    '''
    tipo : INT 
    | FLOAT
    | STRING
    | CHAR
    | BOOL
    '''
    p[0] = 'Tipo'

# Build the parser
parser = yacc()

data = '''STRING x = y'''

ast = parser.parse(data)

print(ast)