from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import app

class User(db.Model):

    __tablename__="users"

    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),index=True,nullable=False)
    firstname=db.Column(db.String(60),index=True,nullable=False)
    lastname=db.Column(db.String(120),index=True,nullable=False)
    email=db.Column(db.String(90),index=True,unique=True,nullable=False)
    image_profile=db.Column(db.String(20),nullable=False, default='default.jpeg')
    password = db.Column(db.String(128),nullable=False)
    
    def get_reset_token(self,expires_sec=600):
        s = Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return "User <'{}', '{}', '{}'>".format(self.id,self.username,self.email)
