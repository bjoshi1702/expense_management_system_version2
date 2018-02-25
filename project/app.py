import json
import redis

from flask import Flask, Response, jsonify, request
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

DATABASE = 'mydb_assignment1'
PASSWORD = 'bhavika'
USER = 'root'
HOSTNAME = 'localhost'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s'%(USER, PASSWORD, HOSTNAME, DATABASE)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.config['REDIS_HOST'] = 'localhost'
app.config['REDIS_PORT'] = 6379
app.config['REDIS_DB'] = 0
redis = Redis(app)

db = SQLAlchemy(app)


class mytable(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200))
    email=db.Column(db.String(200))
    category=db.Column(db.String(200))
    description=db.Column(db.String(200))
    link=db.Column(db.String(200))
    estimated_costs=db.Column(db.String(200))
    submit_date=db.Column(db.String(200))
    
    def __init__(self,name,email,category,description,link,estimated_costs,submit_date):
        self.name=name
        self.email=email
        self.category=category
        self.description=description
        self.link=link
        self.estimated_costs=estimated_costs
        self.submit_date=submit_date
        
class CreateDB():
	def __init__(self):
		import sqlalchemy
		engine = sqlalchemy.create_engine('mysql://%s:%s@%s'%(USER, PASSWORD, HOSTNAME))
		engine.execute("CREATE DATABASE IF NOT EXISTS %s "%(DATABASE))
        


@app.route("/v1/expenses", methods=['POST'])
def index():
    CreateDB()
    db.create_all()
    my_data = str(request.data)
    data = json.loads(my_data, 'utf-8')
    name = data['name']
    email = data['email']
    category = data['category']
    description = data['description']
    link = data['link']
    estimated_costs = data['estimated_costs']
    submit_date = data['submit_date']

   
    user = mytable(name,email,category,description,link,estimated_costs,submit_date)
    db.session.add(user)
    db.session.commit()
    
    store_data={'id' : user.id, 'name' : name, 'email' : email, 'category' : category, 'description' : description, 'link' : link, 'estimated_costs' : estimated_costs, 'submit_date' : submit_date, 'status' : 'pending' , 'decision_date' : '' }
    js=json.dumps(store_data)
    resp=Response(js,status=201, mimetype='application/json')
    return resp

    
@app.route("/v1/expenses/<int:id>", methods=['GET'])    
def index1(id):
    get_data = mytable.query.filter_by(id=id).first_or_404()
    #print(get_data.name)
    
    
    show_data={'id' : get_data.id, 'name' : get_data.name, 'email' : get_data.email, 'category' : get_data.category, 'description' : get_data.description, 'link' : get_data.link, 'estimated_costs' : get_data.estimated_costs, 'submit_date' : get_data.submit_date, 'status' : 'pending', 'decision_date' : '' }
    js1=json.dumps(show_data)
    resp1=Response(js1, status=200, mimetype='application/json')
    return resp1

@app.route("/v1/expenses/<int:id>", methods=['PUT'])
def index2(id):
    updated_cost=str(request.data)
    data=json.loads(updated_cost, 'utf-8')
    up_cost=data['estimated_costs']
    update_data = mytable.query.filter_by(id=id).first()
    update_data.estimated_costs=up_cost
    db.session.commit()
    updated_data={'estimated_costs' : update_data.estimated_costs}
    return Response(status=202)
    
@app.route("/v1/expenses/<int:id>", methods=['DELETE'])
def index3(id):
    delete_data=mytable.query.filter_by(id=id).first()
    db.session.delete(delete_data)
    db.session.commit()
    return Response(status=204)

    
if __name__== "__main__":
    r_server = redis.Redis("127.0.0.1")
    r_server.lrem("PORTS", "6001", 0)
    r_server.rpush("PORTS", "6001")

    app.run(host="127.0.0.1", port=6001, debug=False)
