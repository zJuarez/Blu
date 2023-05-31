from MaquinaVirtual import MaquinaVirtual
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
        parser = my_parser.parse(data)
        if (parser[0] == "ERROR"):
            print(parser)
        else:
            mv = MaquinaVirtual(parser[0], parser[1], parser[2], 800, 1000)
            print(mv.execute())
        print('---')
