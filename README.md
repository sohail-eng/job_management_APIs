# job_management_APIs

This is a simple REST API-based Jobs Management System built with Flask and the Flask Rest Framework. It allows users to sign up, login, create job,update job,delete job, and search job.

## Features

- User signup
- User login with JWT authentication
- CRUD actions for jobs

## Requirements

- Python 3.6 or higher
- Flask 2.2.2
- Postgre SQL 

## Setup

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/sohail-eng/job_management_APIs
```
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Set up the database:
change connection link and run commands
```bash
flask run
```
close the program by ctrl + c
```bash
flask db init
flask db migrate
flask db upgrade
```


## Running the API

To start the API locally, run the following command:
```bash
flask run
```

## Postman Collection
The postman collection is available at `post_man_collection.json` that you can use to test apis by importing collection in Postman


## Testing
To run the pytests, use the following command:

```bash 
pytest testing.py
```
