from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo
import funct
import valid
import Courses

def add_course(request_data):
    id_course=[]
    id_teacher=list(mycol_teachers.find({"username": username}, {"_id":1 }))[0]

    for elem in request_data["course"]:
        elem.update("id_techer":id_teacher)
        id_course.append(Courses.Course.post(elem))
                
    mycol_teachers.update_one({"username":username},{"$set": {"course": id_course})

if __name__ == "__main__":
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["CoursesAPI"]

if not "teachers" in mydb.list_collection_names():
    mycol = mydb.create_collection("teachers", validator = valid.schema)
    mycol.create_index("username", unique=True)
else:
    mycol_teachers = mydb["teachers"]

class Teacher(Resource):
    def get(self, username):
        try:
            teacher = list(mycol_courses.find({"username": username}))
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
                "username": username,
                "password": funct.encoding(request_data["password"]),
                "email"   : request_data["email"],
                "role"    : request_data["role"]
            }
            mycol_teachers.insert_one(new_teacher)

            if "course" in request_data.keys():
                add_course(request_data)
                    
            return dumps(new_teacher), 201
        except Exception as e:
            return {"error": str(e)}, 400


    def delete(self, username):
        try:
            teacher= mycol.find_one_and_delete({"username": username})
            if teacher:
                return {"message": "Teacher deleted."}, 200
            else:
                return {"message": "Teacher with this name not found."}, 404
        except Exception as e:
            return {"error": str(e)}, 400

    def put(self, username):
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
                return {"message": "Teacher updated"}, 200
                if request_data["course"]:
                    if teacher["course"]:
                        for course_id in teacher["course"]:
                            Courses.Course.delete_by_id(course_id)
                    
                    add_course(request_data)
                return dumps(updated_teacher), 201
    
    class TeachersList(Resource):
    def get(self):
        try:
            teachers= list(mycol.find())
            if teachers:
                return dumps(teachers), 200
            else:
                return {"message": "No teachers found."}, 404
        except Exception as e:
            return dumps({"error": str(e)})

