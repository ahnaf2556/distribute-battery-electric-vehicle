from source.processData.processData import *
import heapq


class distanceService(object):
    node_to_node_distance = {}

    def __init__(self):
        self.node_to_node_distance = {}

    def calculate_distance(self, node):
        self.node_to_node_distance[(node, node)] = 0
        queue = []
        queue.append((0, node))
        heapq.heapify(queue)

        while(len(queue)):
            total_dis, node_u = heapq.heappop(queue)

            # if stack == 2000:
            #   continue

            for link in start_node_to_link[node_u]:
                node_v = link_start_node[link]

                if node_v == node_u:
                    node_v = link_end_node[link]
                
                dis = link_distance[link]

                if (node, node_v) not in self.node_to_node_distance or self.node_to_node_distance[(node, node_v)] > self.node_to_node_distance[(node, node_u)] + dis:
                    self.node_to_node_distance[(node, node_v)] = self.node_to_node_distance[(node, node_u)] + dis
                    heapq.heappush(queue,(self.node_to_node_distance[(node, node_v)], node_v))