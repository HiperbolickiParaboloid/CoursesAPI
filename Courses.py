from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import helpers
import pymongo
import os
from werkzeug.utils import secure_filename
from flask_jwt import JWT, jwt_required, current_identity


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
            },
            "image":{
                "bsonType": "string",
                "description": "must be a string and is not required"
            }
          }
      }
    }

if not "courses" in mydb.list_collection_names():
    mycol_courses = mydb.create_collection("courses", validator = req)
    mycol_courses.create_index("name", unique=True)
else:
    mycol_courses = mydb["courses"]
mycol_teachers = mydb["teachers"]

class Image(Resource):      #upload pictures (files) via Postman
    
    @jwt_required()
    def post(self):
        try:
            f = request.files["file"]
            filename = secure_filename(f.filename)
            path = os.path.dirname(os.path.abspath(__file__))
            f.save(os.path.join(path, "static/images", filename))
            return "File successfully saved."
        except Exception as e:
            return {"error": str(e)}, 400

class Course(Resource):

    @jwt_required()
    def get(self, name):        #returns course for specified name
        try:
            course = list(mycol_courses.find({"name": name}))
            if len(course) > 0:
                return dumps(course), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400

    @jwt_required()
    def post(self, name):       #posts new course
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            teacher_id = current_teacher.get("_id")
            request_data = request.get_json()
            new_course = {
                "name": request_data["name"],
                "price": request_data["price"],
                "image": "/images/default.jpg",
                "quantity": 0,
                "teacher": teacher_id
            }
            if "description" in request_data.keys():
                new_course.update({"description": request_data["description"]})
            if "image" in request_data.keys():
                new_course.update({"image": request_data["image"]})
            if "quantity" in request_data.keys():
                new_course.update({"quantity": request_data["quantity"]})
            mycol_courses.insert_one(new_course)
            current_course = mycol_courses.find_one({"name": request_data["name"]})
            course_id = current_course.get("_id")
            updated_course_list = current_teacher.get("course")
            updated_course_list.append(course_id)
            mycol_teachers.update_one({"_id": teacher_id}, {"$set": {"course": updated_course_list}})
            return dumps(new_course), 201
        except Exception as e:
            return {"error": str(e)}, 400        

    @jwt_required()
    def put(self, name):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            teacher_id = current_teacher.get("_id")
            request_data = request.get_json()
            course = mycol_courses.find_one({"name": name})
            if not course:
                new_course = {
                "name": request_data["name"],
                "price": request_data["price"],
                "description": "No description.",
                "image": "/images/default.jpg",
                "quantity": 0,
                "teacher": teacher_id
                }
                if "description" in request_data.keys():
                    new_course.update({"description": request_data["description"]})
                if "image" in request_data.keys():
                    new_course.update({"image": request_data["image"]})
                if "quantity" in request_data.keys():
                    new_course.update({"quantity": request_data["quantity"]})
                mycol_courses.insert_one(new_course)
                current_course = mycol_courses.find_one({"name": request_data["name"]})
                course_id = current_course.get("_id")
                updated_course_list = current_teacher.get("course")
                updated_course_list.append(course_id)
                mycol_teachers.update_one({"_id": teacher_id}, {"$set": {"course": updated_course_list}})
                return dumps(new_course), 201
            else:
                course_id = course.get("teacher")
                if teacher_id != course_id:
                    return {"message": "You can edit only your courses. Please verify your credentials, or course name."}, 404
                else:
                    if request_data.get("name"):
                        new_name = request_data.get("name")
                    else:
                        new_name = course.get("name")
                    if request_data.get("price"):
                        new_price = request_data.get("price")
                    else:
                        new_price = course.get("price")
                    if request_data.get("description"):
                        new_description = request_data.get("descrtiption")
                    else:
                        new_description = course.get("description")
                    if request_data.get("image"):
                        new_image = request_data.get("image")
                    else:
                        new_image = course.get("image")
                    if request_data.get("quantity"):
                        new_quantity = request_data.get("quantity")
                    else:
                        new_quantity = course.get("quantity")
                    new_course = {
                        "name": new_name,
                        "price": new_price,
                        "description": new_description,
                        "image": new_image,
                        "quantity": new_quantity,
                        "teacher": teacher_id
                        }
                    mycol_courses.update_one({"name": name}, {"$set": new_course})
                    return {"message": "Updated"}, 200
        except Exception as e:
            return {"error": str(e)}, 400                 

    @jwt_required()
    def delete(self, name):
        try:
            course = mycol_courses.find_one({"name": name})
            if not course:
                return {"message": "Course with this name not found."}, 404
            else:
                current_teacher = mycol_teachers.find_one({"username": current_identity.username})
                teacher_id_ver = current_teacher.get("_id")
                course_id_ver = course.get("teacher")
                if teacher_id_ver != course_id_ver:
                    return {"message": "You can edit only your courses. Please verify your credentials, or course name."}, 404
                else:
                    teacher_id =  course.get("teacher")
                    teacher = mycol_teachers.find_one({"_id": teacher_id})
                    courses_list = teacher.get("course")
                    course_id = course.get("_id")
                    courses_list.remove(course_id)
                    mycol_teachers.find_one_and_update({"_id": teacher_id}, {"$set": {"course": courses_list}})
                    mycol_courses.find_one_and_delete({"name": name})
                    return {"message": "Course has been deleted."}, 200                    
        except Exception as e:
            return {"error": str(e)}, 400

