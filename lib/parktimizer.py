import math
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


def ShortTermCrossing(xCurrent, yCurrent, sideCurrent, xLast, yLast, sideLast):
#     assign directions
    goSouth = yLast > yCurrent
    goNorth = yLast < yCurrent
    goEast = xLast < xCurrent
    goWest = xLast > xCurrent
    goSW = goSouth and goWest
    goSE = goSouth and goEast
    goNE = goNorth and goEast
    goNW = goNorth and goWest
    xWalk = abs(xCurrent - xLast)
    yWalk = abs(yCurrent - yLast)
    distance = xWalk + yWalk
    
        ##conditions for crossing n,s,e,w
    
    if sideLast == "N" and sideCurrent == "S" and goSouth:
        r=1
    elif sideLast == "S" and sideCurrent == "N" and goNorth:
        r=1
    elif sideLast == "E" and sideCurrent == "W" and goWest:
        r=1
    elif sideLast == "W" and sideCurrent == "E" and goEast:
        r=1
    ###SAME SIDES
    elif sideLast == "N" and sideCurrent == "N" and yWalk > 50:
        r=1
    elif sideLast == "S" and sideCurrent == "S" and yWalk > 50:
        r=1
    elif sideLast == "E" and sideCurrent == "E" and xWalk > 50:
        r=1
    elif sideLast == "W" and sideCurrent == "W" and xWalk > 50:
        r=1


    #diagonals
    elif sideLast == "N" and sideCurrent == "E" and (goSouth or goEast):
        r=1
    elif sideLast == "N" and sideCurrent == "W" and (goSouth or goWest):
        r=1
    elif sideLast == "S" and sideCurrent == "E" and (goNorth or goEast):
        r=1
    elif sideLast == "S" and sideCurrent == "W" and (goNorth or goWest):
        r=1
    elif sideLast == "W" and sideCurrent == "N" and (goEast or goNorth):
        r=1
    elif sideLast == "W" and sideCurrent == "S" and (goEast or goSouth):
        r=1
    elif sideLast == "E" and sideCurrent == "N" and (goWest or goNorth):
        r=1
    elif sideLast == "E" and sideCurrent == "S" and (goWest or goSouth):
        r=1

    else:
        r=0
    return r

def LongTermCrossings(blockSizeX, blockSizeY, xCurrent, yCurrent, xLast, yLast):
    xWalk = abs(xCurrent - xLast)
    yWalk = abs(yCurrent - yLast)
    xBlocks = math.floor(xWalk / blockSizeX)
    yBlocks = math.floor(yWalk / blockSizeY)
    return xBlocks + yBlocks
        


def distance(x1, y1, x2, y2):
    # Manhattan distance
    dist = abs(x1 - x2) + abs(y1 - y2)

    return dist

# Distance callback

class CreateDistanceCallback(object):
    
    def __init__(self, locations, street_name, street_side, cross_penalty, blockSizeX, blockSizeY):
        """Initialize distance array."""
        num_locations = len(locations)
        self.matrix = {}
        self.crossings = {}

        for from_node in xrange(num_locations):
            self.matrix[from_node] = {}
            self.crossings[from_node] = {}
            for to_node in xrange(num_locations):
                x1 = locations[from_node][0]
                y1 = locations[from_node][1]
                x2 = locations[to_node][0]
                y2 = locations[to_node][1]

                #### adding the street crossing penalty
                streetFrom = street_name[from_node]
                streetTo = street_name[to_node]
                sideFrom = street_side[from_node]
                sideTo = street_side[to_node]

                #########changing up new street crossing function 3.30.18 JSW
                stXing = ShortTermCrossing(x2, y2, sideTo, x1, y1, sideFrom)
                ltXing = LongTermCrossings(blockSizeX, blockSizeY, x2, y2, x1, y1)
                totalCrossings = stXing + ltXing
                self.crossings[from_node][to_node] = totalCrossings

                #############END OF DISTANCE BASED UPDATE
                self.matrix[from_node][to_node] = distance(x1, y1, x2, y2)# + x_penalty

    def Distance(self, from_node, to_node):
        return self.matrix[from_node][to_node]

    def Crossings(self, from_node, to_node):
        return self.crossings[from_node][to_node]

# Demand callback
class CreateDemandCallback(object):
    """Create callback to get demands at location node."""

    def __init__(self, demands):
        self.matrix = demands

    def Demand(self, from_node, to_node):
        return self.matrix[from_node]


