from yacc import run
import sys
import os

files = sys.argv[1:] if len(sys.argv) > 1 else os.listdir('examples')

for fileName in files:
    with open("examples/" + fileName) as file:
        print(fileName)
        print('---')
        data = file.read()
        ast = run(data)
        print(ast)
        print('---')
