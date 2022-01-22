import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask import Flask, jsonify, request

# Configurations
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')

db = SQLAlchemy(app)


# Routes
@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/super_simple')
def super_simple():
    return jsonify(message='Hello from Planetary API')


@app.route('/not_found')
def not_found():
    return jsonify(message='Not found'), 404


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))

    if age < 18:
        return jsonify(message='Sorry ' + name + ', youre not old enough!'), 401
    return jsonify(message='Youre are welcome ' + name)


@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        return jsonify(message='Sorry ' + name + ', youre not old enough!'), 401
    return jsonify(message='Youre are welcome ' + name)


# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = 'planets'
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)
    

if __name__ == '__main__':
    app.run()