####STREET NAME ADDED 3/25/18

class CreateStreetCrossingCallback(object):
    
    def __init__(self, street_name, street_side, crossingPenalty, locations, blockSizeX, blockSizeY):
        self.matrix = zip(street_name, street_side, locations)
        #         self.street_direction = street_direction
        self.crossing_penalty = crossingPenalty
        self.blockSizeX = blockSizeX
        self.blockSizeY = blockSizeY

    def CrossingPenalty(self, from_node, to_node):
        sideFrom = self.matrix[from_node][1]
        sideTo = self.matrix[to_node][1]
        x1 = self.matrix[from_node][2][0]
        y1 = self.matrix[from_node][2][1]
        x2 = self.matrix[to_node][2][0]
        y2 = self.matrix[to_node][2][1]
        stXing = ShortTermCrossing(x2, y2, sideTo, x1, y1, sideFrom)
        ltXing = LongTermCrossings(self.blockSizeX, self.blockSizeY, x2, y2, x1, y1)
        return self.crossing_penalty * (stXing + ltXing)

        
        
# Service time (proportional to demand) callback.
class CreateServiceTimeCallback(object):
    """Create callback to get time windows at each location."""

    def __init__(self, demands, time_per_demand_unit):
        self.matrix = demands
        self.time_per_demand_unit = time_per_demand_unit

    def ServiceTime(self, from_node, to_node):
        #     return int(self.matrix[from_node] * self.time_per_demand_unit)
        return self.matrix[from_node] * self.time_per_demand_unit

        ######JSW ADD BLOCK OVERHEAD TIME

class CreateBlockOverheadTime(object):
    """Create callback to get overhead time for each block."""

    def __init__(self, overhead_time):
        self.overhead_time = overhead_time
        
    def BlockOverheadTime(self, from_node, to_node):
        return int(self.overhead_time)



######JSW ADD NONVIOLATOR CHECK TIME
# Service time (proportional to demand) callback.
class CreateCarCheckTimeCallback(object):
    
    def __init__(self, carCheckTime, cars):
        self.matrix = zip(carCheckTime, cars)

    def ServiceTime(self, from_node, to_node):
        return int(self.matrix[from_node][0] * self.matrix[from_node][1])
#####################################

# Create the travel time callback (equals distance divided by speed).
class CreateTravelTimeCallback(object):
    """Create callback to get travel times between locations."""

    def __init__(self, dist_callback, speed):
        self.dist_callback = dist_callback
        self.speed = speed

    def TravelTime(self, from_node, to_node):
        travel_time = self.dist_callback(from_node, to_node) / self.speed
        return int(travel_time)
    
    
# Create total_time callback (equals service time plus travel time).
class CreateTotalTimeCallback(object):
    """Create callback to get total times between locations."""

    def __init__(self, service_time_callback, travel_time_callback, car_check_time_callback, \
                 overhead_time_callback, street_crossing_callback):
        self.service_time_callback = service_time_callback
        self.travel_time_callback = travel_time_callback
        self.car_check_time_callback = car_check_time_callback
        self.overhead_time_callback = overhead_time_callback
        self.street_crossing_callback = street_crossing_callback

    def TotalTime(self, from_node, to_node):
        service_time = self.service_time_callback(from_node, to_node)
        travel_time = self.travel_time_callback(from_node, to_node)
        car_check_time = self.car_check_time_callback(from_node, to_node)
        overhead_time = self.overhead_time_callback(from_node, to_node)
        street_crossing_time = self.street_crossing_callback(from_node, to_node)
        return service_time + travel_time + car_check_time + overhead_time + street_crossing_time

    def get_routes_array(assignment, num_routes, routing):
        # Get the routes for an assignent and return as a list of lists.
        routes = []
        for route_nbr in range(num_routes):
            node = routing.Start(route_nbr)
            route = []

        while not routing.IsEnd(node):
            node = assignment.Value(routing.NextVar(node))
            route.append(node)
            routes.append(route)
        return routes
    
    
    
