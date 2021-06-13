# -*- coding: utf-8 -*-
"""
#Scripted by Mahmoud A. Sofy. @2021
#Fayoum university, ECE class 2022.
LinkedIn: /in/mahmoud-sofy
"""
"""
Core of the simulator:
    1- __simulate():
        Takes the netlist and returns:
            .Symbolic expressions.
            .Numeric values for the nodes voltages.
        It is the integration of the listed below functions
            
    2- __netlist_parse():
        Parses the netlist and returns:
            .Array: consists of each instance symbol and the nodes connected by it.
            .Dictionary: consists of each symbol value.
            
    3- __get_nodes_number():
        Returns number of nodes.
        
    4- __mna_matrices:
        Takes the parsed netlist "Array" and returns:
            .Y, V, I matrices.
            
    5- __solve():
        Takes MNA matrices and returns:
            .Dictionary: contains nodes voltages expressions encoded as:
                Key: Node voltage (e.g. V1).
                Value: Voltage expression
                
    6- __eval():
        Takes both expressions, and values dictionaries and retuns:
            .Same expressions dictionary but evaluated.   
"""
"""
TODO:
    -Core: still has severe limitations need to be solved:
        1. Nodes must be numbered regularly.
        2. Only independent current sources are supported.
        
    -Higher level of integration:
        1. Non-linear devices need to be integrated.
        2. Iterative loops for different analysis types [Core in the loop].        
"""

import warnings
from sympy import zeros, symbols, simplify, Inverse
warnings.filterwarnings("ignore")


def __simulate(netlist):
    parsed_netlist, values = __netlist_parse(netlist)
    y_matrix, v_matrix, i_matrix = __mna_matrices(parsed_netlist)
    expressions = __solve(y_matrix, v_matrix, i_matrix)
    print(expressions)
    print(__eval(expressions, values))
    
    
def __netlist_parse(netlist):
    file = open(netlist)
    unparsed_netlist = file.readlines()
    file.close()

    raw_netlist = []
    for line in unparsed_netlist[1:]:
        if line[0] != '*' and line != "\n":
            raw_netlist.append(line)
        
    values = {}
    parsed_netlist = []
    for line in raw_netlist:
        temp_line = line.split(' ')
        parsed_netlist.append(temp_line[:-1])
        values[temp_line[0]] = temp_line[-1]
    
    return parsed_netlist, values


def __get_nodes_number(netlist):
    nodes = []
    for branch in netlist:
        nodes.append(branch[1])
        nodes.append(branch[2])
    nodes.sort()
    return int(nodes[-1])

    
def __mna_matrices(parsed_netlist):
    no_nodes = __get_nodes_number(parsed_netlist) + 1
    y = zeros(no_nodes, no_nodes)
    v = zeros(no_nodes, 1)
    i = zeros(no_nodes, 1)
    v_count = 0
    for branch in parsed_netlist:
        try:
            fr = int(branch[1])
            to = int(branch[2])
            var = symbols(branch[0])
            if branch[0][0] == 'R':
                y[fr, fr] += 1/var
                y[to, to] += 1/var
                y[fr, to] -= 1/var
                y[to, fr] -= 1/var
                v_count += 1
                v_node = symbols('V' + str(v_count))
                v[v_count, 0] += v_node
            elif branch[0][0] == 'I':
                i[fr, 0] -= var
                i[to, 0] += var
        except:
            pass
        
    return y[1:, 1:], v[1:,:], i[1:,:]
     
   
def __solve(y, v, i):
    inv = simplify(y.inv())
    v_mat = simplify(inv*i)
    expressions = {}
    count = 0
    for v_exp in v_mat:
        expressions[str(v[count])] = v_exp
        count += 1
    return expressions


def __eval(expressions, values):
    evaluated = {}
    for key in expressions.keys():
        evaluated[key] = expressions[key].subs(values)
    return evaluated
