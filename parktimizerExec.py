from lib.CSVImporter import getcsv
from lib.clustaFun import clusters
from lib.dataPrep import getData, empUp, dataExport
from lib.parktimizer import parktimize
import os

################################################
###NOTE THAT INPUT FILES MUST BE IN THE ./data FOLDER AND OUTPUT WILL GO INTO ./output
################################################


def main(inputFile = 'Input_Model_040318_newMC2_noDriving_CLZy_remSEblocks.csv', outputName = "generic", nClusters = 55, \
         time_horizon = 2.2 * 3600, time_per_ticket = 2*60, walk_speed = 1.34, term_check = 120, cross_time = 60, \
         walkingCap = int(1609.344 *12), blockX = int(0.3048 * 660), blockY = int(0.3048 * 330), \
            MCtime_horizon = 2.2 * 3600, MCtime_per_ticket = 2*60, MCwalk_speed = 1.34, MCterm_check = 120\
         , MCcross_time = 10, MCwalkingCap = int(1609.344 *12), \
            MCblockX = int(0.3048 * 600), MCblockY = int(0.3048 * 300), search_time = 500):
    
    
    input_file = inputFile

    locations, labels, demands, cars, megaCluster, streetSide, streetName, \
    start_times, end_times, carTime = getcsv(input_file)
    
    kData = clusters(nClusters, locations, labels, demands, cars, megaCluster,streetName, streetSide, carTime, nClusters)
    
    ###NEIGHBORHOOD RUN
    for k in range(nClusters):
    # k = nClusters
        print("Starting cluster {} of {}".format(k, nClusters))
        loc, dem, ca, labs, depot, start_times, end_times, street_name, street_side, cct = getData(k, kData, nClusters)
        solution, noEmps = empUp(loc, dem, start_times, end_times, depot, cct, labs, ca, street_name, \
                                 street_side, horizon = time_horizon, time_per_demand_unit = time_per_ticket, speed=walk_speed,\
                                blockOverhead = term_check, street_crossing_penalty = cross_time, \
                                 distance_constraint = walkingCap, blockSizeX = blockX, blockSizeY = blockY,\
                                 search_time_limit=search_time)
        
        kData[k].update({'solution': solution, 'empsNeeded': noEmps})

    print("RUNNING MEGACLUSTER")
    ###MEGACLUSTER RUN   
    k = nClusters
    loc, dem, ca, labs, depot, start_times, end_times, street_name, street_side, cct = getData(k, kData, nClusters)
    solution, noEmps = empUp(loc, dem, start_times, end_times, depot, cct, labs, ca, street_name, \
                                 street_side, horizon = MCtime_horizon, time_per_demand_unit = MCtime_per_ticket,\
                             speed=MCwalk_speed,\
                                blockOverhead = MCterm_check, street_crossing_penalty = MCcross_time, \
                                 distance_constraint = MCwalkingCap, blockSizeX = MCblockX, blockSizeY = MCblockY, \
                            search_time_limit = search_time)
    kData[k].update({'solution': solution, 'empsNeeded': noEmps})
    
    fileName = outputName + "_{}_".format(nClusters)
    
    dataExport(kData, nClusters, fileName)
    
    print(fileName + " solution file exported. Check output folder")

###Now run main
if __name__ == "__main__":
    main()
    