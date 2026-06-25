from flask import Flask, request, jsonify, make_response
from models import db, UserModel, UserLog
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import os
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lifepulse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.urandom(32).hex()
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
CORS(app)
api = Api(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)


class Index(Resource):
    def get(self):
        return make_response(jsonify({'message': 'Welcome to LifePulse API'}), 200)

api.add_resource(Index, '/')


class UserRegister(Resource):
    @cross_origin()
    def post(self):
        new_user = UserModel(
            username=request.json['username'],
            email=request.json['email'],
            password=bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
        )

        if not new_user.username or not new_user.email or not new_user.password:
            return jsonify({'error': 'missing required fields'}), 400

        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.email)
        user_dict = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'access_token': access_token
        }

        return make_response(user_dict, 201)

api.add_resource(UserRegister, '/register')


class UserLogIn(Resource):
    @cross_origin()
    def post(self):
        email = request.json['email']
        password = request.json['password']

        user_exists = UserModel.query.filter_by(email=email).first()
        if not user_exists or not bcrypt.check_password_hash(user_exists.password, password):
            return jsonify({'error': 'Invalid email or password'}), 401

        access_token = create_access_token(identity=user_exists.email)
        return make_response(jsonify(
            {
                'id': user_exists.id,
                'username': user_exists.username,
                'email': user_exists.email,
                'access_token': access_token
            }
        ), 200)

api.add_resource(UserLogIn, '/login')


class UserDetails(Resource):
    def get(self, id):
        user = UserModel.query.get(id)
        if user:
            return make_response(user.to_dict(), 200)
        else:
            return jsonify({'message': 'user with the associated id not found'}), 400

api.add_resource(UserDetails, '/userdetails/<int:id>')


class CreateLogs(Resource):
    @cross_origin()
    @jwt_required()
    def post(self):
        current_user_email = get_jwt_identity()
        current_user = UserModel.query.filter_by(email=current_user_email).first()

        if not current_user:
            return {'error': 'unauthorized access'}, 404

        new_user_log = UserLog(
            hashtag=request.json['hashtag'],
            average_sleep=request.json['average_sleep'],
            total_water_taken=request.json['total_water_taken'],
            total_exercise_time=request.json['total_exercise_time'],
            total_meditation_time=request.json['total_meditation_time'],
            low_moments=request.json['low_moments'],
            cope_up=request.json['cope_up'],
            quote_of_the_day=request.json.get('quote_of_the_day'),
            user=current_user
        )
        db.session.add(new_user_log)
        db.session.commit()
        return make_response(new_user_log.to_dict(), 201)

api.add_resource(CreateLogs, '/addlog')


class GetLogs(Resource):
    @cross_origin()
    @jwt_required()
    def get(self):
        current_user_email = get_jwt_identity()
        current_user = UserModel.query.filter_by(email=current_user_email).first()

        if not current_user:
            return {'message': 'access denied!'}

        user_logs = UserLog.query.filter_by(user_id=current_user.id).all()
        return make_response(jsonify([log.to_dict() for log in user_logs]), 200)

api.add_resource(GetLogs, '/logs')


class UserLogTotals(Resource):
    @cross_origin()
    @jwt_required()
    def get(self):
        current_user_email = get_jwt_identity()
        current_user = UserModel.query.filter_by(email=current_user_email).first()

        if not current_user:
            return {"error": "Unauthorized"}, 401

        # Calculate totals
        totals = db.session.query(
            func.avg(UserLog.average_sleep),
            func.sum(UserLog.total_water_taken),
            func.sum(UserLog.total_exercise_time),
            func.sum(UserLog.total_meditation_time),
            func.count(UserLog.id)
        ).filter(UserLog.user_id == current_user.id).first()

        log_count = int(totals[4] or 0)

        # Medal logic
        if log_count >= 6:
            medal = "gold"
        elif log_count >= 4:
            medal = "bronze"
        elif log_count >= 2:
            medal = "silver"
        else:
            medal = None

        # Latest quote
        latest_log = UserLog.query.filter_by(user_id=current_user.id).order_by(UserLog.created_at.desc()).first()
        quote_of_the_day = latest_log.quote_of_the_day if latest_log else None

        result = {
            "avg_sleep": float(totals[0] or 0),
            "total_water": int(totals[1] or 0),
            "total_exercise": int(totals[2] or 0),
            "total_meditation": int(totals[3] or 0),
            "log_count": log_count,
            "medal": medal,
            "quote_of_the_day": quote_of_the_day
        }

        return make_response(jsonify(result), 200)

api.add_resource(UserLogTotals, '/logs/totals')


class EditLog(Resource):
    @cross_origin()
    @jwt_required()
    def put(self, log_id):
        current_user_email = get_jwt_identity()
        current_user = UserModel.query.filter_by(email=current_user_email).first()

        if not current_user:
            return {'error': 'Unauthorized access'}, 401

        log = UserLog.query.filter_by(id=log_id, user_id=current_user.id).first()
        if not log:
            return {'error': 'Log not found'}, 404

        data = request.json
        log.hashtag = data.get('hashtag', log.hashtag)
        log.average_sleep = data.get('average_sleep', log.average_sleep)
        log.total_water_taken = data.get('total_water_taken', log.total_water_taken)
        log.total_exercise_time = data.get('total_exercise_time', log.total_exercise_time)
        log.total_meditation_time = data.get('total_meditation_time', log.total_meditation_time)
        log.low_moments = data.get('low_moments', log.low_moments)
        log.cope_up = data.get('cope_up', log.cope_up)
        log.quote_of_the_day = data.get('quote_of_the_day', log.quote_of_the_day)

        db.session.commit()
        return make_response(log.to_dict(), 200)

api.add_resource(EditLog, '/editlog/<int:log_id>')


class DeleteLog(Resource):
    @cross_origin()
    @jwt_required()
    def delete(self, log_id):
        current_user_email = get_jwt_identity()
        current_user = UserModel.query.filter_by(email=current_user_email).first()

        if not current_user:
            return {'error': 'Unauthorized access'}, 401

        log = UserLog.query.filter_by(id=log_id, user_id=current_user.id).first()
        if not log:
            return {'error': 'Log not found'}, 404

        db.session.delete(log)
        db.session.commit()
        return {'message': f'Log {log_id} deleted successfully'}, 200

api.add_resource(DeleteLog, '/deletelog/<int:log_id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)