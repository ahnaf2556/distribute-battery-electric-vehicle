from source.simulateOrder.populateData import *
from source.processData.processData import *

hourly_link_speed = {}
hourly_link_count = {}

def processHourlyData():
    print("Process speeds......")
    global hourly_link_speed, hourly_link_count
    
    for index, row in traffic.iterrows():
        if (row.begin_node_id, row.end_node_id) in node_to_link:
            temp_link = node_to_link[(row.begin_node_id, row.end_node_id)][0]
            hour = int(row['datetime'].split(' ')[1].split(':')[0])

            if (temp_link, hour) not in hourly_link_speed:
                hourly_link_speed[(temp_link, hour)] = 0
                hourly_link_count[(temp_link, hour)] = 0

            # hourly_link_speed[(temp_link, hour)] += (node_to_link[(row.begin_node_id, row.end_node_id)][1]/row.travel_time)
            hourly_link_speed[(temp_link, hour)] += (row.travel_time * row.num_trips)
            hourly_link_count[(temp_link, hour)] += row.num_trips

    for key in hourly_link_speed.keys():
        hourly_link_speed[key] = hourly_link_speed[key] / hourly_link_count[key]