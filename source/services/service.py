import random
import math


def generate_medians(list_of_nodes, number_of_medians):
  return random.sample(list_of_nodes, number_of_medians)



def generate_time():
  partOfDay = random.randint(0,10)

  if partOfDay < 2:
    return random.randint(0, 7*60*60)
  elif partOfDay > 7:
    return random.randint(20*60*60 + 1, 24*60*60 - 1)
  else:
    return random.randint(7*60*60 + 1, 20*60*60 - 1)



def generate_order_data(number_of_order, list_of_nodes, order_data, time_to_order, day = 0):
  temp_data = random.sample(list_of_nodes, number_of_order)

  for item in temp_data:
    timeOfOrder = generate_time() + day*86400
    order_data.append({item, timeOfOrder})
    
    if timeOfOrder not in time_to_order:
      time_to_order[timeOfOrder] = []
    
    time_to_order[timeOfOrder].append(item)

  return [order_data, time_to_order]



def second_to_time(time):
  second = time % 60

  if(isinstance(second, float)):
    second = int(second)

  minute = (time // 60) % 60

  if(isinstance(minute, float)):
    minute = int(minute)

  hour = (time // 3600) % 24

  if(isinstance(hour, float)):
    hour = int(hour)

  day = (time // 86400)

  if(isinstance(day, float)):
    day = int(day)

  return "Day " + str(day) + " - " + str(hour) + ":" + str(minute) + ":" + str(second)



def findNearestNode(latlong_to_node, ycoord, xcoord):
  diff = 1e9
  node = 0

  for key in latlong_to_node.keys():
    euclideanDis = math.sqrt(math.pow((xcoord - key[0]), 2) + math.pow((ycoord - key[1]), 2))

    if euclideanDis < diff:
      diff = euclideanDis
      node = latlong_to_node[key]
                    
  return node