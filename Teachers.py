from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
from validator import valid
from helpers import line 
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#$PUSH------------------------------PUT
mydb = myclient["CoursesAPI"]

if not "teachers" in mydb.list_collection_names():
    mycol_teachers = mydb.create_collection("teachers")

else:
    mycol_teachers = mydb["teachers"]

mycol_teachers.create_index("username", unique=True)

def eml_check(email):
    if 5<=len(email)<=35 :
        for element in mycol_teachers.find({},{"_id": 0 , "email": 1 }):
            if element == email:
                return False
    return True

class Teacher(Resource):
    def get(self, username):
        try:
            teacher = list(mycol_teachers.find({"username": username}))
            if teacher:
                return dumps(teacher), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400


    def post(self, username): 
        try:
            request_data = request.get_json() 
            mistake_list = []
            if valid(request_data):
                new_teacher = {
                    "username": request_data["username"],
                    "password": request_data["password"],
                    "email": request_data["email"],
                    "role": request_data["role"]
                }
                mycol_teachers.insert_one(new_teacher)

                if "course" in request_data.keys():
                    teacher_id = list(mycol_teachers.find({"username": request_data["username"]}, {"_id":1}))[0]["_id"]
                    for elem in request_data["course"]:
                        elem.update({"teachers_id" : teacher_id})
                        help = line().post(elem)
                        if type(help) != tuple:
                            course_id = {"course_id":help}
                            mycol_teachers.update_one({ "username": request_data["username"] }, { "$set": course_id })
                        else:
                            mistake_list.append(elem)
                if mistake_list:
                    mistake = "Teacher is posted but folowing courses already exist!  "  + str(mistake_list)
                    return mistake, 406
                else:
                    return dumps(new_teacher), 201
            else:
                return dumps("Document failed validation!")
        except Exception as e:
            return {"error": str(e)}, 400
