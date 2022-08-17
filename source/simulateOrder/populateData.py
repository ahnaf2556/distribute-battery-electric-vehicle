import pandas as pd
import os


link = pd.read_csv('assets/links.csv')
node = pd.read_csv('assets/nodes.csv')
traffic = pd.read_csv('assets/data2013_1st_week.csv')
long_island_solar = pd.read_csv('assets/long-island_2013_january_week1.csv')
brentwood_solar = pd.read_csv('assets/brentwood_2013_Jan_week1.csv')
median_serial = {}
node_to_median = {}
medians: any

latlongs = []

def populateLatLong(number_of_medians):
    print("Populate lat longs......")
    global latlongs, node_to_median

    for index in range(number_of_medians):
        dir_name = 'assets/'
        temp = pd.read_csv(os.path.join(dir_name, 'latlongs' + str(index+1) + '.csv'))
        latlongs.append(temp)
        latlongs[index].columns = ['sl.', 'node_id', 'xcoord', 'ycoord']

        for i, row in latlongs[index].iterrows():
            node_to_median[row.node_id] = index
        

def updateMedians():
    print("Update medians......")
    global medians, median_serial

    medians = pd.read_csv('assets/medians.csv')
    medians.columns = ['sl.', 'node_id', 'xcoord', 'ycoord']
    
    for index, row in medians.iterrows():
        median_serial[row.node_id] = index