class CoursesList(Resource):        #returns whole list of courses

    @jwt_required()
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

    @jwt_required()
    def get(self, _id):
        try:
            course = list(mycol_courses.find({"_id": ObjectId(_id)}))
            if len(course) > 0:
                return dumps(course), 200
            else:
                return None, 404
        except Exception as e:
            return {"error": str(e)}, 400

    @jwt_required()
    def delete(self, _id):
        try:
                course = mycol_courses.find_one({"_id": ObjectId(_id)})
                if not course:
                    return {"message": "Course with this ID not found."}, 404
                else:
                    current_teacher = mycol_teachers.find_one({"username": current_identity.username})
                    teacher_id = current_teacher.get("_id")
                    course_id = course.get("teacher")
                    if teacher_id != course_id:
                        return {"message": "You can edit only your courses. Please verify your credentials, or course ID."}, 404
                    else:
                        mycol_courses.find_one_and_delete({"_id": ObjectId(_id)})
                        return {"message": "Course deleted."}, 200
        except Exception as e:
            return {"error": str(e)}, 400

    @jwt_required()
    def put(self, _id):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            teacher_id = current_teacher.get("_id")
            course = mycol_courses.find_one({"_id": ObjectId(_id)})
            course_id = course.get("teacher")
            request_data = request.get_json()
            if course:
                if teacher_id != course_id:
                    return {"message": "You can edit only your courses. Please verify your credentials, or course ID."}, 404
                else:
                    if request_data.get("name"):
                        new_name = request_data.get("name")
                    else:
                        new_name = course.get("name")
                    if request_data.get("price"):
                        new_price = request_data.get("price")
                    else:
                        new_price = course.get("price")
                    if request_data.get("description"):
                        new_description = request_data.get("descrtiption")
                    else:
                        new_description = course.get("description")
                    if request_data.get("image"):
                        new_image = request_data.get("image")
                    else:
                        new_image = course.get("image")
                    if request_data.get("quantity"):
                        new_quantity = request_data.get("quantity")
                    else:
                        new_quantity = course.get("quantity")
                    new_course = {
                        "name": new_name,
                        "price": new_price,
                        "description": new_description,
                        "image": new_image,
                        "quantity": new_quantity,
                        "teacher": teacher_id
                        }
                    mycol_courses.update_one({"_id": ObjectId(_id)}, {"$set": new_course})
                    return {"message": "Selected course has been updated."}, 200
            else:
                return {"message": "Course with this ID not found."}, 404       #can not insert new course by id, it's senseless, than just returns simple message
        except Exception as e:
            return {"error": str(e)}, 400

class CourseNUM(Resource):      #returns number of students for specified course

    @jwt_required()
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

    @jwt_required()
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
    
    @jwt_required()
    def put(self, _id):
        try:
            course = mycol_courses.find_one({"_id": ObjectId(_id)})
            if not course:
                return {"message": "Course with this ID not found."}, 404
            else:
                current_teacher = mycol_teachers.find_one({"username": current_identity.username})
                teacher_id = current_teacher.get("_id")
                course_id = course.get("teacher")
                if teacher_id != course_id:
                    return {"message": "You can edit only your courses. Please verify your credentials, or course ID."}, 404
                else:
                    mycol_courses.update_one({"_id": ObjectId(_id)}, {"$set": {"quantity": (course["quantity"]+1)}})
                    return {"message": "Updated quantity for the selected course."}, 200
        except Exception as e:
            return {"error": str(e)}, 400

class CourseDEC(Resource):      #decreses field "quantity" by one, for specified course
    
    @jwt_required()
    def put(self, _id):
        try:
            course = mycol_courses.find_one({"_id": ObjectId(_id)})
            if not course:
                return {"message": "Course with this ID not found."}, 404
            else:
                current_teacher = mycol_teachers.find_one({"username": current_identity.username})
                teacher_id = current_teacher.get("_id")
                course_id = course.get("teacher")
                if teacher_id != course_id:
                    return {"message": "You can edit only your courses. Please verify your credentials, or course ID."}, 404
                else:
                    mycol_courses.update_one({"_id": ObjectId(_id)}, {"$set": {"quantity": (course["quantity"]-1)}})
                    return {"message": "Updated quantity for the selected course."}, 200
        except Exception as e:
            return {"error": str(e)}, 400