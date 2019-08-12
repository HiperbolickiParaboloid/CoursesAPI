from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo
import funct, security
import Courses

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CoursesAPI"]

req = {
      "$jsonSchema": {
          "bsonType": "object",
          "required": ["username", "password", "email", "role"],
          "properties": {
            "username": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 3,
               "maxLength": 20
            },
            "password": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 5,
               "maxLength": 25
            },
            "email": {
               "bsonType": "string",
               "description": "must be a string and is required",
               "minLength": 5,
               "maxLength": 35
            },
            "role": {
               "bsonType": "int",
               "description": "must be a number and is required",
               "minimum": 0,
               "maximum": 2
            },
            "course": {
                "bsonType": "array",
                "description": "must be an array and not required"
            }
        }
    }
}


if not "teachers" in mydb.list_collection_names():
    mycol_teachers = mydb.create_collection("teachers", validator = req)
    mycol_teachers.create_index("username", unique=True)
else:
    mycol_teachers = mydb["teachers"]
mycol_courses = mydb["courses"]

class Teacher(Resource):
    
    def get(self, username):
        try:
            teacher = list(mycol_teachers.find({"username": username}))
            if len(teacher) > 0:
                return dumps(teacher), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400
    
    def post(self, username):       
        try:
            request_data = request.get_json()
            new_teacher = {
                "username": request_data["username"],
                "password": request_data["password"],
                "email": request_data["email"],
                "role": request_data["role"],
                "course": []
            }
            if "course" in request_data.keys():
                new_teacher.update({"course": request_data["course"]})
            mycol_teachers.insert_one(new_teacher)
            #security.users.append(security.User((len(security.users) + 1), new_teacher["username"], new_teacher["password"]))
            return dumps(new_teacher), 201
        except Exception as e:
            return {"error": str(e)}, 400

    def delete(self, username):
        try:
            teacher = mycol_teachers.find_one({"username": username})
            if not teacher:
                return {"message": "Teacher with this name not found."}, 404
            else:
                courses = (mycol_teachers.find_one({"username": username}))
                courses_to_delete = courses.get("course")
                for i in courses_to_delete:
                    mycol_courses.find_one_and_delete({"_id": i})
                mycol_teachers.find_one_and_delete({"username": username})
                return {"message": "Teacher deleted."}, 200
        except Exception as e:
            return {"error": str(e)}, 400

'''    def put(self, username):
        try:
            request_data = request.get_json()
            teacher = mycol_teachers.find({"username": username})
            name = username    #because line 86
            updated_teacher = {
            "username":request_data["username"] if request_data["username"] else teacher["username"] ,
            "password":funct.encoding(request_data["password"])if request_data["password"] else teacher["password"] ,
            "email":request_data["email"] if request_data["email"] else teacher["email"] ,
            "role":request_data["role"] if request_data["role"] else teacher["role"]
            }
            if not teacher:
                mycol_teachers.insert_one(updated_teacher)
                if request_data["course"]:
                    add_course(request_data)
                return dumps(updated_teacher), 201
            else:
                mycol_teachers.update_one({"username": name}, {"$set": updated_teacher})  #searching by old username for old courses
                if request_data["course"]:
                    if teacher["course"]:
                        for course_id in teacher["course"]:
                            Courses.Course.delete_by_id(course_id)
                    add_course(request_data)                
                return dumps(updated_teacher), 201
        except Exception as e:
            return {"error": str(e)}, 400
 '''   
class TeachersList(Resource):

    def get(self):
        try:
            teachers = list(mycol_teachers.find())
            if teachers:
                return dumps(teachers), 200
            else:
                return {"message": "No teachers found."}, 404
        except Exception as e:
            return dumps({"error": str(e)})


class TeacherSalary(Resource):
    
    def get(self, username):
        try:
            salary = 0
            teacher = mycol_teachers.find_one({"username": username})
            if teacher:
                courses = teacher.get("course")
                for i in courses:
                    course = mycol_courses.find_one({"_id": ObjectId(i)})
                    price = float(course.get("price"))
                    quantity = float(course.get("quantity"))
                    salary = salary + (price * quantity)
                return dumps(salary), 200
            else:
                return {"message": "No teachers found."}, 404
        except Exception as e:
            return dumps({"error": str(e)})
