from myparser import MyParser
import sys
import os

my_parser = MyParser()

files = sys.argv[1:] if len(sys.argv) > 1 else os.listdir('examples')

for fileName in files:
    with open("examples/" + fileName) as file:
        print(fileName)
        print('---')
        data = file.read()
        ast = my_parser.parse(data)
        print(ast)
        print('---')
