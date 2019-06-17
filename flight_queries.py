import pymongo
import random
from bson import ObjectId
from flask import Flask, render_template, jsonify, request
from collections import Counter
from random import randint
from datetime import datetime, timedelta
app=Flask(__name__)

connection = pymongo.MongoClient("localhost", 27017)

database = connection['my_database']
collection = database['flight_booking']
collection_1 = database['booking_info']
print("Database connected")
#qyery 1

print("1. Flight whose model number is 7001\n")
def get_single_data(model_no):

    flight_info = collection.find_one({'model':model_no})
    return flight_info

flight_data = get_single_data("7001")
print(flight_data)

#query 2
print("\n\n\n2.All the Flights whose capacity are greater than 40 and above.\n")

def get_multiple_data():

    flight_info = collection.find()
    for flight in flight_info:
        if int(flight["capacity"]) >= 40 :
            print(flight)

get_multiple_data()

#query 3
print("\n\n\n3.Total flights whose service happend 5 or more months back.\n")

months = 5
before_5_months = datetime.today() - timedelta(days=30*months)
print(before_5_months)

flights_before_5_months = collection.find({"service_record.date_of_service":{"$lte":before_5_months}})

for flight in flights_before_5_months:
    print(flight)

#query 4

print("\n\n\n4. Which flight had serviced more?\n")

counter_list=[]
flight_id=[]
max_services={}
flight_info = collection.find()
for flight in flight_info:
    flight_id.append(flight["_id"])
    length=len(flight["service_record"])
    counter_list.append(length)
    max_services=dict(zip(flight_id, counter_list))

max_value = [(value, key) for key, value in max_services.items()]
print(max(max_value)[1])

#query 5

print("\n\n\n5. Which Team Serviced most lousy?\n")

flights_info = collection.find()


min = datetime.now() - datetime.strptime("18-05-1997", "%d-%m-%Y")
lousy_team = ""

for flight in flights_info:
    service = flight["service_record"]
    for i in range(len(service)-1):
        time_diff = abs(service[i+1]["date_of_service"] - service[i]["date_of_service"])
        if time_diff < min:
            min = time_diff
            lousy_team = service[i]["service_by"]

print(" The most lousy service has provided by \"" + lousy_team + "\" whose service last only for " + str(min.days) + " days in flight "+ flight["_id"]+ "-"+flight["Name"]+".")
