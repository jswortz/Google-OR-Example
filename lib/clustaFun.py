import pandas as pd
from sklearn.cluster import KMeans
from scipy.cluster.vq import vq
from sklearn.metrics import pairwise_distances_argmin_min
import numpy as np

def clusters(nClusters, locations, labels, cars, demands, megaCluster, streetName, streetSide, carTime, seed=1234):
    seed = seed

    fullData = {'locations': locations, 'labels': labels, 'cars': cars, 'demands': demands\
            , 'megacluster': megaCluster, 'streetName' : streetName, \
            'streetSide': streetSide, 'carCheckTime': carTime}

    fullDS = pd.DataFrame.from_dict(fullData)


    kData ={key: {'center': None, 'locations': None, 'labels' : None, 'cars' : None, 'demand' : None,\
                  'centralTerm': None} for key in range(nClusters)}

    #now load up the megacluster first:

    megaData = fullDS.loc[fullDS['megacluster'] == 1]
    nonmegaData = fullDS.loc[fullDS['megacluster'] == 0]

    megaDict = megaData.to_dict(orient='list')
    nonMegaDict = nonmegaData.to_dict(orient='list')

    X = np.array(zip([x[0] for x in nonMegaDict['locations']],[x[1] for x in nonMegaDict['locations']]))


    kmeans = KMeans(n_clusters=nClusters, random_state=seed)
    kmeans.fit(X)

    kPred = kmeans.predict(X)


    centers = kmeans.cluster_centers_

    # print np.average(np.bincount(idx))
    closest, _ = pairwise_distances_argmin_min(centers, X)
    centerTerminals = [nonMegaDict['labels'][c] for c in closest]
    # kData ={key: {'center': None, 'locations': None, 'labels' : None, 'cars' : None, 'demand' : None,\
    #               'centralTerm': None} for key in range(nClusters)}
    # kData = {}
    for k in range(nClusters):
        klocations = []
        klabels = []
        kcars = []
        kdemand = []
        kstreet = []
        kside = []
        kctime = []
        for loc, lab, car, dem, kp, sn, sd, cct in zip(nonMegaDict['locations'], nonMegaDict['labels'],\
                                          nonMegaDict['cars'], nonMegaDict['demands'], kPred,\
                                         nonMegaDict['streetName'], nonMegaDict['streetSide'], nonMegaDict['carCheckTime']):
            if kp == k:
                klocations.append(loc)
                klabels.append(lab)
                kcars.append(car)
                kdemand.append(dem)
                kstreet.append(sn)
                kside.append(sd)
                kctime.append(cct)

        kData[k].update({'center': centers[k], 'locations': klocations, 'labels': klabels, \
                        'cars': kcars, 'demand': kdemand, 'centralTerm': centerTerminals[k], \
                        'streetName': kstreet, 'streetSide': kside, 'carCheckTime': kctime})
    #     print(len(klocations))


    stuffThatIsDrivingMeNutsWPython = {'center': [448476.6, 4636929], 'locations': megaDict['locations'], \
                     'labels': megaDict['labels'], 'cars' : megaDict['cars'], 'demand': megaDict['demands'],\
                                 'centralTerm' : "LAZ GARAGE", 'streetName': megaDict['streetName'],\
                                       'streetSide' : megaDict['streetSide'], 'carCheckTime': megaDict['carCheckTime']}
    kData.update({nClusters  : stuffThatIsDrivingMeNutsWPython})
    return(kData)
