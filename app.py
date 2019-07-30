from flask import Flask, request
from flask_restful import Resource, Api
import Courses

app = Flask(__name__)
api = Api(app)

api.add_resource(Courses.Course, "/course/<string:name>")
api.add_resource(Courses.CoursesList, "/products")
api.add_resource(Courses.CourseID, "/courseid/<string:_id>")
api.add_resource(Courses.CourseNUM, "/subs_num/<string:_id>")
api.add_resource(Courses.CoursesLimit, "/courses")
api.add_resource(Courses.CourseINC, "/subs_inc/<string:_id>")
api.add_resource(Courses.CourseDEC, "/subs_dec/<string:_id>")

app.run(port=5000, debug=True)