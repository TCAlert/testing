# ----------------------------------------
#  CSC 315 / 615 Spring 2023
#  Project 4 TaxonomyTree
#
#  Deelan Jariwala
# ----------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import bisect


# ------------------------------------------
# The TaxonomyNode class
# ------------------------------------------

class TaxonomyNode:
    def __init__(self, name, category):
        self.name = name  # The "name" of the node such as Animalia or Chordata
        #   (i.e. the values of the csv table)
        self.category = category  # The "category" such as Kingdom or Phylum
        #   (i.e. the column headers of the csv table)
        self.children = []  # The list of children each of type TaxonomyNode

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.name == other.name

    def addChild(self, name, category):
        # ToDo: function must create a TaxonomyNode(name,category)
        #       and insert this node into self.children
        #       in sorted order of the name
        newNode = TaxonomyNode(name, category)
        self.children.append(newNode)
        return

    def hasChild(self, name, category):
        # ToDo: function returns True if TaxonomyNode(name,category)
        #       is in self.children, and returns False otherwise
        if TaxonomyNode(name, category) in self.children:
            return True
        else:
            return False

    def getChild(self, name, category):
        # ToDo: add code that returns the child node with a given name,category
        #       it should return None, if no such name,category exists
        if TaxonomyNode(name, category) in self.children:
            for x in range(len(self.children)):
              if self.children[x].name == name:
                return self.children[x]
        else:
            return None


# ------------------------------------------
# The TaxonomyTree class
# ------------------------------------------

class TaxonomyTree:
    def __init__(self):
        self.root = TaxonomyNode("", "")

    def addSpecies(self, names, categories):
        # ToDo:  implement code to populate the TaxonomyTree
        #        self.root given the names and categories
        node = self.root
        for x in range(len(names)):
            if node.hasChild(names[x], categories[x]):
                node = node.getChild(names[x], categories[x])
            else:
                node.addChild(names[x], categories[x])
                node = node.getChild(names[x],categories[x])

    @staticmethod
    def print_internal(node, lineno, number_str, name_str):
        # ToDo:  Implement a recursive function to print
        #        the contents of the TaxonomyTree as formatted
        #        to resemble the sample output
            print(lineno, number_str, name_str)
            counter = 0
            for x in range(len(node.children)):
                counter = counter + 1
                lineno = lineno + 1
                temp = node.children[x]
                name_str = name_str + "." + temp.name
                number_str = str(number_str) + '.' + str(counter)
                lineno = TaxonomyTree.print_internal(temp, lineno, number_str, name_str)

            return lineno

    def print(self):
        # Do not modify
        TaxonomyTree.print_internal(self.root, 1, "", "")

    @staticmethod
    def listScientificNames_internal(node):
        # Extra Credit:  Implement a recursive function to traverse
        #                the TaxonomyTree and return a list of
        #                Scientific Names
        return []

    def printScientificNames(self):
        # Do not modify
        names = TaxonomyTree.listScientificNames_internal(self.root)
        names.sort()
        for name in names:
            print(name)


# ------------------------------------------
# Main code
#   Do not Modify
# ------------------------------------------

# Read the Pandas dataframe
df = pd.read_csv(r"C:\Users\deela\Downloads\taxonomy.csv")
rows = df.shape[0]
cols = df.shape[1]
categories = list(df.columns)[1:cols]

# Construct a Taxonomy Tree
tree = TaxonomyTree()

# Insert species into the tree row by row
for r in range(rows):
    names = list(df.iloc[r, 1:cols])
    tree.addSpecies(names, categories)

# Print the contents of the TaxonomyTree
tree.print()
