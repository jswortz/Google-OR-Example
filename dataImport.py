import csv
def dataImport(location = 'Copy of blocks_com_031318.csv', latLoc = 13, longLoc = 14, labelLoc = 0, demLoc = 17, \
              carLoc = 16):
    demands = []
    labels = []
    locations = []
    firstLine = True
    limiter = 9999999
    counter = 0
    cars = []
    with open(location, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if counter < limiter: #this is just a cap to QA the model with fewer locations
                if firstLine:
                    firstLine = False
                else:
                    latLong = []
                    latLong.append(float(row[latLoc]))
                    latLong.append(float(row[longLoc]))
                    locations.append(latLong)
                    labels.append(row[labelLoc])
                    demands.append(float(row[demLoc]))
                    cars.append(float(row[carLoc]))
                    counter+=1


    start_times =  [0] * len(demands)
    end_times = [3600 * 24] * len(start_times)
    return demands, labels, locations, cars, start_times, end_times