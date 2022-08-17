from source.simulateOrder.populateData import *

list_of_nodes = []
node_to_latlong = {}
latlong_to_node = {}

def processNodes(notAllowed = []):
    print("Process nodes......")
    global list_of_nodes, node_to_latlong, latlong_to_node

    for index, row in node.iterrows():
        # if row.node_id not in notAllowed:
        # if row.xcoord < -73.84320065 and row.xcoord > -74.00470975 and row.ycoord < 40.89300485 and row.ycoord > 40.652341199999995 and row.node_id not in notAllowed:
        if row.xcoord < -73.8081681 and row.xcoord > -74.040936 and row.ycoord < 40.89300485 and row.node_id not in notAllowed:
            list_of_nodes.append(row.node_id)
            node_to_latlong[row.node_id] = (row.xcoord, row.ycoord)
            latlong_to_node[(row.xcoord, row.ycoord)] = row.node_id
