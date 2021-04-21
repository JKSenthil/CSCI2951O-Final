import math
import numpy as np
from random import random, shuffle

class CVRP:
    def __init__(self, num_customers, num_vehicles, vehicle_capacity, customer_demand, customer_x_coord, customer_y_coord):
        self.num_customers = num_customers
        self.num_vehicles = num_vehicles
        self.vehicle_capacity = vehicle_capacity
        self.customer_demand = customer_demand

        self.dist = np.zeros((num_customers, num_customers))
        for i in range(num_customers):
            for j in range(num_customers):
                self.dist[i][j] = (customer_x_coord[i] - customer_x_coord[j]) ** 2 + (customer_y_coord[i] - customer_y_coord[j]) ** 2
        self.dist = np.sqrt(self.dist)

    def compute_obj_value(self, routes):
        cost = 0
        for route in routes:
            if len(route) == 0:
                continue
            cost += self.dist[0][route[0]]
            for i in range(1, len(route)):
                cost += self.dist[route[i-1]][route[i]]
            cost += self.dist[route[-1]][0]
        return round(cost, 2)

    def _cap_constraint(self, route):
        s = 0
        for n in route:
            s += self.customer_demand[n]
            if s > self.vehicle_capacity:
                return False
        return True

    def simulated_annealing(self, temperature=1, cooling_rate=0.95, max_iter=1000):
        def neighbor(r):
            r_prime = [[i for i in row] for row in r] # same as deepcopy(r)
            r1_idx = int(random() * len(r))
            r2_idx = int(random() * len(r))
            while len(r[r1_idx]) == 0 or len(r[r2_idx]) == 0:
                r1_idx = int(random() * len(r))
                r2_idx = int(random() * len(r))
            
            c1_idx = int(random() * len(r[r1_idx]))
            c2_idx = int(random() * len(r[r2_idx]))
            r_prime[r1_idx][c1_idx], r_prime[r2_idx][c2_idx] = r_prime[r2_idx][c2_idx], r_prime[r1_idx][c1_idx]
            count = 0
            while not (self._cap_constraint(r_prime[r1_idx]) and self._cap_constraint(r_prime[r2_idx])):
                r_prime = [[i for i in row] for row in r]
                c1_idx = int(random() * len(r[r1_idx]))
                c2_idx = int(random() * len(r[r2_idx]))

                r_prime[r1_idx][c1_idx], r_prime[r2_idx][c2_idx] = r_prime[r2_idx][c2_idx], r_prime[r1_idx][c1_idx]
                count += 1
                if count == 50:
                    return r
            return r_prime


        routes = self._generate_initial_config()
        for i in range(len(routes)):
            if len(routes[i]) <= 1:
                continue
            routes[i] = self._tsp_simulated_annealing(routes[i])

        best_routes = [[i for i in row] for row in routes] # same as deepcopy(routes)
        min_cost = self.compute_obj_value(routes)

        for j in range(max_iter):
            print(j)
            new_routes = neighbor(routes)
            for i in range(len(new_routes)):
                if len(new_routes[i]) <= 1:
                    continue
                new_routes[i] = self._tsp_simulated_annealing(new_routes[i])
            new_cost = self.compute_obj_value(new_routes)

            if new_cost < min_cost:
                best_routes = [[i for i in row] for row in new_routes]
                min_cost = new_cost 
                routes = new_routes
            elif math.exp((min_cost - new_cost) / temperature) < random():
                routes = new_routes
            temperature *= cooling_rate
        
        return best_routes

    def _generate_initial_config(self):
        routes = [[] for _ in range(self.num_vehicles)]
        rolling_capacities = [0 for _ in range(self.num_customers)]
        customer_idxs = list(range(1,self.num_customers))
        shuffle(customer_idxs)

        while customer_idxs:
            idx = customer_idxs.pop()
            customer_allocated = False
            for i in range(self.num_vehicles):
                if rolling_capacities[i] + self.customer_demand[idx] <= self.vehicle_capacity:
                    rolling_capacities[i] += self.customer_demand[idx]
                    routes[i].append(idx)
                    customer_allocated = True
                    break
            
            if not customer_allocated:
                routes = [[] for _ in range(self.num_vehicles)]
                rolling_capacities = [0 for _ in range(self.num_customers)]
                customer_idxs = list(range(1,self.num_customers))
                shuffle(customer_idxs)

        return routes

    def _tsp_simulated_annealing(self, route, temperature=1, cooling_rate=0.95, max_iter=1000):
        """
        https://www.baeldung.com/java-simulated-annealing-for-traveling-salesman
        """
        def cost(r):
            cost = self.dist[0][r[0]]
            for i in range(1, len(r)):
                cost += self.dist[r[i-1]][r[i]]
            cost += self.dist[r[-1]][0]
            return cost
        
        def neighbor(r):
            r_prime = r[:]
            idx1 = int(random() * len(r))
            idx2 = int(random() * len(r))
            r_prime[idx1], r_prime[idx2] = r_prime[idx2], r_prime[idx1]
            return r_prime
        
        best_solution = route[:]
        min_cost = cost(route)

        for _ in range(max_iter):
            new_route = neighbor(route)
            new_cost = cost(new_route)

            if new_cost < min_cost:
                best_solution = new_route[:]
                min_cost = new_cost 
                route = new_route
            elif math.exp((min_cost - new_cost) / temperature) < random():
                route = new_route
            temperature *= cooling_rate
        
        return best_solution