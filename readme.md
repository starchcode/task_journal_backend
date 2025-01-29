# Task Journal App

## About The Project
DESCRIPTION LATER

## Getting Started

### Steps

This is an example of how to list things you need to use the software and how to install them.
* create a virtual environment
  ```sh
  python3 -m venv env
  ```

* start your env
  ```sh
  source env/bin/activate
  ```

* install dependencies
  ```sh
  pip install fastapi sqlalchemy psycopg2-binary uvicorn python-dotenv openai pgvector 

You need a postgre server on your machine and add its details to a .env file. see .env.example file for details

* start the server
  ```sh
  uvicorn main:app --reload


  command for running docker postgres image and rest of instructions: 
  docker run --name pgvector-demo -e POSTGRES_PASSWORD=<your password here> -p 5555:5555 ankane/pgv
ector

