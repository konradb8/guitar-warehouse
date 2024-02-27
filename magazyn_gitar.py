from flask import Flask, jsonify, request, render_template
import sqlalchemy as db
from sqlalchemy import create_engine, Column, Integer, String, select, Table, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, aliased
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
Base = declarative_base()


class Guitar(Base):
    __tablename__ = 'guitars'
    __table_args__ = {'schema': 'schemat24'}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Integer)

    def __str__(self):
        return str(self.id) + " " + str(self.name) + " " + str(self.quantity) + " " + str(self.price)


class Amp(Base):
    __tablename__ = 'amps'
    __table_args__ = {'schema': 'schemat24'}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Integer, nullable=False)

    def __str__(self):
        return str(self.id) + " " + str(self.name) + " " + str(self.quantity) + " " + str(self.price)


engine = db.create_engine('postgresql://postgres:kanapka123@localhost:5432/postgres')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/', methods=['GET'])
def get_guitars():
    guitars = session.query(Guitar).all()
    amps = session.query(Amp).all()
    return render_template('guitars.html', guitars=guitars, amps=amps)


@app.route('/api/guitars', methods=['GET'])
def get_guitars_json():
    guitars = session.query(Guitar).all()
    guitars_list = [{'id': guitar.id, 'name': guitar.name, 'quantity': guitar.quantity, 'price': guitar.price} for
                    guitar in guitars]
    return jsonify(guitars_list)


@app.route('/api/all', methods=['GET'])
def get_all_json():
    guitars = session.query(Guitar).all()
    amps = session.query(Amp).all()
    guitars_list = [{'id': guitar.id, 'name': guitar.name, 'quantity': guitar.quantity, 'price': guitar.price} for
                    guitar in guitars]
    amps_list = [{'id': amp.id, 'name': amp.name, 'quantity': amp.quantity, 'price': amp.price} for amp in amps]
    return jsonify(guitars_list) + jsonify(amps_list)


@app.route('/api/amps', methods=['GET'])
def get_amps_json():
    amps = session.query(Amp).all()
    amps_list = [{'id': amp.id, 'name': amp.name, 'quantity': amp.quantity, 'price': amp.price} for amp in amps]
    return jsonify(amps_list)


@app.route('/guitars/add', methods=['POST'])
def add_guitar():
    new_guitar = Guitar(name=request.json['name'], quantity=request.json['quantity'], price=request.json['price'])
    session.add(new_guitar)
    session.commit()
    return jsonify({'message': 'Dodano nową gitarę'}), 201


@app.route('/guitars/edit/<int:id>', methods=['PUT'])
def update_guitar(id):
    guitar_to_update = session.query(Guitar).get(id)
    guitar_to_update.name = request.json['name']
    guitar_to_update.quantity = request.json['quantity']
    guitar_to_update.price = request.json['price']
    session.commit()
    return jsonify({'message': 'Zaktualizowano gitarę'}), 200


@app.route('/guitars/delete/<int:id>', methods=['DELETE'])
def delete_guitar(id):
    guitar_to_delete = session.query(Guitar).get(id)
    session.delete(guitar_to_delete)
    session.commit()
    return jsonify({'message': 'Usunięto gitarę'}), 200


@app.route('/guitars/left', methods=['GET'])
def leftjoin():
    amps = aliased(Amp)
    query = session.query(Guitar, amps).outerjoin(amps, (Guitar.id > amps.id))
    result = query.all()
    return jsonify([{"Guitar": str(guitar), "Amp": str(amp)} for guitar, amp in result])



@app.route('/guitars/inner', methods=['GET'])
def innerjoin():
    amps = aliased(Amp)
    query = session.query(Guitar, amps).join(amps, Guitar.id == amps.id)
    result = query.all()
    return jsonify([{"Guitar": str(guitar), "Amp": str(amp)} for guitar, amp in result])


if __name__ == '__main__':
    app.run(debug=True)
