from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from src.models import User
from src import Exceptions

app = Flask(__name__)

try:
    eng = create_engine('postgresql://kacper:dupa123@rychel.dev/rest',
                        connect_args={"options": "-c statement_timeout=1000"})
    con = eng.connect()
    Smaker = sessionmaker(bind=eng)
    session = Smaker()
    User.metadata.create_all(eng)
except OperationalError as e:
    print('Connection timeout!')


def getData():
    return request.get_json()


def isEmpty(queryRes):
    if queryRes.count() == 0:
        raise Exceptions.UserNotFoundException()


def paramsValidate(params):
    keys = {'name', 'nickname', 'age'}
    for key in keys:
        if params.get(key) is None:
            raise Exceptions.IncorrectInputException()
    if (not str(params.get('age')).isnumeric()) or params.get('age') <= 0:
        raise Exceptions.IncorrectInputException()


# Get dla usera: aby mogl sprawdzac info
@app.route('/<id>', methods=['GET'])
def getInfo(id):
    try:
        object = session.query(User).filter_by(id=id)
        isEmpty(object)
        object = object.first()
    except Exceptions.UserNotFoundException as e:
        return jsonify({"message": "User not found."}), 404

    print('name = {}, nickname = {}, age = {}'.format(object.name, object.nickname, object.age))
    return {"message": "Person has been shown 'name = {}, nickname = {}, age = {}'".format(object.name, object.nickname,
                                                                                           object.age)}, 200

def _register():
    try:
        content = getData()
        paramsValidate(content)
    except Exceptions.IncorrectInputException as e:
        return jsonify({'message': 'Parameters given incorrectly'}), 404

    addUser = User()
    addUser.name = content['name']
    addUser.nickname = content['nickname']
    addUser.age = content['age']
    session.add(addUser)
    # TODO find proper exception for session.add and session.commit
    session.commit()
    # try:
    #   session.commit()
    # except    <SOME EXCEPTION>
    return jsonify({"message": "person has been added", "id": addUser.id}), 202

@app.route('/register', methods=['PUT'])
def register():
    return _register()


@app.route('/delete', methods=['DELETE'])
def delete():
    try:
        id = request.get_json()['id']  # ogolna skladnia do pracy na tym co zwroci funkcja
        object = session.query(User).filter_by(id=id)
        isEmpty(object)
        object = object.first()
    except Exceptions.UserNotFoundException as e:
        return jsonify({'message': 'The specified ID does not exist. Deletion cannot be made.'}), 404
    session.delete(object)
    session.query()  # request.get_json() -> uzycie [] nawiasow
    session.commit()  # w tym przypadk. get_json daje mi dicta -> w [] mam mozliwosc
    return jsonify({'message': 'person has been deleted'}), 202  # od razu na nim pracowac

    # #opja na piechote (zamiast tego ^):
    # content = request.get_json()
    # id = content['id']


@app.route('/update', methods=['PATCH'])
def update():
    try:
        id = request.get_json()['id']
        content = request.get_json()
        object = session.query(User).filter_by(id=id)
        isEmpty(object)
        object = object.first()
    except Exceptions.IncorrectInputException as e:
        return jsonify({'message': 'The specified ID does not exist. Updating cannot be made.'}), 404
    object.name = content['name']
    object.nickname = content['nickname']
    object.age = content['age']
    session.add(object)
    session.commit()

    return jsonify({'message': 'person has been updated'}), 202


if __name__ == '__main__':
    app.run()
