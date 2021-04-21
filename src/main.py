import sys
from parser import parse
from cvrp import CVRP

if __name__ == "__main__":
    filename = sys.argv[1]

    args = parse(filename)
    cvrp = CVRP(*args)
    initial_config = cvrp._generate_initial_config()
    print(initial_config)
    