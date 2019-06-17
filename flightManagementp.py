import pymongo
import random
from bson import ObjectId
from flask import Flask, render_template, jsonify, request
from random import randint
from datetime import datetime
app=Flask(__name__)

connection = pymongo.MongoClient("localhost", 27017)

database = connection['my_database']
collection = database['flight_booking']
collection_1 = database['booking_info']
print("Database connected")


def insert_data(data):

    document = collection.insert_one(data)
    return document.inserted_id


def update_or_create(document_id, data):

    # TO AVOID DUPLICATES - THIS WILL CREATE NEW DOCUMENT IF SAME ID NOT EXIST
    document = collection.update_one({'_id': ObjectId(document_id)}, {"$set": data}, upsert=True)
    return document.acknowledged


def get_single_data(document_id):

    data = collection.find_one({'_id':document_id})
    return data


def get_multiple_data():
    """
    get document data by document ID
    :return:
    """
    data = collection.find()
    return list(data)


def update_existing(document_id, data):
    """
    Update existing document data by document ID
    :param document_id:
    :param data:
    :return:
    """
    document = collection.update_one({'_id':document_id}, {"$set": data})
    return document.acknowledged


def remove_data(document_id):
    document = collection.delete_one({'_id':document_id})
    return document.acknowledged


# CLOSE DATABASE
connection.close()
#data={"_id":"1004", "Name":"Airbus","model":"7001", "Airline":"IndiGo", "capacity":"100", "manufacturing_date":"12/06/2019", "service_record":[{"date_of service":"12/03/2019", "service_by":"team1"}]}
#insert_data(data)

#flask





@app.route('/')
def index():
    return 'wlecome'

@app.route('/flights/',methods=["GET", "POST"])
def get_method():
    if request.method == "GET":
        flight_data=get_multiple_data()
        return jsonify(flight_data)
    if request.method == "POST":


        data=({
            "_id" :request.args["_id"],
            "Name" :request.args["Name"],
            "model" : request.args["model"],
            "Airline" : request.args["Airline"],
            "capacity" :request.args["capacity"],
            "availability":request.args["availability"],
            "manufacturing_date" : request.args["manufacturing_date"],
            "service_record":[]
        })
        insert_data(data)


    return "data updated"

@app.route('/flight/<flight_no>')
def search(flight_no):
    data_one=get_single_data(flight_no)
    print(data_one)
    return jsonify(data_one)

@app.route('/flight/<flight_no>',methods=["PATCH"])
def update(flight_no):
    data = ({"Name": request.args["Name"]})

    data_update=update_existing(flight_no,data)
    print(data_update)
    return jsonify(data_update)

@app.route('/flight/<flight_no>',methods=["DELETE"])
def delete (flight_no):
    data_deleted=remove_data(flight_no)
    print(data_deleted)
    return jsonify(data_deleted)

# flight management

@app.route('/flight/<flight_no>/availability/')
def availability (flight_no):
    data = collection.find_one({'_id': flight_no})
    print(data)
    return jsonify(data["availability"])

@app.route('/flight/<flight_no>/book/',methods=["GET", "POST"])
def book (flight_no):
    booking_id=str(random.randint(1001,10000))
    number_of_seats= request.args["number_of_seats"]

    users_data=({
            "_id":booking_id,
            "Name" :request.args["Name"],
            "e-mail" :request.args["e-mail"],
            "number_of_seats" : request.args["number_of_seats"],
            "phone_number" : request.args["phone_number"]})


    flight_data = collection.find_one({'_id': flight_no})

    #customer_data= collection_1.find_one({'_id': booking_id})
    print(type(number_of_seats))
    print(type(flight_data["availability"]))

    if int(flight_data["availability"]) >= int(number_of_seats):
        booking_data = collection_1.insert_one(users_data)
        flight_data = collection.find_one({'_id': flight_no})
        data={"availability": str(int(flight_data["availability"])-int(request.args["number_of_seats"]))}
        data_update = collection.update_one({'_id':flight_no}, {"$set": data})
        return booking_id
    else:
        return "seat full"


@app.route('/flight/<flight_no>/book/<booking_id>')
def booking_flight (flight_no,booking_id):
    booking_info= collection_1.find_one({'_id': booking_id})
    print(booking_info)
    return jsonify(booking_info)
@app.route('/flight/cancellation/<flight_no>/<booking_id>',methods=["GET", "POST", "PATCH"])
def cancellation (flight_no,booking_id):
    booking_info = collection_1.find_one({'_id': booking_id})
    total_seats=booking_info["number_of_seats"] #10
    flight_data = collection.find_one({'_id': flight_no})
    availability=flight_data["availability"] #90
    number_of_seats = request.args["number_of_seats"] #6  update
    canceled_seats =int(total_seats)-int(number_of_seats) #4
    total_availability = int(availability)+ int(canceled_seats) #94 update
    flight_data={"availability": str(total_availability)}
    flight_data_update = collection.update_one({'_id': flight_no}, {"$set": flight_data})
    booking_data={"number_of_seats": str(number_of_seats)}
    booking_data_update = collection_1.update_one({'_id': booking_id}, {"$set": booking_data})
    return jsonify(booking_data)

@app.route("/service/<flight_no>", methods=["POST"])
def service(flight_no):
    if all(argument in request.args for argument in ["date_of_service","service_by"]):
        service_by = request.args["service_by"]

        date_of_service = datetime.strptime(request.args["date_of_service"], "%d-%m-%Y")


        flight_data = collection.find_one_and_update({"_id":flight_no},{
            "$addToSet":{
                "service_record": {"date_of_service": date_of_service,
                            "service_by": service_by}
            }
        })
        if flight_data:
            return "succesfully data updated"
        else:
            return "please check the flight ID"


    else:
        return "please privide the correct data"






