from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo
import funct, security
import Courses
from flask_jwt import JWT, jwt_required, current_identity
from validator import valid
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["CoursesAPI"]



if not "teachers" in mydb.list_collection_names():
    mycol_teachers = mydb.create_collection("teachers")
else:
    mycol_teachers = mydb["teachers"]
mycol_courses = mydb["courses"]
mycol_teachers.create_index("username", unique=True)

def add_course(request_data):
    mistake_list = []
    courses_id=[]
    teachers_id = list(mycol_teachers.find({"username": request_data["username"]}, {"_id":1}))[0]["_id"]
    #teachers_id=list((list(mycol_teachers.find({"username": request_data["username"]}, {"_id":1 }))[0]).values())[0]
    call=Courses.Course()
   
    for elem in request_data["course"]:
        elem.update({"teachers_id" : teachers_id})
        help = call.post(elem)
        mycol_teachers.create_index("username", unique=True)
        if type(help) != tuple:
            courses_id.append(help)
        else:
            mistake_list.append(elem)
    return courses_id, mistake_list

def make_str_dict(request_data):
    course=[]
    for elem in request_data:
        course.append(eval(elem))    
    return course


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
            if current_identity.username == "admin" or current_teacher.get("role") == 1:
                request_data = request.get_json()
                if valid(request_data):
                    new_teacher = {
                        "username": request_data["username"],
                        "password": funct.encoding(request_data["password"]),
                        "email"   : request_data["email"],
                        "role"    : request_data["role"]
                    }
                    mycol_teachers.insert_one(new_teacher)
                    if "course" in request_data.keys():
                        (courses_id, mistake_list) = add_course(request_data)
                        mycol_teachers.update_one({ "username": request_data["username"] }, { "$set": {"courses_id" : courses_id }})   
                        if mistake_list:
                            mistake = "Teacher is posted but folowing courses already exist!  "  + str(mistake_list)
                            return mistake, 406
                        else:
                            return dumps(new_teacher), 201
                    return dumps(new_teacher), 201

            else:
                return {"error": "You are not authorized to create a new teacher. You must have an admin status."}, 401
        except Exception as e:
            return {"error": str(e)}, 400

            
    @jwt_required()
    def delete(self, username):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            if current_identity.username == "admin" or current_teacher.get("role") == 1:
                teacher = mycol_teachers.find_one({"username": username})
                if teacher:
                    if "course" in teacher.keys():
                        for course_id in teacher["course"]:
                            call=Courses.CourseID()
                            call.delete(course_id)
                        teacher= mycol_teachers.find_one_and_delete({"username": username})
                        return {"message": "Teacher (and his courses) deleted."}, 200
                    teacher= mycol_teachers.find_one_and_delete({"username": username})
                    return {"message": "Teacher deleted."}, 200
                else:
                    return {"message": "Teacher with this name not found."}, 404
            
            else:
                return {"error": "You are not authorized to delete a teacher. You must have an admin status."}, 401

        except Exception as e:
            return {"error": str(e)}, 400



    @jwt_required()
    def put(self, username):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            if current_identity.username == "admin" or current_teacher.get("role") == 1:
                teacher = list(mycol_teachers.find({"username": username}))
                parser = reqparse.RequestParser()
                is_required = False
                if not teacher: 
                    is_required = True
                else:
                    teacher = teacher[0]
             
                parser.add_argument("username", type=str, required=is_required)
                parser.add_argument("password", type=str, required=is_required)
                parser.add_argument("email", type=str, required=is_required)
                parser.add_argument("role", type=int, required=is_required)
                parser.add_argument("course", action='append', required= False)
                parser.add_argument("delete_course", type=str, required= False)
                
                request_data = parser.parse_args()    
            
                updated_teacher = {
                "username":request_data["username"] if request_data["username"] else teacher["username"] ,
                "password":request_data["password"] if request_data["password"] else teacher["password"] ,
                "email":request_data["email"] if request_data["email"] else [teacher["email"]] ,
                "role":request_data["role"] if request_data["role"]!=None else teacher["role"]   
                }

                if valid(updated_teacher):
                    updated_teacher["password"] = funct.encoding(request_data["password"])
                     
                    if not teacher:
                        mycol_teachers.insert_one(updated_teacher)
                        course=make_str_dict(request_data["course"])
                        updated_teacher.update({"course":course})
        
                        (courses_id, mistake_list) = add_course(updated_teacher)
                        mycol_teachers.update_one({ "username": request_data["username"] }, { "$set": {"courses_id" : courses_id }})   
                        if mistake_list:
                            mistake = "Teacher is posted but folowing courses already exist!  "  + str(mistake_list)
                            return mistake, 406
                        else:
                            return dumps(updated_teacher    ), 201

                    else:
                        if type(updated_teacher["email"]) == list:
                            updated_teacher["email"] = teacher["email"]
                        mycol_teachers.update_one({"username": username}, {"$set": updated_teacher}) 
                        
                        if request_data["course"]:
                            append_to_course = 0
                            if "courses_id" in teacher.keys(): 
                                if "delete_courses" in request_data.keys():
                                    if request_data["delete_courses"] == "y":
                                        for course_id in teacher["course"]: 
                                            call=Courses.CourseID()
                                            call.delete(course_id)
                                    else:
                                        append_to_course = 1
                                else:
                                    append_to_course = 1     
                            course=make_str_dict(request_data["course"])
                            updated_teacher.update({"course":course})
                            if append_to_course:
                                (courses_id, mistake_list) = add_course(updated_teacher)
                                mycol_teachers.update_one({ "username": updated_teacher["username"] }, { "$set": {"courses_id" : courses_id }})   
                                if mistake_list:
                                    mistake = "Teacher is posted but folowing courses already exist!  "  + str(mistake_list)
                                    return mistake, 406
                                else:
                                    return dumps(updated_teacher), 201
                            else:
                                (courses_id, mistake_list) = add_course(updated_teacher)
                                mycol_teachers.update_one({ "username": updated_teacher["username"] }, { "$push": { "courses_id": { "$each": courses_id } } })   
                                if mistake_list:
                                    mistake = "Teacher is posted but folowing courses already exist!  "  + str(mistake_list)
                                    return mistake, 406
                                else:
                                    return dumps(updated_teacher), 201    
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



