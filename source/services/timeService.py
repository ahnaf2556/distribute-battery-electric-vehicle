from source.processData.processData import *
from source.processData.processHourlyData import *
import heapq


class timeService(object):
    node_to_node_time = {}
    
    def __init__(self):
        self.node_to_node_time = {}

    def calculate_time(self, node, destination, hour, memoization = False):
        time_data = {}

        self.node_to_node_time[(node, node, hour)] = 0
        time_data[(node, node, hour)] = 0
        queue = []
        queue.append((0, node))
        heapq.heapify(queue)

        while(len(queue)):
            total_time, node_u = heapq.heappop(queue)

            if node_u == destination:
                self.node_to_node_time[(node, destination, hour)] = time_data[(node, destination, hour)]
                return

            if node_u not in start_node_to_link:
                continue

            for link in start_node_to_link[node_u]:
                node_v = link_end_node[link]

                if node_v == node_u:
                    node_v = link_start_node[link]
                
                time = 50
                
                if (link, hour) in hourly_link_speed:
                    time = hourly_link_speed[(link, hour)]

                if (node, node_v, hour) not in time_data or time_data[(node, node_v, hour)] > time_data[(node, node_u, hour)] + time:
                    time_data[(node, node_v, hour)] = time_data[(node, node_u, hour)] + time

                    if memoization:
                        self.node_to_node_time[(node, node_v, hour)] = time_data[(node, node_u, hour)] + time

                    heapq.heappush(queue, (time_data[(node, node_v, hour)], node_v))