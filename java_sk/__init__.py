import sys
import os

pwd = os.path.dirname(__file__)

javaAST = os.path.abspath(os.path.join(pwd,'../../javaAST'))
sys.path.insert(0, javaAST)

from ast.body.classorinterfacedeclaration import ClassOrInterfaceDeclaration
from ast.body.methoddeclaration import MethodDeclaration


CONVERSION_TYPES = {u'boolean':u'bit',
                    u'this':u'self',
                    u'byte':u'char',
                    u'short':u'char',
                    u'int':u'int',
                    u'long':u'double',
                    u'float':u'float',
                    u'double':u'double',
                    u'Byte':'char',
                    u'Short':u'char',
                    u'Integer':u'int',
                    u'Long':u'long',
                    u'Float':u'float',
                    u'Double':u'double'}

sk_d = {u'@t': u'ClassOrInterfaceDeclaration', u'name': u''}
sk_cls = ClassOrInterfaceDeclaration(sk_d)

minimize = {u'@t': u'MethodDeclaration', u'name': {u'name': u'minimize'}, u'type': {u'@t': u'VoidType'}, u'parentNode': sk_d}
sk_cls.members.append(minimize)

builtins = {u'minimize': MethodDeclaration(minimize)}
