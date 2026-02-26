from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata=MetaData(naming_convention={ "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",})
db=SQLAlchemy(metadata=metadata)


class UserModel(db.Model, SerializerMixin):
    __tablename__='users'
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String,  nullable=False)
    email=db.Column(db.String,  nullable=False)
    password=db.Column(db.String, nullable=False) 
    created_at=db.Column(db.DateTime, server_default=db.func.now())
    updated_at=db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('Invalid email address')
        return email
    
    def __repr__(self):
        return f'<User {self.username}, {self.email}>'
    