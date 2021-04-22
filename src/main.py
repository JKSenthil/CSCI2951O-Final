import sys
import time
from parser import parse
from cvrp import CVRP

if __name__ == "__main__":
    filename = sys.argv[1]

    args = parse(filename)
    cvrp = CVRP(*args)

    start_time = time.time()
    routes = cvrp.simulated_annealing()
    cost = cvrp.compute_obj_value(routes)

    for _ in range(3):
        routes2 = cvrp.simulated_annealing()
        cost2 = cvrp.compute_obj_value(routes2)
        if cost2 < cost:
            routes = routes2

    end_time = time.time()

    s = ""
    for route in routes:
        s += "0 "
        for e in route:
            s += str(e) + " "
        s += "0 "
    s = s[:-1]

    print(f"Instance: {filename} Time: {end_time - start_time} Result: {cost} Solution: {s}")
    