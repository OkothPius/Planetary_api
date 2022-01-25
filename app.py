import os
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from sqlalchemy import Column, Integer, String, Float
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from dotenv import load_dotenv

load_dotenv()

# Configurations
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] =os.getenv("JWT_SECRET_KEY")

# Flask-Mail Extension
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False



db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)


# Database commands
@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database Created!')

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database Dropped!')

@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury',
                     planet_type='Class D',
                     home_star='Sol',
                     mass=3.258e23,
                     radius=1516,
                     distance=35.98e6)

    venus = Planet(planet_name='Venus',
                     planet_type='Class K',
                     home_star='Sol',
                     mass=4.867e24,
                     radius=3760,
                     distance=67.24e6)

    earth = Planet(planet_name='Earth',
                     planet_type='Class M',
                     home_star='Sol',
                     mass=5.972e24,
                     radius=3959,
                     distance=92.96e6)

    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)

    test_user = User(first_name='William',
                     last_name='Herschel',
                     email='test@test.com',
                     password='p@ssw0rd')

    db.session.add(test_user)
    db.session.commit()
    print('Database Seeded!')

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


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exist!'), 409
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    password = request.form['password']
    user = User(first_name=first_name, last_name=last_name, email=email,
                password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify(message='User has been created Succesfully!'), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    email = request.form['email']
    password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login Succeeded!', access_token=access_token)
    return jsonify(message='Bad email or password!'), 401


@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("your planetary password is " + user.password,
                      sender="admin@planetary-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message='Password sent to ' + email)
    return jsonify(message="That email doesn't exist!"), 401


@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    return jsonify(message='Planet does not exist'), 404


@app.route('/add_planet', methods=['POST'])
@jwt_required()
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()

    if test:
        return jsonify(message='There is a planet with that name'), 409
    planet_type = request.form['planet_type']
    home_star = request.form['home_star']
    radius = float(request.form['radius'])
    mass = float(request.form['mass'])
    distance = float(request.form['distance'])

    new_planet = Planet(planet_name=planet_name,
                        planet_type=planet_type,
                        home_star=home_star,
                        radius=radius,
                        mass=mass,
                        distance=distance)

    db.session.add(new_planet)
    db.session.commit()
    return jsonify(message='A new planet has been added!'), 201


@app.route('/update_planet', methods=['PUT'])
@jwt_required()
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id=planet_id).first()

    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.home_star = request.form['home_star']
        planet.radius = request.form['radius']
        planet.mass = request.form['mass']
        planet.distance = request.form['distance']

        db.session.commit()
        return jsonify(message='The planet was updated!'), 202
    return jsonify(message='The planet was not found!'), 404


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


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type', 'home_star', 'mass'
                    'radius', 'distance')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__main__':
    app.run()
