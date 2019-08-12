from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo
import funct, security
import Courses
from flask_jwt import JWT, jwt_required, current_identity

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
    
    @jwt_required()
    def get(self, username):
        try:
            teacher = list(mycol_teachers.find({"username": username}))
            if len(teacher) > 0:
                return dumps(teacher), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400
    
    @jwt_required()
    def post(self, username):       
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            if current_identity.username == "admin":
                request_data = request.get_json()
                new_teacher = {
                    "username": request_data["username"],
                    "password": request_data["password"],
                    "email": request_data["email"],
                    "role": request_data["role"],
                    "course": []
                }
                mycol_teachers.insert_one(new_teacher)
                return dumps(new_teacher), 201
            elif current_teacher.get("role") == 1:
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
                return dumps(new_teacher), 201
            else:
                return {"error": "You are not authorized to create a new teacher. You must have an admin status."}, 401
        except Exception as e:
            return {"error": str(e)}, 400

    @jwt_required()
    def delete(self, username):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            if current_identity.username == "admin":
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
            elif current_teacher.get("role") == 1:
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
            else:
                return {"error": "You are not authorized to delete a teacher. You must have an admin status."}, 401
        except Exception as e:
            return {"error": str(e)}, 400

    @jwt_required()
    def put(self, username):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            if current_identity.username == "admin":
                request_data = request.get_json()
                teacher = mycol_teachers.find_one({"username": username})
                if not teacher:
                    new_teacher = {
                        "username": request_data["username"],
                        "password": request_data["password"],
                        "email": request_data["email"],
                        "role": request_data["role"],
                        "course": []
                    }
                    mycol_teachers.insert_one(new_teacher)
                    return dumps(new_teacher), 201
                else:
                    if request_data.get("username"):
                        new_username = request_data.get("username")
                    else:
                        new_username = teacher.get("username")
                    if request_data.get("password"):
                        new_password = request_data.get("password")
                    else:
                        new_password = teacher.get("password")
                    if request_data.get("email"):
                        new_email = request_data.get("email")
                    else:
                        new_email = teacher.get("email")
                    if request_data.get("role") in [0,1]:
                        new_role = request_data.get("role")
                    else:
                        new_role = teacher.get("role")
                    new_course = teacher.get("course")
                    new_teacher = {
                        "username": new_username,
                        "password": new_password,
                        "email": new_email,
                        "role": new_role,
                        "course": new_course
                        }
                    mycol_teachers.update_one({"username": username}, {"$set": new_teacher})
                    return {"message": "Updated teacher"}, 200
            elif current_teacher.get("role") == 1:
                request_data = request.get_json()
                teacher = mycol_teachers.find_one({"username": username})
                if not teacher:
                    new_teacher = {
                        "username": request_data["username"],
                        "password": request_data["password"],
                        "email": request_data["email"],
                        "role": request_data["role"],
                        "course": []
                    }
                    mycol_teachers.insert_one(new_teacher)
                    return dumps(new_teacher), 201
                else:
                    if request_data.get("username"):
                        new_username = request_data.get("username")
                    else:
                        new_username = teacher.get("username")
                    if request_data.get("password"):
                        new_password = request_data.get("password")
                    else:
                        new_password = teacher.get("password")
                    if request_data.get("email"):
                        new_email = request_data.get("email")
                    else:
                        new_email = teacher.get("email")
                    if request_data.get("role") in [0,1]:
                        new_role = request_data.get("role")
                    else:
                       new_role = teacher.get("role")
                    print (request_data.get("role"))
                    print (new_role)
                    new_course = teacher.get("course")
                    new_teacher = {
                        "username": new_username,
                        "password": new_password,
                        "email": new_email,
                        "role": new_role,
                        "course": new_course
                        }
                    mycol_teachers.update_one({"username": username}, {"$set": new_teacher})
                    return {"message": "Updated"}, 200
            else:
                return {"error": "You are not authorized to edit a teacher. You must have an admin status."}, 401
        except Exception as e:
            return {"error": str(e)}, 400

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
