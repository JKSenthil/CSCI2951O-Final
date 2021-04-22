import sys
from parser import parse
from cvrp import CVRP

def writeFile(filename, soln, cost):
    s = ""
    for route in soln:
        s += "0 "
        for e in route:
            s += str(e) + " "
        s += "0\n"

    f = open(filename + ".sol", "w")
    f.write(f"{cost} 0\n")
    f.write(s)
    f.close

if __name__ == "__main__":
    filename = sys.argv[1]

    args = parse(filename)
    cvrp = CVRP(*args)
    
    initial_config, best_config = cvrp.simulated_annealing()
    
    splt = filename.split('/')
    filename = 'results' + '/' + splt[1]
    writeFile(filename + "_initial", initial_config, cvrp.compute_obj_value(initial_config))
    writeFile(filename, best_config, cvrp.compute_obj_value(best_config))