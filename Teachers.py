from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo
import funct
import Courses
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CoursesAPI"]

'''
schem = {
      "$jsonSchema": {
          "bsonType": "object",
          "required": [ "username", "password", "email", "role"],
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
               "maxLength": 25,
               
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
               "maximum": 1
            },
            "course": {
                "bsonType": "array",
                "description": "must be array and not required"
            }
          }
      }
    }
'''


if not "teachers" in mydb.list_collection_names():
    mycol_teachers = mydb.create_collection("teachers")
    mycol_teachers.create_index("username", unique=True)
    
else:
    mycol_teachers = mydb["teachers"]

def add_course(request_data):
    id_course=[]
    
    id_teacher=list((list(mycol_teachers.find({"username": request_data["username"]}, {"_id":1 }))[0]).values())[0]
    call=Courses.Course()
   
    for elem in request_data["course"]:
        
        elem.update({"id_teacher":id_teacher})
        
        id_course.append(call.post(elem))
        

    myquery = {"username": request_data["username"]}
    newvalues = {"$set": {"course": id_course}}          
    mycol_teachers.update_one(myquery, newvalues)

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
            teacher= mycol_teachers.find_one_and_delete({"username": username})
            if teacher:
                return {"message": "Teacher deleted."}, 200
            else:
                return {"message": "Teacher with this name not found."}, 404
        except Exception as e:
            return {"error": str(e)}, 400

    def put(self, username):
        try:
            request_data = request.get_json()
            
            teacher = list(mycol_teachers.find({"username": username}))
            
            name = username    #because line 86
            updated_teacher = {
            "username":request_data["username"] if request_data["username"] else teacher["username"] ,
            "password":funct.encoding(request_data["password"])if request_data["password"] else teacher["password"] ,
            "email":request_data["email"] if request_data["email"] else teacher["email"] ,
            "role":request_data["role"] if request_data["role"] else teacher["role"]
            }
           
            if not teacher:
                mycol_teachers.insert_one(updated_teacher)
                if "course" in request_data.keys():
                    add_course(request_data)
                return dumps(updated_teacher), 201
            else:
                
                mycol_teachers.update_one({"username": name}, {"$set": updated_teacher})  #searching by old username for old courses
                if "course" in request_data.keys():
                    if "course" in teacher[0].keys():
                        for course_id in teacher["course"]:
                            
                            call=Courses.Course()
                            call.delete_by_id(course_id)
                            
                    add_course(request_data)                
                return dumps(updated_teacher), 201
        except Exception as e:
            return {"error": str(e)}, 400
    
class TeachersList(Resource):

    def get(self):
        try:
            teachers= list(mycol_teachers.find())
            if teachers:
                return dumps(teachers), 200
            else:
                return {"message": "No teachers found."}, 404
        except Exception as e:
            return dumps({"error": str(e)})


