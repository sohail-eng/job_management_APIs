from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate
from flask_restful import reqparse, Api, Resource
import datetime
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_restful_swagger import swagger

import re

app = Flask(__name__, template_folder='./swagger/templates')
api = swagger.docs(Api(app), apiVersion='0.1',api_spec_url='/api/spec')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='004f2af45d3a4e161a7dd2d17fdae47f'

db = SQLAlchemy(app)
ma = Marshmallow(app)
auth = HTTPBasicAuth()
migrate = Migrate(app,db)
basic_auth = HTTPBasicAuth()
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self,first_name,last_name,email,username,password):
        self.first_name=first_name
        self.last_name=last_name
        self.email=email
        self.username=username
        self.password=password

    def __repr__(self):
        return f"<User {self.first_name}>"

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'password')

class Job(db.Model):
    __tablename__ = 'Job'
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    job_description = db.Column(db.String(255), nullable=False)
    job_rate = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, nullable=False)
    job_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    job_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, 
                            onupdate=datetime.datetime.utcnow
                            )

    def __init__(self,job_title, job_description, job_rate, latitude, longitude, user_id):
        self.job_title=job_title
        self.job_description=job_description
        self.job_rate=job_rate
        self.latitude=latitude
        self.longitude=longitude
        self.user_id=user_id

    def __repr__(self):
        return f"<Job {self.job_title}>"

class JobSchema(ma.Schema):
    class Meta:
        fields = ('id', 'job_title', 'job_description',
                 'job_rate', 'latitude', 'longitude', 
                 'is_active', 'user_id', 'job_created', 
                 'job_updated'
                 )

job_schema = JobSchema()
jobs_schema = JobSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
parser = reqparse.RequestParser()

class User_SignUp(Resource):

    def post(self):
        req_data = request.get_json(force=True)
        first_name = req_data['first_name']
        last_name = req_data['last_name']
        email = req_data['email']
        username = req_data['username']
        password = req_data['password']

        if not first_name:
            return {
                    'error': 'First name is required.'
                    },400
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
            return {
                    'error': 'Invalid email address.'
                    },400
        if len(password) < 10:
            return {
                    'error': 'Password must be at least 10 characters.'
                    },400
        if User.query.filter_by(email=email).first():
            return {
                    'error': 'Email already in use.'
                    },400
        if User.query.filter_by(username=username).first():
            return {
                    'error': 'Username already taken.'
                    },400
        new_user = User(first_name=first_name, last_name=last_name, 
                        email=email, username=username, password=password
                        )
        db.session.add(new_user)
        db.session.commit()
        return user_schema.jsonify(new_user)

class User_Login(Resource):

    def post(self):
        req_data = request.get_json(force=True)
        username = req_data['username']
        password = req_data['password']
        user = User.query.filter_by(username=username).first()
        if not user or not user.password == password:
            return  {
                    'error': 'Invalid username or password.'
                    },401
        access_token = create_access_token(identity=user.id)
        return jsonify(
                    {
                    'jwt_token': access_token
                    }
                )

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return True
    return False

class Jobs_Route(Resource):

    @jwt_required()
    def post(self):
        req_data = request.get_json(force=True)
        job_title = req_data['job_title']
        job_description = req_data['job_description']
        job_rate = req_data['job_rate']
        latitude = req_data['latitude']
        longitude = req_data['longitude']
        user_id = get_jwt_identity()
        new_job = Job(job_title=job_title, job_description=job_description, 
                        job_rate=job_rate, latitude=latitude, 
                        longitude=longitude, user_id=user_id
                        )
        db.session.add(new_job)
        db.session.commit()
        return job_schema.jsonify(new_job)

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        radius = request.args.get('radius', default=None, type=float)
        latitude = request.args.get('latitude', default=None, type=float)
        longitude = request.args.get('longitude', default=None, type=float)
        jobs = Job.query.filter_by(user_id=user_id, is_active=True)
        if radius and latitude and longitude:
            jobs = jobs.filter(Job.id.in_(
                db.session.query(Job.id).filter(
                    Job.is_active.is_(True),
                    Job.user_id == user_id,
                    db.func.ST_Distance_Sphere(
                        db.func.ST_MakePoint(Job.longitude, Job.latitude),
                        db.func.ST_MakePoint(longitude, latitude)
                    ) <= radius * 1000
                )
            ))
        jobs = jobs.all()
        return jobs_schema.jsonify(jobs)

class Jobs_Put_Delete(Resource):
    @jwt_required()
    def put(self,id):
        job = Job.query.get(id)
        if job:
            if job.user_id == get_jwt_identity():
                job.job_title = request.json.get('job_title', job.job_title)
                job.job_description = request.json.get('job_description', job.job_description)
                job.job_rate = request.json.get('job_rate', job.job_rate)
                job.latitude = request.json.get('latitude', job.latitude)
                job.longitude = request.json.get('longitude', job.longitude)
                job.is_active = request.json.get('is_active', job.is_active)
                job.job_updated = datetime.datetime.utcnow()
                db.session.commit()
                return job_schema.jsonify(job)
            else:
                return {
                        'error': 'Unauthorized to update this job.'
                        },401
        else:
            return {
                    'error': 'Job not found'
                    },404
    
    @jwt_required()
    def delete(self,id):
        job = Job.query.get(id)
        if job:
            if job.user_id == get_jwt_identity():
                job.is_active = False
                db.session.commit()
                return job_schema.jsonify(job)
            else:
                return jsonify(
                                {
                                    'error': 'Unauthorized to delete this job.'
                                }
                            )
        else:
            return jsonify(
                            {
                                'error': 'Job not found.'
                            }
                        )

api.add_resource(User_SignUp,'/signup')
api.add_resource(User_Login,'/login')
api.add_resource(Jobs_Route,'/jobs')
api.add_resource(Jobs_Put_Delete,'/jobs/<id>')

@app.route('/',methods=['GET'])
def main_page():
    return "OK"

if __name__=="__main__":
    app.run()
    