class TeacherCourse(Resource):

    def get(self, username, id):
        try:
            teacher = list(mycol_teachers.find_one({"username": username}))
            if teacher:
                teacher = teacher[0]
                course = list(mycol_courses.find({"name": id}))
                if course:
                    course = course[0]
                    teacher["course"] = course
                    return dumps(teacher), 200
                else:
                    teacher.pop("course", None)
                    teacher.pop("password", None)
                    message = str(teacher) + "Teacher exists but course does not!"
                    return dumps(message), 406
            else:
                return {"message": "Teacher not found."}, 404
        except Exception as e:
            return dumps({"error": str(e)})


    def post(self, username, id):
            try:
                current_teacher = mycol_teachers.find_one({"username": current_identity.username})
                if current_identity.username == "admin" or current_teacher.get("role") == 1:
                    teacher = list(mycol_teachers.find_one({"username": username}))
                    course_id = list(mycol_courses.find_one({"_id": id}))
                    if teacher and course_id:
                        teacher = teacher[0]
                        course_teacher = list(mycol_teachers.find({"_id" : 0, "courses_id": {"$elemMatch": id}}))
                        if not course_teacher:
                            if "courses_id" in teacher.keys():
                                mycol_teachers.update_one({ "username": username }, { "$push": { "courses_id": id } }) 
                                return {"message": "Teacher updated!"}, 200  
                            else:
                                mycol_teachers.update_one({ "username": username }, { "$set": { "courses_id": id } })
                                return {"message": "Teacher updated!"}, 200
                        else:
                            return {"error": "Course already has a teacher. You need to use put operation or delete it from current teacher first!"}, 400
                    else:
                        if course_id:
                            return {"error": "Teacher not found!"}, 404
                        elif teacher:
                            return {"error": "Course not found!"}, 404
                        else:
                            return {"error": "teachet and Course not found!"}, 404
                else:
                    return {"error": "You are not authorized to edit a teacher. You must have an admin status."}, 401

            except Exception as e:
                return dumps({"error": str(e)})


    def put(self, username, id):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            if current_identity.username == "admin" or current_teacher.get("role") == 1:
                teacher = list(mycol_teachers.find_one({"username": username}))
                course_id = list(mycol_courses.find_one({"_id": id}))
                if teacher and course_id:
                    teacher = teacher[0]
                    course_teacher = list(mycol_teachers.find({"_id" : 0, "courses_id": {"$elemMatch": id}}))
                    if course_teacher:
                        mycol_teachers.update({}, { "$pull": { "courses_id": id } })
                        mycol_courses.replace_one({"_id": id}, {"teachers_id" : current_teacher.get("_id")})

                       
                    if "courses_id" in teacher.keys():
                        mycol_teachers.update_one({ "username": username }, { "$push": { "courses_id": id } }) 
                        return {"message": "Teacher updated!"}, 200  
                    else:
                        mycol_teachers.update_one({ "username": username }, { "$set": { "courses_id": id } })
                        return {"message": "Teacher updated!"}, 200
                        
                else:
                    if course_id:
                        return {"error": "Teacher not found!"}, 404
                    elif teacher:
                        return {"error": "Course not found!"}, 404
                    else:
                        return {"error": "Teacher and Course not found!"}, 404
            else:
                return {"error": "You are not authorized to edit a teacher. You must have an admin status."}, 401

        except Exception as e:
            return dumps({"error": str(e)})

    def delete(self, username, id):
        try:
            current_teacher = mycol_teachers.find_one({"username": current_identity.username})
            if current_identity.username == "admin" or current_teacher.get("role") == 1:
                teacher = list(mycol_teachers.find_one({"username": username}))
                course_id = list(mycol_courses.find_one({"_id": id}))
                if teacher and course_id:
                    teacher = teacher[0]
                    if "courses_id" in teacher.keys():
                        if id in teacher["courses_id"]:
                            mycol_teachers.update({}, { "$pull": { "courses_id": id } })
                            mycol_courses.find_one_and_update({"_id" : id}, {"teachers_id" : None })

                        else:
                            return {"error": "This teacher does not operate over wanted course!"}, 400
                    else:
                        return {"error": "This teacher does not operate over wanted course!"}, 400
                else:
                    if course_id:
                        return {"error": "Teacher not found!"}, 404
                    elif teacher:
                        return {"error": "Course not found!"}, 404
                    else:
                        return {"error": "Teacher and Course not found!"}, 404
            else:
                return {"error": "You are not authorized to edit a teacher. You must have an admin status."}, 401
        except Exception as e:
            return dumps({"error": str(e)})
