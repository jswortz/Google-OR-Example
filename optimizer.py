import math
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

def distance(x1, y1, x2, y2):
    # Manhattan distance
    dist = abs(x1 - x2) + abs(y1 - y2)

    return dist

# Distance callback

class CreateDistanceCallback(object):
  """Create callback to calculate distances and travel times between points."""

  def __init__(self, locations):
    """Initialize distance array."""
    num_locations = len(locations)
    self.matrix = {}

    for from_node in xrange(num_locations):
      self.matrix[from_node] = {}
      for to_node in xrange(num_locations):
#             JSW: THIS ALLOWS O TRAVEL PENALTY FROM DEPOT
#         if from_node == depot or to_node == depot:
#           self.matrix[from_node][to_node] = 0
#         else:
          x1 = locations[from_node][0]
          y1 = locations[from_node][1]
          x2 = locations[to_node][0]
          y2 = locations[to_node][1]
          self.matrix[from_node][to_node] = distance(x1, y1, x2, y2)

  def Distance(self, from_node, to_node):
     return self.matrix[from_node][to_node]


# Demand callback
class CreateDemandCallback(object):
  """Create callback to get demands at location node."""

  def __init__(self, demands):
    self.matrix = demands

  def Demand(self, from_node, to_node):
    return self.matrix[from_node]

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
    self.matrix = demands
    self.overhead_time = overhead_time

  def BlockOverheadTime(self, from_node, to_node):
    return int(self.overhead_time)


####################

######JSW ADD NONVIOLATOR CHECK TIME
# Service time (proportional to demand) callback.
class CreateCarCheckTimeCallback(object):
  """Create callback to get time windows at each location."""

  def __init__(self, cars, time_per_car_unit):
    self.matrix = cars
    self.time_per_car_unit = time_per_car_unit

  def ServiceTime(self, from_node, to_node):
    return int(self.matrix[from_node] * self.time_per_car_unit)
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
              overhead_time_callback):
    self.service_time_callback = service_time_callback
    self.travel_time_callback = travel_time_callback
    self.car_check_time_callback = car_check_time_callback
    self.overhead_time_callback = overhead_time_callback

  def TotalTime(self, from_node, to_node):
    service_time = self.service_time_callback(from_node, to_node)
    travel_time = self.travel_time_callback(from_node, to_node)
    car_check_time = self.car_check_time_callback(from_node, to_node)
    overhead_time = self.overhead_time_callback(from_node, to_node)
    return service_time + travel_time + car_check_time + overhead_time

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
  
def optimizer(locations, demands, start_times, end_times, \
         num_vehicles, search_time_limit,\
        horizon, time_per_demand_unit, speed, VehicleCapacity,\
        depot, time_per_car_unit, labs, cars, blockOverhead):

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

    # Callbacks to the distance function and travel time functions here.
    dist_between_locations = CreateDistanceCallback(locations)
    dist_callback = dist_between_locations.Distance

    routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
    demands_at_locations = CreateDemandCallback(demands)
    demands_callback = demands_at_locations.Demand


    NullCapacitySlack = 0;
    fix_start_cumul_to_zero = True
    capacity = "Unpaid and Overdue"

    routing.AddDimension(demands_callback, NullCapacitySlack, VehicleCapacity,
                         fix_start_cumul_to_zero, capacity)
    # Add time dimension.

    time = "Time"

    service_times = CreateServiceTimeCallback(demands, time_per_demand_unit)
    service_time_callback = service_times.ServiceTime
    
    car_check_time = CreateCarCheckTimeCallback(cars, time_per_car_unit)
    car_check_time_callback = car_check_time.ServiceTime
    
    block_overhead_time = CreateBlockOverheadTime(blockOverhead)
    block_overhead_time_callback = block_overhead_time.BlockOverheadTime

    travel_times = CreateTravelTimeCallback(dist_callback, speed)
    travel_time_callback = travel_times.TravelTime

    total_times = CreateTotalTimeCallback(service_time_callback, travel_time_callback\
                                          , car_check_time_callback, block_overhead_time_callback)
    total_time_callback = total_times.TotalTime

    routing.AddDimension(total_time_callback,  # total time function callback
                         horizon,
                         horizon,
                         fix_start_cumul_to_zero,
                         time)
    # Add time window constraints.
    time_dimension = routing.GetDimensionOrDie(time)
    
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
      solByCar = []
      for vehicle_nbr in range(num_vehicles):
        nodeSolution = []
        ticketLoad = []
        tminArr = []
#         tmaxArr = []
        index = routing.Start(vehicle_nbr)
        plan_output = 'Route {0}:'.format(vehicle_nbr)

        while not routing.IsEnd(index):
          node_index = routing.IndexToNode(index)
          load_var = capacity_dimension.CumulVar(index)
          time_var = time_dimension.CumulVar(index)
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
          tminArr.append(str(assignment.Min(time_var)))
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
        solByCar.append((nodeSolution, ticketLoad, tminArr))
        print "\n"
        print routing.CostVar()
      return solByCar, assignment
    else:
      print 'No solution found.'
  else:
    print 'Specify an instance greater than 0.'

def create_data_array():

  locations = [[820, 760], [960, 440], [500, 50], [490, 80], [130, 70], [290, 890], [580, 300],
               [840, 390], [140, 240], [120, 390], [30, 820], [50, 100], [980, 520], [840, 250],
               [610, 590], [10, 650], [880, 510], [910, 20], [190, 320], [930, 30], [500, 930],
               [980, 140], [50, 420], [420, 90], [610, 620], [90, 970], [800, 550], [570, 690],
               [230, 150], [200, 700], [850, 600], [980, 50]]

  demands =  [0, 19, 21, 6, 19, 7, 12, 16, 6, 16, 8, 14, 21, 16, 3, 22, 18,
             19, 1, 24, 8, 12, 4, 8, 24, 24, 2, 20, 15, 2, 14, 9]

  start_times =  [0] * len(demands)

  # tw_duration is the width of the time windows.
#   tw_duration = 60 * 24

  # In this example, the width is the same at each location, so we define the end times to be
  # start times + tw_duration. For problems in which the time window widths vary by location,
  # you can explicitly define the list of end_times, as we have done for start_times.
#   start_times =  [0] * len(start_times)
  end_times = [3600 * 24] * len(start_times)

#   for i in range(len(start_times)):
#     end_times[i] = start_times[i] + tw_duration
  data = [locations, demands, start_times, end_times]
  return data
# if __name__ == '__main__':
#   main()