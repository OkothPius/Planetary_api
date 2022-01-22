from flask import Flask, jsonify, request

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run()