#######BEHOLD PARKTIMIZER    
def parktimize(locations, demands, start_times, end_times, depot, time_per_car_unit, labs, cars, \
               street_name, street_side, num_vehicles=30, search_time_limit = 500,\
               horizon = 2.2 * 3600, time_per_demand_unit = 2*60, speed = 1.34, VehicleCapacity = 999999,\
               blockOverhead = 2 * 60, street_crossing_penalty = 10, \
               distance_constraint = int(1609.344 * 12), blockSizeX = int(0.3048 * 600), blockSizeY = int(0.3048 * 600) ,\
               distanceCrossingPenalty = False):

    num_locations = len(locations)

    if num_locations > 0:

        # The number of nodes of the VRP is num_locations.
        # Nodes are indexed from 0 to num_locations - 1. By default the start of
        # a route is node 0.
        routing = pywrapcp.RoutingModel(num_locations, num_vehicles, depot)
        search_parameters = pywrapcp.RoutingModel_DefaultSearchParameters()
        search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING) ## added by jw for search
        search_parameters.time_limit_ms = search_time_limit #added by jsw
        search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC) #added by jsw
        #JW ADD - make sure all nodes will be reached
        #routing.AddAllActive
        ## Added 3.28 for street crossing to be done by speed
        if distanceCrossingPenalty:
            cross_dist = street_crossing_penalty * speed
        else:
            cross_dist = 0
            # Callbacks to the distance function and travel time functions here.
        dist_between_locations = CreateDistanceCallback(locations, street_name, street_side, cross_dist, blockSizeX, \
                                                            blockSizeY)
        dist_callback = dist_between_locations.Distance
        crossing_callback = dist_between_locations.Crossings

        routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
        demands_at_locations = CreateDemandCallback(demands)
        demands_callback = demands_at_locations.Demand


        NullCapacitySlack = 0;
        fix_start_cumul_to_zero = True
        capacity = "Unpaid and Overdue"

        routing.AddDimension(demands_callback, NullCapacitySlack, VehicleCapacity,
                                 fix_start_cumul_to_zero, capacity)
            # Add time dimension.

        time = "Total Time"

        if distanceCrossingPenalty: #this disables the adding of time for crossing
            street_crossing_penalty = 0 #hack to not double add
                    #     self, street_name, street_side, crossingPenalty, locations, blockSizeX, blockSizeY
        street_crossing_times = CreateStreetCrossingCallback(street_name, street_side, street_crossing_penalty, \
                                                                         locations, blockSizeX, blockSizeY)
        street_crossing_callback = street_crossing_times.CrossingPenalty

        service_times = CreateServiceTimeCallback(demands, time_per_demand_unit)
        service_time_callback = service_times.ServiceTime

        car_check_time = CreateCarCheckTimeCallback(cars, time_per_car_unit)
        car_check_time_callback = car_check_time.ServiceTime

        block_overhead_time = CreateBlockOverheadTime(blockOverhead)
        block_overhead_time_callback = block_overhead_time.BlockOverheadTime

        travel_times = CreateTravelTimeCallback(dist_callback, speed)
        travel_time_callback = travel_times.TravelTime

        total_times = CreateTotalTimeCallback(service_time_callback, travel_time_callback,\
                                                          car_check_time_callback, block_overhead_time_callback, \
                                                          street_crossing_callback)
        total_time_callback = total_times.TotalTime
        horizon = int(horizon)
        dist_slack = 0
                    ### added distance constraint
        routing.AddDimension(dist_callback,  # total time function callback
                                         distance_constraint,
                                         distance_constraint + dist_slack,
                                         fix_start_cumul_to_zero,
                                         "Total Distance")


        crossing_constraint = 999999999
        routing.AddDimension(crossing_callback,  # total crossings callback
                                         crossing_constraint,
                                         crossing_constraint,
                                         fix_start_cumul_to_zero,
                                         "Total Crossings")

        routing.AddDimension(street_crossing_callback,  # total crossings callback
                                         crossing_constraint,
                                         crossing_constraint,
                                         fix_start_cumul_to_zero,
                                         "Total Crossings Time")

        routing.AddDimension(total_time_callback,  # total time function callback
                                         horizon,
                                         horizon,
                                         fix_start_cumul_to_zero,
                                         time)
        routing.AddDimension(travel_time_callback,  # total time function callback
                                         horizon,
                                         horizon,
                                         False,
                                         "Travel Time")
        routing.AddDimension(street_crossing_callback,  # total time function callback
                                         horizon,
                                         horizon,
                                         False,
                                         "Street Crossing Time")
        routing.AddDimension(service_time_callback,  # total time function callback
                                         horizon,
                                         horizon,
                                         False,
                                         "Ticket Writing Time")
        routing.AddDimension(car_check_time_callback,  # total time function callback
                                         horizon,
                                         horizon,
                                         False,
                                         "Car Checking Time")
        routing.AddDimension(block_overhead_time_callback,  # total time function callback
                                         horizon,
                                         horizon,
                                         False,
                                         "Block Checkin Time")

                    #     JSW - removed the time windows
                    #     for location in range(1, num_locations):
                    #       start = start_times[location]
                    #       end = end_times[location]
                    #       time_dimension.CumulVar(location).SetRange(start, end)
                    # Solve displays a solution if any.
        assignment = routing.SolveWithParameters(search_parameters)

        if assignment:
            size = len(locations)
            # Solution cost.
            print "Total distance of all routes: " + str(assignment.ObjectiveValue()) + "\n"
            # Inspect solution.
            capacity_dimension = routing.GetDimensionOrDie(capacity);
            time_dimension = routing.GetDimensionOrDie(time);
            travel_time = routing.GetDimensionOrDie("Travel Time")
            street_crossing_time = routing.GetDimensionOrDie("Street Crossing Time")
            ticket_writing_time = routing.GetDimensionOrDie("Ticket Writing Time")
            car_checking_time = routing.GetDimensionOrDie("Car Checking Time")
            block_checkin_time = routing.GetDimensionOrDie("Block Checkin Time")
            crossings = routing.GetDimensionOrDie("Total Crossings")
            street_crossing_time = routing.GetDimensionOrDie("Street Crossing Time")
            total_distance = routing.GetDimensionOrDie("Total Distance")

            solByCar = []
            for vehicle_nbr in range(num_vehicles):
                nodeSolution = []
                ticketLoad = []
                tminArr = []
                travTime = []
                scTime = []
                twTime = []
                ccTime = []
                bcTime = []
                totCrossings = []
                scTime = []
                ctTime = []
                tDist = []
                #         tmaxArr = []
                index = routing.Start(vehicle_nbr)
                plan_output = 'Route {0}:'.format(vehicle_nbr)

                while not routing.IsEnd(index):
                    node_index = routing.IndexToNode(index)
                    load_var = capacity_dimension.CumulVar(index)
                    trav_var = travel_time.CumulVar(index)
                    time_var = time_dimension.CumulVar(index)
                    street_cross_var = street_crossing_time.CumulVar(index)
                    ticket_write_var = ticket_writing_time.CumulVar(index)
                    car_check_var = car_checking_time.CumulVar(index)
                    block_check_var = block_checkin_time.CumulVar(index)
                    crossings_var = crossings.CumulVar(index)
                    ct_var = street_crossing_time.CumulVar(index)
                    dis_var = total_distance.CumulVar(index)
                    plan_output += \
                    " {node_index} Load({load}) Time({tmin}) -> ".format(
                        node_index=labs[node_index],
                        load=assignment.Value(load_var),
                        tmin=str(assignment.Min(time_var)))
                    #                         ,
                    #                         tmax=str(assignment.Max(time_var)))
                    index = assignment.Value(routing.NextVar(index))
                    nodeSolution.append(labs[node_index])
                    ticketLoad.append(assignment.Value(load_var))
                    travTime.append(assignment.Value(trav_var))
                    scTime.append(assignment.Value(street_cross_var))
                    twTime.append(assignment.Value(ticket_write_var))
                    ccTime.append(assignment.Value(car_check_var))
                    bcTime.append(assignment.Value(block_check_var))
                    tminArr.append(str(assignment.Value(time_var)))
                    totCrossings.append(assignment.Value(crossings_var))
                    ctTime.append(assignment.Value(ct_var))
                    tDist.append(assignment.Value(dis_var))
                    #           tmaxArr.append(str(assignment.Max(time_var)))

                node_index = routing.IndexToNode(index)
                load_var = capacity_dimension.CumulVar(index)
                time_var = time_dimension.CumulVar(index)
                plan_output += \
                    " {node_index} Load({load}) Time({tmin})".format(
                        node_index=labs[node_index],
                        load=assignment.Value(load_var),
                        tmin=str(assignment.Min(time_var)))
                    #                       ,
                    #                       tmax=str(assignment.Max(time_var)))
                print plan_output
                solByCar.append((nodeSolution, ticketLoad, tminArr, travTime, twTime, ccTime, bcTime,\
                                     totCrossings, ctTime, tDist))
                print "\n"
                print routing.CostVar()
            return solByCar, assignment
        else:
            print 'No solution found.'
    else:
        print 'Specify an instance greater than 0.'