from optimizer import optimizer
def getData(cluster, kData):
    clustData = kData[cluster]
    loc = clustData['locations']
    dem = clustData['demand']
    labs = clustData['labels']
    ca = clustData['cars']


    #begin appending of dummy start point
    loc.append(loc[labs.index(clustData['centralTerm'])])
    dem.append(0)
    ca.append(0)
    labs.append('starting by termial: ' + clustData['centralTerm'])
    depot = len(loc) - 1
    start_times =  [0] * len(dem)
    end_times = [3600 * 24] * len(dem)
    return loc, dem, ca, labs, depot, start_times, end_times
    

def empUp(searchLimit = 30000, horizion = int(6.4 * 3600), timePerTicket = 3*60, walkingSpeed = 1.34, timePerCar = 1 * 60, \
          overheadPerBlock = 2*60):    
    noEmps = 0
    solByCar = None
    while solByCar is None:
        try:
            noEmps += 1
            print("trying # of emplyoes : " + str(noEmps))
            solByCar, assignment = optimizer(locations=loc, demands=dem, start_times=start_times, end_times=end_times, \
         num_vehicles=noEmps, search_time_limit = searchLimit,\
        horizon = horizion, time_per_demand_unit = timePerTicket, speed = walkingSpeed, VehicleCapacity = 999999,\
        depot = depot, time_per_car_unit=timePerCar, labs=labs, cars=ca, blockOverhead = overheadPerBlock)
        except:
            pass
    return solByCar, noEmps

def empUpByCluster(nClusters, kData, searchLimit = 30000, horizion = int(6.4 * 3600), timePerTicket = 3*60, \
     walkingSpeed = 1.34, timePerCar = 1 * 60, overheadPerBlock = 2*60):
     for k in range(nClusters):
        print("Starting cluster {} of {}".format(k, nClusters))
        loc, dem, ca, labs, depot, start_times, end_times = getData(k, kData)
        solution, noEmps = empUp()
        kData[k].update({'solution': solution, 'empsNeeded': noEmps})
        return kDatademand