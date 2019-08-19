from flask import Flask, request
from flask_restful import Resource, Api
from security import identity, authenticate
from flask_jwt import JWT, jwt_required, current_identity
import Courses, Teachers
import os

app = Flask(__name__)
app.secret_key = "VERY-CONFIDENTAL"
api = Api(app)
jwt = JWT(app, authenticate, identity)

api.add_resource(Courses.Course, "/course/<string:name>")
api.add_resource(Courses.CoursesList, "/products")
api.add_resource(Courses.CourseID, "/courseid/<string:_id>")
api.add_resource(Courses.CourseNUM, "/subs_num/<string:_id>")
api.add_resource(Courses.CoursesLimit, "/courses")
api.add_resource(Courses.CourseINC, "/subs_inc/<string:_id>")
api.add_resource(Courses.CourseDEC, "/subs_dec/<string:_id>")
api.add_resource(Courses.Image, "/images")
api.add_resource(Teachers.Teacher, "/teacher/<string:username>")
api.add_resource(Teachers.TeachersList, "/teachers")
api.add_resource(Teachers.TeacherSalary, "/salary/<string:username>")
api.add_resource(Teachers.TeacherCourse, "/teacher") 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)