def parse(filename):
    with open(filename, 'r') as fp:
        line = fp.readline().split(" ")

        num_customers = int(line[0])
        num_vehicles = int(line[1])
        vehicle_capacity = int(line[2])

        customer_demand = [0 for _ in range(num_customers)]
        customer_x_coord = [0 for _ in range(num_customers)]
        customer_y_coord = [0 for _ in range(num_customers)]

        for i in range(0, num_customers):
            line = fp.readline().split(" ")

            customer_demand[i] = int(line[0])
            customer_x_coord[i] = float(line[1])
            customer_y_coord[i] = float(line[2])
    
    return num_customers, num_vehicles, vehicle_capacity, customer_demand, customer_x_coord, customer_y_coord

