from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class UserModel(db.Model, SerializerMixin):
    __tablename__ = 'users'
    serialize_rules = ('-logs.user',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    logs = db.relationship('UserLog', back_populates='user', cascade='all, delete')

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('Invalid email address')
        return email

    def __repr__(self):
        return f'<User {self.username}, {self.email}>'


class UserLog(db.Model, SerializerMixin):
    __tablename__ = 'userlogs'
    serialize_rules = ('-user.logs',)

    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String)
    average_sleep = db.Column(db.Integer, default=0)
    total_water_taken = db.Column(db.Integer, default=0)
    total_exercise_time = db.Column(db.Integer, default=0)
    total_meditation_time = db.Column(db.Integer, default=0)
    low_moments = db.Column(db.String)
    cope_up = db.Column(db.String)
    quote_of_the_day = db.Column(db.String)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', back_populates='logs')

    def __repr__(self):
        return (f"<UserLog {self.id}, {self.hashtag}, {self.average_sleep}, "
                f"{self.total_water_taken}, {self.total_exercise_time}, {self.total_meditation_time}, "
                f"{self.low_moments}, {self.cope_up}, {self.quote_of_the_day}>")