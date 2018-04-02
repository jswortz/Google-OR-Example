from lib.parktimizer import parktimize


def getData(kData, cluster, nClusters):
    clustData = kData[cluster]
    loc = clustData['locations']
    dem = clustData['demand']
    labs = clustData['labels']
    ca = clustData['cars']
    street_side = clustData['streetSide']
    street_name = clustData['streetName']
    #TODO: implement the LAZ GARAGE IF CLUSTERID = N-CLUSTERS
    if cluster == nClusters:
        loc.append([448476.6, 4636929])
        dem.append(0)
        ca.append(0)
        labs.append('starting by termial: LAZ GARAGE')
        street_name.append("NA")
        street_side.append("NA")
        depot = len(loc) - 1

    #begin appending of dummy start point
    else:
        loc.append(loc[labs.index(clustData['centralTerm'])])
        dem.append(0)
        ca.append(0)
        labs.append('starting by termial: ' + clustData['centralTerm'])
        street_name.append(street_name[labs.index(clustData['centralTerm'])])
        street_side.append(street_side[labs.index(clustData['centralTerm'])])
        depot = len(loc) - 1
    start_times =  [0] * len(clustData['cars'])
    end_times = [3600 * 24] * len(start_times)
    return loc, dem, ca, labs, depot, start_times, end_times, street_name, street_side


def empUp(kData, cluster, nClusters, maxi=50): 
    loc, dem, ca, labs, depot, start_times, end_times, street_name, street_side = getData(kData, cluster, nClusters)
    noEmps = 0
    solByCar = None
    while solByCar is None and noEmps < maxi:
        #try:
            noEmps += 1
            print("trying # of employees : " + str(noEmps))
            solByCar, assignment = parktimize(num_vehicles=noEmps, locations=loc, demands=dem, \
            start_times=start_times, end_times=end_times, search_time_limit = 20000,\
            horizon = int(6.5 * 3600), time_per_demand_unit = 3*60, speed = 1.34,
            depot = depot, time_per_car_unit=1*60, labs=labs, cars=ca, blockOverhead = 2 * 60, \
             street_crossing_penalty = 60, street_name=street_name, street_side=street_side, \
             distance_constraint = 20922, blockSizeX = int(0.3048 * 600), blockSizeY = int(0.3048 * 600))
        #except:
            # pass
    return solByCar, noEmps