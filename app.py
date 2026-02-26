from flask import Flask, request, jsonify, make_response
from models import db, UserModel
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import os

app=Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI']='sqlite:///lifepulse.db'
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config ['JWT_SECRET_KEY']=os.urandom(32).hex()
app.json.compact=False

migrate=Migrate(app, db)

db.init_app(app)
CORS(app)
api=Api(app)
jwt=JWTManager(app)
bcrypt=Bcrypt(app)

class Index(Resource):
    def get(self):
        return make_response(jsonify({'message':'Welcome to LifePulse API'}), 200)
    
api.add_resource(Index, '/')


class UserRegister(Resource):
    @cross_origin()
    def post(self):
        new_user=UserModel(
            username=request.json['username'],
            email=request.json['email'],
            password=bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
            
        )
        
       
        
        if not new_user.username or not new_user.email or not new_user.password:
            return jsonify({'error':'missing required fields'}), 400
        
        
        db.session.add(new_user)
        db.session.commit()
        
        access_token=create_access_token(identity=new_user.email)
        user_dict={
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'access_token': access_token
        }
        
        return make_response(user_dict, 201)
    
api.add_resource(UserRegister, '/register')


class userLogIn(Resource):
    @cross_origin()
    def post(self):
        
        email=request.json['email']
        password=request.json['password']
        
        user_exists=UserModel.query.filter_by(email=email).first()
        if not user_exists:
            return jsonify({'error':'Invalid email or password'}), 401
        if not bcrypt.check_password_hash(user_exists.password, password):
            return jsonify({'error':'Invalid email or password'}), 401
        
        access_token=create_access_token(identity=user_exists.email)
        
        return make_response(jsonify(
            {
                'id': user_exists.id,
                'username': user_exists.username,
                'email': user_exists.email,
                'access_token': access_token
            }
        ), 200
        )
        
api.add_resource(userLogIn, '/login')
        
        
        


if __name__=='__main__':
    app.run(port=5555, debug=True)
                
