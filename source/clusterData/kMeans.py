from source.services.distanceService import distanceService
from source.processData.latLongBoundary import *
from source.services.service import *
import pandas as pd

class kMeans(object):
    def __init__(self, medians):
        self.nodeToMedian = {}
        self.medians = medians
        self.distanceServiceRef = distanceService()

    def kClusterData(self, numOfIterations=1000):
        maxIteration = numOfIterations
        changesMade = 1

        while changesMade and numOfIterations:
            print("iteration no.", maxIteration-numOfIterations, " changes made:", changesMade)
            changesMade = 0
            numOfIterations -= 1

            for i in range(len(self.medians)):
                self.distanceServiceRef.calculate_distance(self.medians[i])             # O(number of nodes)

            for node in list_of_nodes:                                                  # O(number of nodes)
                distance_min = 1e9
                currentMedian = -1

                for i in range(len(self.medians)):
                    if (self.medians[i], node) in self.distanceServiceRef.node_to_node_distance and self.distanceServiceRef.node_to_node_distance[(self.medians[i], node)] < distance_min:
                        distance_min = self.distanceServiceRef.node_to_node_distance[(self.medians[i], node)]
                        currentMedian = i
                
                changesMade += 1

                if node in self.nodeToMedian and currentMedian == self.nodeToMedian[node]:
                    changesMade -= 1
                
                self.nodeToMedian[node] = currentMedian
            
            self.medians = self.findMedians(self.medians)                               # O(number of medians * number of nodes)

    def findMedians(self, medians):
        sumsX = []
        sumsY = []
        counts = []

        for i in range(len(medians)):                                                       # O(number of medians)
            sumsX.append(0)
            sumsY.append(0)
            counts.append(0)

        for key in self.nodeToMedian.keys():                                                # O(number of nodes)
            index = self.nodeToMedian[key]

            if index == -1:
                continue

            sumsX[index] += node_to_latlong[key][0]
            sumsY[index] += node_to_latlong[key][1]
            counts[index] += 1

        for i in range(len(medians)):                                                       # O(number of medians * number of nodes)
            xcoord = sumsX[i]/counts[i]
            ycoord = sumsY[i]/counts[i]

            if (xcoord, ycoord) in latlong_to_node:
                medians[i] = latlong_to_node[(xcoord, ycoord)]
            else:
                medians[i] = findNearestNode(latlong_to_node, ycoord, xcoord)               # O(number of nodes)

        return medians

    def save_data(self):
        unclustered = []
        latlongData = []

        for i in range(len(self.medians)):
            latlongData.append([])

        for key in self.nodeToMedian.keys():
            index = self.nodeToMedian[key]
            if index == -1:
                unclustered.append((key, node_to_latlong[key][0], node_to_latlong[key][1]))
            else:
                latlongData[index].append((key, node_to_latlong[key][0], node_to_latlong[key][1]))


        unclustered_df = pd.DataFrame(unclustered)
        latlongDataDf = []

        for i in range(len(self.medians)):
            latlongDataDf.append(pd.DataFrame(latlongData[i]))

        unclustered_df.to_csv('assets/unclustered.csv')

        for i in range(len(self.medians)):
            dir_name = 'assets/'
            latlongDataDf[i].to_csv(os.path.join(dir_name, 'latlongs' + str(i+1) + '.csv'))

        medians_to_df = []

        for key in self.medians:
            medians_to_df.append((key, node_to_latlong[key][0], node_to_latlong[key][1]))

        medians_df = pd.DataFrame(medians_to_df)
        medians_df.to_csv('assets/medians.csv')
