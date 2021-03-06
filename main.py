#!/bin/env python3

import ast
import astunparse
import random
import inspect
import sys

builtins = [name for name, function in sorted(
    vars(__builtins__).items())] + ["__builtins__"]


class Obfuscator(ast.NodeTransformer):
    def __init__(self):
        self.seen = {}
        self.constants = []

    def visit_FunctionDef(self, node):
        if not node.name.startswith("_"):
            node.name = self.assign_name(node.name)
        for a in node.args.args:
            a.arg = self.assign_name(a.arg)
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        node.name = self.assign_name(node.name)
        return self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            oldname = alias.asname if alias.asname != None else alias.name
            alias.asname = self.assign_name(oldname)
        return self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        for alias in node.names:
            oldname = alias.asname if alias.asname != None else alias.name
            alias.asname = self.assign_name(oldname)
        return self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in builtins:
            node.id = self.add_to_constants(node.id)
        else:
            node.id = self.assign_name(node.id)
        return self.generic_visit(node)

    def visit_Constant(self, node):
        new_node = ast.Name()
        new_node.id = self.add_to_constants(node.value, convert=True)
        return new_node

    def add_to_constants(self, constant, convert=False):
        if convert:
            if isinstance(constant, str):
                constant = "\"{}\"".format(constant)
            elif isinstance(constant, int) or isinstance(constant, float):
                constant = str(constant)
            else:
                return constant

        if constant in self.constants:
            return "laTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller[{}]".format(self.constants.index(constant))
        else:
            self.constants.append(constant)
            return "laTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller[{}]".format(len(self.constants) - 1)

    def get_variable_name(self, i):
        return 'laTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller' + str(i)

    def assign_name(self, oldName):
        if oldName in self.seen:
            return self.seen[oldName]
        else:
            newName = self.get_variable_name(len(self.seen))
            self.seen[oldName] = newName
            return newName

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        tree = ast.parse(f.read())

    obfuscator = Obfuscator()
    obfuscator.visit(tree)

    random.seed('laTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller')
    shuffled = list(range(len(obfuscator.constants)))
    random.shuffle(shuffled)

    shuffled_constants = [
        obfuscator.constants[shuffled.index(i)] for i in range(len(obfuscator.constants))]

    out = """import random as LaTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller
LaTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller.seed('laTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller')
laTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller = [""" + ",".join(shuffled_constants) + """]
LaTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller.shuffle(laTableBleueQuiEstAuFondDuJardinEstEntrainDeRouiller)
""" + astunparse.unparse(tree)

    with open(sys.argv[2], "w") as f:
        f.write(out)
