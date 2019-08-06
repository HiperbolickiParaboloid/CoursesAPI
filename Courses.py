from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import helpers
import pymongo
import inspect
if __name__ == "__main__":
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["CoursesAPI"]

req = {
      "$jsonSchema": {
          "bsonType": "object",
          "required": ["name", "price"],
          "properties": {
            "name": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 3,
               "maxLength": 15
            },
            "price": {
               "bsonType": "double",
               "description": "must be a number and is required",
               "minimum": 1,
               "maximum": 10000
            },
            "description": {
               "bsonType": "string",
               "description": "must be a string and is not required",
               "minLength": 10,
               "maxLength": 150
            },
            "quantity": {
               "bsonType": "int",
               "description": "must be a number and is not required",
               "minLength": 0,
               "maxLength": 50
            }
          }
      }
    }

if not "courses" in mydb.list_collection_names():
    mycol = mydb.create_collection("courses", validator = req)
    mycol.create_index("name", unique=True)
else:
    mycol_courses = mydb["courses"]

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
            teacher__caller=0
            for elem in inspect.stack():
                if "Teachers" in elem: 
                    teacher_caller=1
                    break

            if teacher__caller==0:
                request_data = request.get_json()
            else:
                request_data=name


            new_course = {
                "name": request_data["name"],
                "price": request_data["price"],
            }
            if "description" in request_data.keys():
                new_course.update({"description": helpers.set_description(request_data["description"])})
            if "quantity" in request_data.keys():
                new_course.update({"quantity": helpers.set_quantity(request_data["quantity"])})
            mycol_courses.insert_one(new_course)

            
            if teacher__caller==0:
                return dumps(new_course), 201

            else:
                mycol_courses.update_one({"name":request_data["name"]},{"$set": {"teacher": request_data["id_teacher"]})
                return mycol_courses.find({"name":request_data["name"]})['_id']
            

            
        except Exception as e:
            return {"error": str(e)}, 400

#delete by id for teachers put method
    def delete_by_id(self, _id):
        try:
            course = mycol.find_one_and_delete({"_id": _id})
            if course:
                return {"message": "Course deleted."}, 200
            else:
                return {"message": "Course with this name not found."}, 404
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
                mycol_courses.update_one({"_id": ObjectId(_id)}, {"$set": {"quantity": (course[0]["quantity"]+1)}})
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
                mycol_courses.update_one({"_id": ObjectId(_id)}, {"$set": {"quantity": (course[0]["quantity"]-1)}})
                return {"message": "Updated"}, 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400