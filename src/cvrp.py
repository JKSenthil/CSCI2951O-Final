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
            cost += self.dist[0][route[0]] # manually add first edge (fr depot)
            for i in range(1, len(route)):
                cost += self.dist[route[i-1]][route[i]]
            cost += self.dist[route[-1]][0] # manually add last edge (to depot)
        return round(cost, 2)

    def _cap_constraint(self, route):
        s = 0
        for n in route:
            s += self.customer_demand[n]
            if s > self.vehicle_capacity:
                return False
        return True

    '''
    output of this fn is passed to compute_obj_value
    '''
    def simulated_annealing(self, temperature=1, cooling_rate=0.95, max_iter=10000):
        def RHA(r):
            r_prime = [[i for i in row] for row in r] # same as deepcopy(r)
            highest_avg_customer_idx = -1
            route_idx = -1
            max_cost = float("-inf")
            for j, route in enumerate(r):
                if len(route) == 0 or len(route) == 1:
                    continue
                c = self.dist[0][route[0]] + self.dist[route[0]][route[1]]
                if c > max_cost:
                    highest_avg_customer_idx = 0
                    route_idx = j
                    max_cost = c
                for i in range(1, len(route)-1):
                    c = self.dist[route[i-1]][route[i]] + self.dist[route[i]][route[i+1]]
                    if c > max_cost:
                        highest_avg_customer_idx = i
                        route_idx = j
                        max_cost = c
                c = self.dist[route[-2]][route[-1]] + self.dist[route[-1]][0]
                if c > max_cost:
                    highest_avg_customer_idx = len(route) - 1
                    route_idx = j
                    max_cost = c

            assert highest_avg_customer_idx != -1
            assert route_idx != -1

            customer_idx = r_prime[route_idx].pop(highest_avg_customer_idx)

            route_idxs = list(range(len(r)))
            shuffle(route_idxs)
            inserted = False
            for r_idx in route_idxs:
                r_prime[r_idx].append(customer_idx)
                if not self._cap_constraint(r_prime[r_idx]):
                    r_prime[r_idx].pop()
                else:
                    inserted = True
                    break
            if not inserted:
                print("not inserted")
            return r_prime

        # beginning of sim_annealing fn
        routes = self._generate_initial_configV2()
        for i in range(len(routes)):
            # if there is <= 1 node assigned to vehicle i, then no need to solve tsp prob
            # each vehicle represents a tsp prob to solve, after we have done step 1 (the bin packing)
            if len(routes[i]) <= 1:
                continue
            routes[i] = self._tsp_simulated_annealing(routes[i])

        initial_routes = [[i for i in row] for row in routes] # same as deepcopy(routes)
        best_routes = [[i for i in row] for row in routes] # same as deepcopy(routes)
        min_cost = self.compute_obj_value(best_routes)

        print('initial objective:', min_cost)
        for j in range(max_iter): 
            new_routes = RHA(routes)
            for _ in range(4):
                new_routes = RHA(new_routes)
            for i in range(len(new_routes)):
                if len(new_routes[i]) <= 1:
                    continue
                new_routes[i] = self._tsp_simulated_annealing(new_routes[i])
            new_cost = self.compute_obj_value(new_routes)

            if new_cost < min_cost:
                best_routes = [[i for i in row] for row in new_routes]
                min_cost = new_cost 
                print('objective at iteration', j, ':', min_cost)
                routes = new_routes
            elif math.exp((min_cost - new_cost) / temperature) < random():
                routes = new_routes
            temperature *= cooling_rate
        
        return initial_routes, best_routes

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

    '''
    output: 2d array called routes

    '''
    def _generate_initial_configV2(self):
        def shuffle_tiny_bit(a, times=1):
            for _ in range(times):
                i = int(random() * len(a))
                j = int(random() * len(a))
                a[i], a[j] = a[j], a[i]
            return a

        routes = [[] for _ in range(self.num_vehicles)]
        rolling_capacities = [0 for _ in range(self.num_vehicles)]
        customer_idxs = list(range(1,self.num_customers))
        customer_idxs.sort(key=lambda x : self.dist[x][0])

        # each iteration of while loop is assigning a customer to a vehicle
        while customer_idxs:
            idx = customer_idxs.pop(0) # id of customer we are trying to assign
            customer_allocated = False

            # try to assign this customer to each vehicle
            for i in range(self.num_vehicles):
                if rolling_capacities[i] + self.customer_demand[idx] <= self.vehicle_capacity:
                    rolling_capacities[i] += self.customer_demand[idx]
                    routes[i].append(idx)
                    customer_allocated = True
                    break
            
            # if we fail to assign customer to vehicle, then reset, with some randomness
            if not customer_allocated:
                routes = [[] for _ in range(self.num_vehicles)]
                rolling_capacities = [0 for _ in range(self.num_vehicles)]
                customer_idxs = list(range(1,self.num_customers))
                customer_idxs.sort(key=lambda x : self.dist[x][0])
                customer_idxs = shuffle_tiny_bit(customer_idxs, times=3)

        return routes

    def _generate_initial_configV3(self):
        routes = [[] for _ in range(self.num_vehicles)]
        rolling_capacities = [0 for _ in range(self.num_customers)]
        customer_idxs = list(range(1,self.num_customers))
        customer_idxs.sort(key=lambda x : self.dist[x][0])

        for i in range(self.num_vehicles):
            if len(customer_idxs) == 1:
                routes[i].append(customer_idxs.pop())
                break

            idx1 = customer_idxs.pop(0)
            idx2 = customer_idxs.pop(0)
            rolling_capacities[i] = self.customer_demand[idx1] + self.customer_demand[idx2]
            routes[i].append(idx1)
            while True:
                if len(customer_idxs) == 0:
                    break
                idx = customer_idxs.pop()
                if rolling_capacities[i] + self.customer_demand[idx] > self.vehicle_capacity:
                    customer_idxs.append(idx)
                    break
                else:
                    rolling_capacities[i] += self.customer_demand[idx]
                    routes[i].append(idx)
            routes[i].append(idx2)
        
        if len(customer_idxs) != 0:
            assert 1 == 0 # force error to raise

        return routes

    def _tsp_simulated_annealing(self, route, temperature=1, cooling_rate=0.95, max_iter=10):
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
