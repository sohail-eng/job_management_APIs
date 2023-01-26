import pytest
import requests
import jwt
from flask_jwt_extended import get_jwt_identity


# Constants for the test User

first_name="Test1"
last_name="Test1"
email="tes2t866@gmail.com"
username="ali11223"
password="Ali1qw23@123432"


job_title="Developer"
job_description="Any one can apply"
job_rate=50.5
latitude=200.2
longitude=301.6
user_id=7


def test_signup():
     
    response = requests.post('http://127.0.0.1:5000/signup', json={
            "first_name":first_name,
            "last_name":last_name,
            "email":email,
            "username":username,
            "password": password
    })
    assert response.status_code == 200

def test_login():
    
    response = requests.post('http://127.0.0.1:5000/login', json={
            "username":username,
            "password": password
    })

    token = response.json()['jwt_token']
    assert token is not None

def test_job_get():
    response = requests.post('http://127.0.0.1:5000/login', json={
            "username":username,
            "password": password
    })
    token = response.json()['jwt_token']

    headers = {'Authorization': f'Bearer {str(token)}'}

    response = requests.get('http://127.0.0.1:5000/jobs', headers=headers)

    assert response.status_code == 200

def test_job_post():
    response = requests.post('http://127.0.0.1:5000/login', json={
            "username":username,
            "password": password
    })
    token = response.json()['jwt_token']
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('http://127.0.0.1:5000/jobs', headers=headers , 
        json={
            "job_title":job_title,
            "job_description":job_description,
            "job_rate":job_rate,
            "latitude":latitude,
            "longitude":longitude
        }
    )
    assert response.status_code ==200

def test_job_put():
    response = requests.post('http://127.0.0.1:5000/login', json={
            "username":username,
            "password": password
    })
    token = response.json()['jwt_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.put('http://127.0.0.1:5000/jobs/7', headers=headers , 
        json={
            "job_title":job_title,
            "job_description":job_description,
            "job_rate":job_rate,
            "latitude":latitude,
            "longitude":longitude
        }
    )
    assert response.status_code ==200

def test_job_delete():
    response = requests.post('http://127.0.0.1:5000/login', json={
            "username":username,
            "password": password
    })
    token = response.json()['jwt_token']

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.delete('http://127.0.0.1:5000/jobs/1', headers=headers)

    assert response.status_code ==200



