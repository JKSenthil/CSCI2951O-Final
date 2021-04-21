import sys
from parser import parse
from cvrp import CVRP

if __name__ == "__main__":
    filename = sys.argv[1]

    args = parse(filename)
    cvrp = CVRP(*args)
    
    initial_config = cvrp.simulated_annealing()
    cost = cvrp.compute_obj_value(initial_config)
    
    s = ""
    for route in initial_config:
        s += "0 "
        for e in route:
            s += str(e) + " "
        s += "0\n"

    f = open(filename + ".sol", "w")
    f.write(f"{cost} 0\n")
    f.write(s)
    f.close


    # new_config = []
    # for route in initial_config:
    #     if len(route) > 2:
    #         new_route, _ = cvrp._tsp_simulated_annealing(route)
    #         new_config.append(new_route)
    #     else:
    #         new_config.append(route)
    # cost = cvrp._compute_obj_value(new_config)

    # s = ""
    # for route in new_config:
    #     s += "0 "
    #     for e in route:
    #         s += str(e) + " "
    #     s += "0\n"

    # f = open(filename + "2.sol", "w")
    # f.write(f"{cost} 0\n")
    # f.write(s)
    # f.close