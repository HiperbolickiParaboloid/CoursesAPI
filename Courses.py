from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import helpers
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CoursesAPI"]
mycol_courses = mydb["courses"]
#mycol_teachers = mydb["teachers"]

class Course(Resource):

    def get(self, name):        #returns course for specified name
        try:
            course = list(mycol_courses.find({"name": name}))
            if len(course) > 0:
                return dumps(course), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400


    def post(self, name):       #posts new course
        try:
            request_data = request.get_json()
            new_course = {
                "name": helpers.set_name(request_data["name"]),
                "description": helpers.set_description(request_data["description"]),
                "price": helpers.set_price(request_data["price"]),
                "quantity": helpers.set_quantity(request_data["quantity"])
            }
            if new_course["name"] == False:
                return {"error": "Wrong name!"}, 404
            elif new_course["description"] == False:
                return {"error": "Wrong description!"}, 404
            elif new_course["price"] == False:
                return {"error": "Wrong price!"}, 404
            elif new_course["quantity"] == False:
                return {"error": "Wrong quantity!"}, 404
            else:
                mycol_courses.insert_one(new_course)
                return dumps(new_course), 201
        except Exception as e:
            return {"error": str(e)}, 400

class CoursesList(Resource):        #returns whole list of courses

    def get(self):
        try:
            courses = list(mycol_courses.find())
            if courses:
                return dumps(courses), 200
            else:
                return None, 404 
        except Exception as e:
            return dumps({"error": str(e)}), 400

class CourseID(Resource):       #returns course for specified id

    def get(self, _id):
        try:
            course = list(mycol_courses.find({"_id": ObjectId(_id)}))
            if len(course) > 0:
                return dumps(course), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400

class CourseNUM(Resource):      #returns number of students for specified course

    def get(self, _id):
        try:
            course = list(mycol_courses.find({"_id": ObjectId(_id)}))
            if len(course) > 0:
                return dumps(course[0]["quantity"]), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400

class CoursesLimit(Resource):       #returns list of courses using query

    def get(self):
        try:
            limit = int(request.args.get('limit'))
            offset = int(request.args.get('offset'))
            courses = list(mycol_courses.find().limit(limit).skip(offset))
            if courses:
                return dumps(courses), 200
            else:
                return None, 404 
        except Exception as e:
            return dumps({"error": str(e)}), 400

class CourseINC(Resource):      #increses field "quantity" by one, for specified course (supscription)
    def put(self, _id):
        try:
            course = list(mycol_courses.find({"_id": ObjectId(_id)}))
            if len(course) > 0:
                quantity = int(course[0]["quantity"])
                new_quantity = str(quantity+1)
                mycol_courses.update_one({"_id": ObjectId(_id)}, {"$set": {"quantity": new_quantity}})
                return {"message": "Updated"}, 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400

class CourseDEC(Resource):      #decreses field "quantity" by one, for specified course
    def put(self, _id):
        try:
            course = list(mycol_courses.find({"_id": ObjectId(_id)}))
            if len(course) > 0:
                quantity = int(course[0]["quantity"])
                new_quantity = str(quantity-1)
                mycol_courses.update_one({"_id": ObjectId(_id)}, {"$set": {"quantity": new_quantity}})
                return {"message": "Updated"}, 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400