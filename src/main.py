import sys
import time
from parser import parse
from cvrp import CVRP

if __name__ == "__main__":
    filename = sys.argv[1]

    args = parse(filename)
    cvrp = CVRP(*args)

    start_time = time.time()
    _, best_routes = cvrp.simulated_annealing()
    best_cost = cvrp.compute_obj_value(best_routes)

    # run SA 3 more times
    for _ in range(3):
        _, new_routes = cvrp.simulated_annealing()
        new_cost = cvrp.compute_obj_value(new_routes)
        if new_cost < best_cost:
            best_routes = new_routes
            best_cost = new_cost

    end_time = time.time()

    s = ""
    for route in best_routes:
        s += "0 "
        for e in route:
            s += str(e) + " "
        s += "0 "
    s = s[:-1]

    print(f"Instance: {filename.split('/')[1]} Time: {end_time - start_time} Result: {best_cost} Solution: {s}")
    