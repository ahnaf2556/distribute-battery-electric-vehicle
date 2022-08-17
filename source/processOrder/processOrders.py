import math
from source.services.timeService import timeService
from source.services.service import *
from source.processData.latLongBoundary import *
from source.simulateOrder.populateData import *


class orderProcessing(object):
    def __init__(
      self, 
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
    ):
        self.order_data = []
        self.time_to_order = {}

        self.reload_data = {}
        self.charge_complete = {}
        self.car_reach_farm = {}

        self.data_of_car = []

        self.number_of_medians = number_of_medians
        self.number_of_cars = number_of_cars_in_hub
        self.hub_car_capacity = hub_car_capacity

        self.initial_charged_battery_in_hub = initial_charged_battery_in_hub
        self.battery_in_hub = []
        self.uncharged_battery_in_hub = []

        self.hourToCover = hourToCover
        self.ordersPerDay = ordersPerDay

        self.total_rejected = 0
        self.rejected_for_battery = []
        self.battery_asked = 0
        self.battery_supplied = 0

        self.en_route = []

        self.number_of_solar_farm = len(solar_farm_nodes)           # we only have data for 2 solar farms
        self.solar_farm_nodes = solar_farm_nodes
        self.initial_charged_battery_in_farm = initial_charged_battery_in_farm
        self.charged_battery_in_farm = []

        self.number_of_solar_farm_cars = number_of_cars_in_farm
        self.order_time_per_node = {}
        self.farm_car_data = []
        self.farm_car_capacity = farm_car_capacity

        self.farm_data = [{}, {}]

        self.charging_battery = []
        self.charging_battery.append({})
        self.charging_battery.append({})
        self.charging_battery[0][0.0] = initial_zero_charged_battery_in_farm
        self.charging_battery[1][0.0] = initial_zero_charged_battery_in_farm

        self.uncharged_battery_in_farm = []
        self.uncharged_battery_in_farm.append(initial_zero_charged_battery_in_farm)
        self.uncharged_battery_in_farm.append(initial_zero_charged_battery_in_farm)


        self.waitingQueue = []


        self.rejectOrderData = []
        self.confirmOrderData = []
        self.carData = []
        self.hubData = []
        self.farmData = []

        
        self.timeServiceRef = timeService()

    
    
    def populateData(self):
        print("Populate order data......")
        [self.order_data, self.time_to_order] = generate_order_data(self.ordersPerDay, list_of_nodes, self.order_data, self.time_to_order)           # O(nlogn)

        for i in range(self.number_of_medians):                         # O(number of medians * car in hub)
            self.data_of_car.append({})
            self.order_time_per_node[i] = []
            self.battery_in_hub.append(self.initial_charged_battery_in_hub)
            self.waitingQueue.append(0)
            self.uncharged_battery_in_hub.append(0)
            self.rejected_for_battery.append(0)
            self.en_route.append(0)

            for index in range(self.number_of_cars):
                self.data_of_car[i][index] = (medians.iloc[i].node_id.astype('int64'), 0, self.hub_car_capacity, 0)        #(current location of car, time upto which committed, battery in car)

        for i in range(self.number_of_solar_farm):                      # O(number of farm * car in farm)
            self.farm_car_data.append({})
            self.charged_battery_in_farm.append(self.initial_charged_battery_in_farm)

            for index in range(self.number_of_cars):
                self.farm_car_data[i][index] = (self.solar_farm_nodes[i], 0, 0)        #(current location of car, time upto which committed, battery in car)


        for index, row in long_island_solar.iterrows():                 # O(number of solar farm data)
            time = (row.Day - 1)*86400 + row.Hour*3600 + row.Minute*60
            self.farm_data[0][int(time)] = math.floor(row["NO. of Batteries charged AC"])

        for index, row in brentwood_solar.iterrows():                   # O(number of solar farm data)
            time = (row.Day - 1)*86400 + row.Hour*3600 + row.Minute*60
            self.farm_data[1][int(time)] = math.floor(row["NO. of Batteries charged AC"])

        print("Order Data READY!!!!!!")
    
    
    
    def number_of_orders_in_last_hour(self, node, time_of_check):
        order = 0

        for index in range(len(self.order_time_per_node[node]) - 1, -1, -1):
            if self.order_time_per_node[node][index] < time_of_check - 3600:
                break
            
            order += 1

        return order



    def prioritizeWaitingHubs(self, time):
        priorityList = []

        for index in range(self.number_of_medians):
            priorityList.append((self.priority((index, self.waitingQueue[index]), time), index))

        priorityList.sort(reverse=True)                                 # O(nlogn), n = number of medians
        
        for item in priorityList:
            cluster_number = item[1]
            
            self.requestFarmBattery(time, cluster_number)                # O(number of farms * number of farm car * nlogn), n = number of nodes



    def priority(self, item, time):
        return (self.number_of_orders_in_last_hour(item[0], time) * (time - item[1]))
    
    

    def chargeBatteryInfarm(self, time, farm_index, fullChargeTime = 7.5):
        if time in self.farm_data[farm_index]:
            battery_capacity = self.farm_data[farm_index][time]

            if battery_capacity > 0:
                keys = list(self.charging_battery[farm_index].keys())
                keys.sort(reverse=True)

                for key in keys:
                    if not battery_capacity:
                        break

                    if self.charging_battery[farm_index][key] > 0:
                        init = self.charging_battery[farm_index][key]
                        self.charging_battery[farm_index][key] = max(init - battery_capacity, 0)
                        battery_capacity -= (init - self.charging_battery[farm_index][key])

                        if key + 0.5 == fullChargeTime:
                            self.charged_battery_in_farm[farm_index] += (init - self.charging_battery[farm_index][key])
                            self.uncharged_battery_in_farm[farm_index] -= (init - self.charging_battery[farm_index][key])
                            self.farmData.append((farm_index, second_to_time(time), init - self.charging_battery[farm_index][key], self.uncharged_battery_in_farm[farm_index]))
                            # print("$$$$$$$$$ Battery added in farm", farm_index, ":", (init - self.charging_battery[farm_index][key]), " at ", second_to_time(time), "$$$$$$$$$")
                        else:
                            if (key + 0.5) not in self.charging_battery[farm_index]:
                                self.charging_battery[farm_index][key + 0.5] = 0

                            self.charging_battery[farm_index][key + 0.5] += (init - self.charging_battery[farm_index][key])


    
    def requestFarmBattery(self, time, cluster_number):
        hour = time // 3600

        lastHourOrders = self.number_of_orders_in_last_hour(cluster_number, time)

        if self.charged_battery_in_farm[0] < self.hourToCover * lastHourOrders and self.charged_battery_in_farm[1] < self.hourToCover * lastHourOrders:
            return

        if self.battery_in_hub[cluster_number] + self.en_route[cluster_number] < self.hourToCover * lastHourOrders:
            # print("Need Battery in hub: ", cluster_number, " at: ", second_to_time(time), " Already there:", self.battery_in_hub[cluster_number], " en route:", self.en_route[cluster_number], " Needed:", self.hourToCover * lastHourOrders)
            self.battery_asked += 1
            minimum_time = 1e9
            farm_index = -1
            car_index = -1

            for i in range(self.number_of_solar_farm):                                      # O(number of farms * number of farm car * nlogn), n = number of nodes
                if self.charged_battery_in_farm[i] < self.hourToCover * lastHourOrders:
                    continue
                
                farm_node = self.solar_farm_nodes[i]

                for car in self.farm_car_data[i].keys():                                    # O(number of farm car * nlogn), n = number of nodes
                    location = self.farm_car_data[i][car][0]
                    last_time = max(time, self.farm_car_data[i][car][1])
                    hour = last_time // 3600
                    battery = self.farm_car_data[i][car][2]

                    if battery + self.hourToCover * lastHourOrders > self.farm_car_capacity:
                        continue

                    if location == medians.iloc[cluster_number].node_id.astype('int64') and last_time < minimum_time:
                        minimum_time = last_time
                        farm_index = i
                        car_index = car
                        continue
                
                    if (location, medians.iloc[cluster_number].node_id.astype('int64'), hour%24) not in self.timeServiceRef.node_to_node_time:
                        destination = medians.iloc[cluster_number].node_id.astype('int64')

                        if location == farm_node:
                            destination = -1
                        
                        self.timeServiceRef.calculate_time(location, destination, hour%24, location == farm_node)                       # O(nlogn), n = number of nodes
                        
                    if self.timeServiceRef.node_to_node_time[(location, medians.iloc[cluster_number].node_id.astype('int64'), hour%24)] + last_time < minimum_time:
                        minimum_time = self.timeServiceRef.node_to_node_time[(location, medians.iloc[cluster_number].node_id.astype('int64'), hour%24)] + last_time
                        farm_index = i
                        car_index = car
                    
            if farm_index != -1:
                self.en_route[cluster_number] += self.hourToCover * lastHourOrders
                self.waitingQueue[cluster_number] = time

                last_time = max(time, self.farm_car_data[farm_index][car_index][1])

                delivery_time = round(minimum_time + 10*60)          # 10*60 is misc. time

                if minimum_time == last_time:
                    delivery_time = minimum_time
                    
                self.charged_battery_in_farm[farm_index] -= self.hourToCover * lastHourOrders

                battery = self.farm_car_data[farm_index][car_index][2]
                self.farm_car_data[farm_index][car_index] = (medians.iloc[cluster_number].node_id.astype('int64'), minimum_time + 10*60, battery + self.hourToCover * lastHourOrders)

                if delivery_time not in self.reload_data:
                    self.reload_data[delivery_time] = []

                self.reload_data[delivery_time].append((cluster_number, self.hourToCover * lastHourOrders, farm_index, car_index))

                self.hubData.append((cluster_number, second_to_time(time), self.hourToCover * lastHourOrders, self.battery_in_hub[cluster_number], self.en_route[cluster_number], farm_index, car_index, second_to_time(delivery_time)))
                # print("Asked for battery -> cluster number:", cluster_number, "  Current Time:", second_to_time(time), "  Delivery Time:", second_to_time(delivery_time), "  Farm:", farm_index, " Car:", car_index)

            else:
                self.hubData.append((cluster_number, second_to_time(time), self.hourToCover * lastHourOrders, self.battery_in_hub[cluster_number], self.en_route[cluster_number], -1, -1, -1))
                # print("Sorry sent to waiting list, cluster number:", cluster_number)

    
    
    def supplyBatteryToHub(self, time):
        if time in self.reload_data:                                                                        
            for reload_data_element in self.reload_data[time]:                                              # O(number of battery request * nlogn), n = number of nodes
                hour = time // 3600

                location = medians.iloc[reload_data_element[0]].node_id.astype('int64')
                farm_index = reload_data_element[2]
                car_index = reload_data_element[3]

                self.en_route[reload_data_element[0]] -= reload_data_element[1]
                self.battery_in_hub[reload_data_element[0]] += reload_data_element[1]

                if location != self.farm_car_data[farm_index][car_index][0]:
                    continue
                
                if (location, self.solar_farm_nodes[farm_index], hour%24) not in self.timeServiceRef.node_to_node_time:
                    self.timeServiceRef.calculate_time(location, -1, hour%24, True)                          # O(nlogn), n = number of nodes

                time_to_reach_farm = round(self.timeServiceRef.node_to_node_time[(location, self.solar_farm_nodes[farm_index], hour%24)])

                if round(time + time_to_reach_farm) not in self.car_reach_farm:
                    self.car_reach_farm[round(time + time_to_reach_farm)] = []

                self.car_reach_farm[round(time + time_to_reach_farm)].append((farm_index, car_index))

                # print("++++++++++++++ Battry added to Hub: ", reload_data_element[0], " from Farm:", farm_index, " at: ", second_to_time(time), "++++++++++++++")
                self.battery_supplied += 1

    
    
    def batteryToFarm(self, time):
        if time in self.car_reach_farm:
            for car_data in self.car_reach_farm[time]:                                              # O(number of battery request)
                farm_index = car_data[0]
                car_index = car_data[1]

                self.charging_battery[farm_index][0.0] += self.farm_car_data[farm_index][car_index][2]
                self.uncharged_battery_in_farm[farm_index] += self.farm_car_data[farm_index][car_index][2]
                self.farm_car_data[farm_index][car_index] = (self.solar_farm_nodes[farm_index], 0, 0)


    
    def carToHub(self, time, car_index, cluster_number):
        location = self.data_of_car[cluster_number][car_index][0]
        last_time = max(time, self.data_of_car[cluster_number][car_index][1])
        hour = last_time // 3600
        initialTime = self.data_of_car[cluster_number][car_index][3]

        if(isinstance(hour, float)):
            hour = int(hour)
        if (location, medians.iloc[cluster_number].node_id.astype('int64'), hour%24) not in self.timeServiceRef.node_to_node_time:
            self.timeServiceRef.calculate_time(location, medians.iloc[cluster_number].node_id.astype('int64'), hour%24)

        time_when_reach = last_time + self.timeServiceRef.node_to_node_time[(location, medians.iloc[cluster_number].node_id.astype('int64'), hour%24)]
        battery_in_car = min(10, self.battery_in_hub[cluster_number])
        self.battery_in_hub[cluster_number] = max(0, self.battery_in_hub[cluster_number] - battery_in_car)
        self.data_of_car[cluster_number][car_index] = (medians.iloc[cluster_number].node_id.astype('int64'), time_when_reach + 20*60, battery_in_car, time)

        self.carData.append((cluster_number, car_index, second_to_time(time_when_reach), second_to_time(time_when_reach - initialTime)))


    
    def processOrder(self, time):
        if time in self.time_to_order:
            order_nodes = self.time_to_order[time]

            for order_node in order_nodes:                                                                          # O (number of orders * number of hub cars * nlogn), n = number of nodes
                waiting_time = random.randint(10*60, 2*60*60)

                if order_node not in node_to_median:
                    continue

                cluster_number = node_to_median[order_node]
                self.order_time_per_node[cluster_number].append(time)

                # print(">>>>>>>> Order recieved -> Cluster number:", cluster_number, " Time:", second_to_time(time))

                minimum_time = 1e9
                car_index = -1
                one_with_battery = False
                miniumOfTimeReach = 1e9

                for car in self.data_of_car[cluster_number].keys():                                                 # O (number of hub cars * nlogn), n = number of nodes
                    time_to_reach = -1
                    location = self.data_of_car[cluster_number][car][0]
                    last_time = max(time, self.data_of_car[cluster_number][car][1])
                    hour = last_time // 3600
                    battery = self.data_of_car[cluster_number][car][2]

                    if(isinstance(hour, float)):
                        hour = int(hour)

                    if battery == 0:
                        if self.battery_in_hub[cluster_number] > 0:
                            battery = min(10, self.battery_in_hub[cluster_number])
                            self.battery_in_hub[cluster_number] = max(0, self.battery_in_hub[cluster_number] - battery)
                            self.data_of_car[cluster_number][car] =  (location, self.data_of_car[cluster_number][car][1], battery, time)
                        else:
                            # print("----- zero battery in car", car)
                            continue

                    one_with_battery = True

                    if (location, order_node, hour%24) not in self.timeServiceRef.node_to_node_time:
                        if location == medians.iloc[cluster_number].node_id.astype('int64'):
                            self.timeServiceRef.calculate_time(location, -1, hour%24, True)                         # O(nlogn), n = number of nodes
                        else:
                            self.timeServiceRef.calculate_time(location, order_node, hour%24)                       # O(nlogn), n = number of nodes

                    time_when_reach = last_time + self.timeServiceRef.node_to_node_time[(location, order_node, hour%24)]
                    miniumOfTimeReach = min(miniumOfTimeReach, time_when_reach)

                    # print("Car", car, "possible delivery time:", second_to_time(time_when_reach))

                    if time_when_reach <= time + waiting_time and time_when_reach < minimum_time:
                        minimum_time = time_when_reach
                        car_index = car

                if car_index != -1:
                    # print("Order confirmed -> cluster number:", cluster_number, "  Current Time:", second_to_time(time), "  Delivery Time:", second_to_time(minimum_time), "  Car:", car_index)
                    last_time = max(time, self.data_of_car[cluster_number][car_index][1])
                    battery = self.data_of_car[cluster_number][car_index][2]
                    initialCarTime = self.data_of_car[cluster_number][car_index][3]

                    if location == medians.iloc[cluster_number].node_id.astype('int64'):
                        initialCarTime = time

                    self.data_of_car[cluster_number][car_index] = (order_node, minimum_time + 10*60, battery - 1, initialCarTime)           # 10*60 is misc. time

                    if (battery == 1):
                        self.carToHub(time, car_index, cluster_number)

                    self.confirmOrderData.append((order_node, cluster_number, second_to_time(time), second_to_time(waiting_time), second_to_time(minimum_time), second_to_time(minimum_time - last_time), location, car_index, battery))
                else:
                    self.total_rejected += 1
                    # print("X X X X X X X X X X X --- Order rejected -> cluster number:", cluster_number, "--- X X X X X X X X X X X")
                    reason = "Time constraint"
                    if one_with_battery == False:
                        reason = "Battery constraint"
                        self.rejected_for_battery[cluster_number] += 1
                        # print("No battery in possible cars for hub: ", cluster_number)
                    
                    self.rejectOrderData.append((order_node, cluster_number, second_to_time(time), second_to_time(time+waiting_time), second_to_time(miniumOfTimeReach), reason))