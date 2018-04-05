import csv
import numpy as np
import os

def getcsv(filename):
    demands = []
    labels = []
    locations = []
    firstLine = True
    limiter = 9999999
    counter = 0
    cars = []
    megaCluster = []
    streetSide = []
    streetName = []
    carTime = []
    carTime = []

    dataFolder = "data"
    with open(os.path.join(dataFolder, filename), 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if counter < limiter: #this is just a cap to QA the model with fewer locations
                if firstLine:
                    firstLine = False
                else:
                    latLong = []
                    carTime.append(float(row[28]))
                    latLong.append(float(row[23]))
                    latLong.append(float(row[24]))
                    locations.append(latLong)
                    labels.append(row[1])
                    demands.append(float(row[26]))
                    cars.append(float(row[27]))
                    megaCluster.append(int(row[25]))
                    streetSide.append(row[14])
                    streetName.append(row[18].split(" ",1)[1])
                    counter+=1


    start_times =  [0] * len(demands)
    end_times = [3600 * 24] * len(start_times)
    return locations, labels, demands, cars, megaCluster, streetSide, streetName, start_times, end_times, carTime