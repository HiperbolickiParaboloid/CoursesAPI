from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import Courses
import Teachers
app = Flask(__name__)
api = Api(app)

api.add_resource(Courses.Course, "/course/<string:name>")
api.add_resource(Courses.CoursesList, "/products")
api.add_resource(Courses.CourseID, "/courseid/<string:_id>")
api.add_resource(Courses.CourseNUM, "/subs_num/<string:_id>")
api.add_resource(Courses.CoursesLimit, "/courses")
api.add_resource(Courses.CourseINC, "/subs_inc/<string:_id>")
api.add_resource(Courses.CourseDEC, "/subs_dec/<string:_id>")
api.add_resource(Teachers.Teacher, "/teachers/<string:username>")
api.add_resource(Teachers.TeachersList, "/teachers")


app.run(port=5000, debug=True)