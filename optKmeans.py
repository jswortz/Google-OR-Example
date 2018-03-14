from sklearn.cluster import KMeans
from scipy.cluster.vq import vq
from sklearn.metrics import pairwise_distances_argmin_min
import numpy as np

def kMeans(locations, labels, cars, demands, nClusters):
    seed = 1234
    X = np.array(zip([x[0] for x in locations],[x[1] for x in locations]))

    nClusters = 30
    kmeans = KMeans(n_clusters=nClusters, random_state=seed)
    kmeans.fit(X)

    kPred = kmeans.predict(X)

   

    centers = kmeans.cluster_centers_

    # print np.average(np.bincount(idx))
    closest, _ = pairwise_distances_argmin_min(centers, X)
    centerTerminals = [labels[c] for c in closest]
    kData ={key: {'center': None, 'locations': None, 'labels' : None, 'cars' : None, 'demand' : None,\
                  'centralTerm': None} for key in range(nClusters)}
    # kData = {}
    for k in range(nClusters):
        klocations = []
        klabels = []
        kcars = []
        kdemand = []
        for loc, lab, car, dem, kp in zip(locations, labels, cars, demands, kPred):
            if kp == k:
                klocations.append(loc)
                klabels.append(lab)
                kcars.append(car)
                kdemand.append(dem)
    #     print(len(klocations))
        kData[k].update({'center':centers[k], 'locations': klocations, 'labels': klabels, 'cars' : kcars, 'demand': kdemand,'centralTerm' : centerTerminals[k]})
            
    return kData