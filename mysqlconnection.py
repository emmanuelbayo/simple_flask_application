from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

class MySQLConnection(object):
    def __init__(self,app):

        config = {
            'host':'localhost',
            'database':'DBNAME',
            'user': 'DBUSER',
            'password':'DBPASSWORD'
        }

        DATABASE_URI="mysql://{}:{}@{}/{}".format(config['user'],config['password'],config['host'],config['database'])
        app.config['SQLALCHEMY_DATABASE_URI']=DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

        self.db = SQLAlchemy(app)
    
    def get_db(self):
        return self.db
    
    def query_db(self,query,data=None):
        result = self.db.session.execute(text(query), data)
        if query[0:6].lower()=='select':
            list_result = [dict(r) for r in result]
            return list_result
        elif query[0:6].lower() =='insert':
            self.db.session.commit()
            return result.lastrowid
        else:
            self.db.session.commit()

def MySQLConnector(app):
    return MySQLConnection(app)