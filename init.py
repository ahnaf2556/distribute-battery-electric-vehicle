from source.processData.processHourlyData import *
from source.simulateOrder.populateData import *
from source.processData.latLongBoundary import *
from source.processData.processData import *
from source.services.service import *

# Variables to change for comparisons

number_of_medians = 20
number_of_cars_in_hub = 5
number_of_cars_in_farm = 10
hub_car_capacity = 5
farm_car_capacity = 50
initial_charged_battery_in_hub = 100
initial_charged_battery_in_farm = 100
initial_zero_charged_battery_in_farm = 100
days_of_simulation = 2
hourToCover = 2
ordersPerDay = 1000

solar_farm_latLong = [(40.85, -72.86), (40.77, -73.26)]             # (40.85, -72.86) -> Long Island Solar (40.77, -73.26) -> Brentwood Solar





processNodes()          # O(total number of nodes)
processLinks()          # O(number of links)

initalMedians = generate_medians(list_of_nodes, number_of_medians)              # O(nlogn) of the number of samples -> can be improved for the logn, and more randomized data

# not necessary to change unless 100 iterations are completed, 
# or RAM cannot handle, in that case use the previously calculated medians as new medians
number_of_maximum_iterations = 100

from source.clusterData.kMeans import kMeans

kCluster = kMeans(initalMedians)               

print("Start clustering")

kCluster.kClusterData(number_of_maximum_iterations)                 # O(number of iterations * number of medians * total number of nodes)
kCluster.save_data()

kCluster.distanceServiceRef.node_to_node_distance = {}

populateLatLong(number_of_medians)          # O(number of median * number of node in each cluster) = O(total number of nodes)
updateMedians()                             # O(number of medians)
processHourlyData()                          # O(traffic data available) -> O(n)

solar_farm_nodes = []

for item in solar_farm_latLong:             # O(number of farms * total number of nodes)
    solar_farm_nodes.append(findNearestNode(latlong_to_node, item[0], item[1]))             # O(total number of nodes)

from source.simulateOrder.basicSimulation import basicSimulation

basicSimulation.simulate(
    days_of_simulation,
    number_of_medians, 
    number_of_cars_in_hub, 
    number_of_cars_in_farm, 
    hub_car_capacity, 
    farm_car_capacity,
    initial_charged_battery_in_hub, 
    initial_charged_battery_in_farm, 
    initial_zero_charged_battery_in_farm,
    hourToCover,
    solar_farm_nodes,
    ordersPerDay
)
