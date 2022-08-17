from source.processData.latLongBoundary import *
from source.simulateOrder.populateData import *


node_to_link = {}
start_node_to_link = {}
end_node_to_link = {}
link_start_node = {}
link_end_node = {}
link_distance = {}

def processLinks():
    print("Process links......")
    global node_to_link, start_node_to_link, end_node_to_link, link_start_node, link_end_node, link_distance
    
    for index, row in link.iterrows():
        if row.begin_node_id in list_of_nodes and row.end_node_id in list_of_nodes:
            node_to_link[(row.begin_node_id, row.end_node_id)] = (row.link_id, row.street_length)
            link_start_node[row.link_id] = row.begin_node_id
            link_end_node[row.link_id] = row.end_node_id
            link_distance[row.link_id] = row.street_length

            if row.begin_node_id not in start_node_to_link:
                start_node_to_link[row.begin_node_id] = []

            if row.end_node_id not in start_node_to_link:
                start_node_to_link[row.end_node_id] = []

            start_node_to_link[row.begin_node_id].append(row.link_id)
            start_node_to_link[row.end_node_id].append(row.link_id)
