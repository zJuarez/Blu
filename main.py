from MaquinaVirtual import MaquinaVirtual
from myparser import MyParser
import sys
import os

my_parser = MyParser()

files = sys.argv[1:] if len(sys.argv) > 1 else os.listdir('test1')

for fileName in files:
    with open("test1/" + fileName) as file:
        print(fileName)
        print('---')
        data = file.read()
        print("CODE: ")
        print(data)
        print()
        parser = my_parser.parse(data)
        if (parser[0] == "ERROR"):
            print(parser)
        else:
            mv = MaquinaVirtual(parser[0], parser[1], parser[2], 800, 1000)
            print(mv.execute())
        print('---')
