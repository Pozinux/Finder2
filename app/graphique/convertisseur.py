import pyside6uic
import os

# With the pysideuic module you can convert a file
#.ui as a.py file. The "compileUiDir" function
# allows us to convert all files inside
# of the folder that is indicated
# The variable __file__ corresponds to the current file
# os.path.dirname() retrieves the name of the folder from
# of the full path of the file

pyside6uic.compileUiDir(os.path.dirname(__file__))