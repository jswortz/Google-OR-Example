from lib.parktimizer import parktimize
import pickle
import datetime
import pandas as pd
import os

def getData(cluster, data, nClusters):
    kData = data
    clustData = kData[cluster]
    loc = clustData['locations']
    dem = clustData['demand']
    labs = clustData['labels']
    ca = clustData['cars']
    street_side = clustData['streetSide']
    street_name = clustData['streetName']
    cct = clustData['carCheckTime']
    #TODO: implement the LAZ GARAGE IF CLUSTERID = N-CLUSTERS
    if cluster == nClusters:
        loc.append([448476.6, 4636929])
        dem.append(0)
        ca.append(0)
        cct.append(0)
        labs.append('starting by termial: LAZ GARAGE')
        street_name.append("NA")
        street_side.append("NA")
        depot = len(loc) - 1

    #begin appending of dummy start point
    else:
        loc.append(loc[labs.index(clustData['centralTerm'])])
        dem.append(0)
        ca.append(0)
        cct.append(0)
        labs.append('starting by termial: ' + clustData['centralTerm'])
        street_name.append(street_name[labs.index(clustData['centralTerm'])])
        street_side.append(street_side[labs.index(clustData['centralTerm'])])
        depot = len(loc) - 1
    start_times =  [0] * len(dem)
    end_times = [3600 * 24] * len(start_times)
    return loc, dem, ca, labs, depot, start_times, end_times, street_name, street_side, cct


def empUp(locations, demands, start_times, end_times, depot, time_per_car_unit, labs, cars, \
               street_name, street_side, search_time_limit = 500,\
               horizon = 2.2 * 3600, time_per_demand_unit = 2*60, speed = 1.34, VehicleCapacity = 999999,\
               blockOverhead = 2 * 60, street_crossing_penalty = 10, \
               distance_constraint = int(1609.344 * 12), blockSizeX = int(0.3048 * 600), blockSizeY = int(0.3048 * 600) ,\
               distanceCrossingPenalty = False, start = 0):    
    noEmps = start
    solByCar = None
    while solByCar is None and noEmps < 50:
        try:
            noEmps += 1
            print("trying # of employees : " + str(noEmps))
            solByCar, assignment = parktimize(locations, demands, start_times, end_times, depot, time_per_car_unit, labs, cars,\
               street_name, street_side, noEmps, search_time_limit,\
               horizon, time_per_demand_unit, speed, VehicleCapacity,\
               blockOverhead, street_crossing_penalty, \
               distance_constraint, blockSizeX, blockSizeY,\
               distanceCrossingPenalty )
        except:
             pass
    return solByCar, noEmps

def dataExport(data, nClusters, fileName):
    kData = data
    time_per_ticket = 2*60
    bid = []
    time = []
    personID = 1
    people = []
    clus = []
    origin = []
    ro = []
    travTime = []
    blockCheckTime = []
    ticketWritingTime = []
    carCheckTime = []
    tickets = []
    crossings = []
    xTime = []
    dist = []

    for k in range(nClusters + 1):
        try:
            for person in kData[k]['solution']:
                o = []
                for p in person[0]:
                    if p.startswith("starting"):
                        o.append("True")
                    else:
                        o.append("False")
                origin.extend(o)
                rr = range(len(person[0]))
                ro.extend(rr)
                bid.extend(person[0])
                time.extend(person[2])
                travTime.extend(person[3])
                blockCheckTime.extend(person[6])
                crossings.extend(person[7])
                ticketWritingTime.extend(person[4])
                carCheckTime.extend(person[5])
                tickets.extend([x / time_per_ticket for x in person[4]])
                xTime.extend(person[8])
                dist.extend(person[9])
                pp = [personID] * len(person[0])
                people.extend(pp)
                personID += 1
                clusta = [k] * len(person[0])
                clus.extend(clusta)
        except:
            print("skipping {} cluster.. there was a problem".format(k))
            pass
    now = datetime.datetime.now()
    finalDFDict = {'origin_flg': origin, 'Cluster ID': clus, 'Route ID': people, \
                   'Block ID': bid, 'Expected Time': time, "Route ID": people, "RouteOrder": ro, \
                  'travel time': travTime, 'block check time': blockCheckTime, 'ticket writing time': ticketWritingTime,\
                  'car check time': carCheckTime, 'total tickets': tickets, 'street crossings' : crossings, \
                  'crossing time': xTime, 'distance': dist}


    finalData = pd.DataFrame.from_dict(finalDFDict)


    filename = os.path.join("output", "routeFile" + fileName + now.strftime("%Y-%m-%d %H:%M") + ".csv")

    finalData.to_csv(filename)
