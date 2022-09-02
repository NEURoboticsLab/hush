from flask import Flask, redirect, render_template, request, flash, session, url_for,g
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# initialiazing the flask app
app = Flask(__name__)
api = Api(app)
app.secret_key = "flaskesp32"

# Creating the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor.db'
db = SQLAlchemy(app)

# creating the UUID's
def generate_UUID():
   return ["cac1010b-fa6e-4641-9d95-ba82ec4e5d27"]

# Database model
class Data(db.Model):
    uuid = db.Column(db.String(60), name = "uuid", nullable = False, primary_key = True)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.now, primary_key=True)
    decibel = db.Column(db.Integer, nullable = False)
# db.create_all()

# creating my request parser
sensor_post = reqparse.RequestParser()
sensor_post.add_argument("uuid",type = str, help = "This is required", default = generate_UUID, required = True)
sensor_post.add_argument("decibel",type = int, help= "This is Required", required = True)

# resource fields
resource_fields = {
    "uuid":fields.String,
    "timestamp": fields.DateTime,
    "decibel":fields.Integer
}

# API
class Sensor(Resource):
    def get(self):
        datas = Data.query.all()
        all = []
        for data in datas:
            all.append ({"uuid":str(data.uuid), "timestamp":str(data.timestamp), "decibel":data.decibel})
        return all
    @marshal_with(resource_fields)
    def post(self):
        args = sensor_post.parse_args()
        sensor_new =Data(uuid = args['uuid'], decibel = args["decibel"])
        if args['uuid'] not in generate_UUID():
            abort(405)
        db.session.add(sensor_new)
        db.session.commit()
        return sensor_new, 201

# creating the endpoint
api.add_resource(Sensor, "/sensor")

# main route
@app.route('/')
def index():
    return render_template("login.html")

# login username and password
login_database = {"busayo":"busayo","admin":"admin","1234":"1234"}

# logging into the website
@app.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        pwd = request.form['password']
        session['name'] = name
        session['pwd'] = pwd
        if name not in login_database:
            flash("User not found")
            session.pop('name', None)
            return render_template('login.html')
        else:
            if login_database[name]!= pwd:
                flash("Incorrect password")
                session.pop('name', None)
                return render_template('login.html')
            else:
                return redirect('/home')
    else:
        if 'name' and 'pwd' in session:
            return redirect(url_for('home'))
            
        return render_template('login.html')

# logging out of the website
@app.route('/logout')
def logout():
    if 'name' and 'pwd' in session:
        session.pop('name', None)
        session.pop('pwd', None)
        flash('You have been logged out!')

    return redirect(url_for('login'))


# to keep track of sessions
@app.before_request
def before_request():
    g.name = None
    if 'name' in session:
        g.name = session['name']

# home page
@app.route('/home')
def home():

    if g.name:
        # number of devices
        devices = len(generate_UUID())
        # print(devices)
        # pagination
        page = request.args.get('page', 1, type=int)
        all_data = Data.query.order_by(desc(Data.timestamp)).paginate(page = page, per_page = 20)
        # top_data = Data.query.order_by(desc(Data.timestamp)).first()
        # print(dir(all_data))

        #for infinte scroll
        if 'hx_request' in request.headers:
            return render_template("table.html", datas = all_data, devices = devices)
        return render_template("home.html", datas = all_data, devices = devices)
    else:
        flash('Unauthorised access!')
        return render_template('login.html')

# for active search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if g.name:
        # if methods == 'POST':
        search_table = request.args.get('search')
        if search_table:
            tables = Data.query.filter(Data.uuid.contains(search_table) | Data.timestamp.contains(search_table))
            
        else:
            tables = []
        # return render_template('search.html', result = tables)
            
        if 'hx_request' in request.headers:
            return render_template("searchres.html", result = tables)
        return render_template('search.html', result = tables)
    else:
        flash('Unauthorised access!')
        return redirect(url_for('login'))

# for average
def get_average_hour(a,w):              # Average per hour
    if a and w:
        a = int(a)
        
        current_time = datetime.now()            # getting current time
        time_diff = current_time - timedelta(hours=a) # getting time difference
        last_data = Data.query.filter_by(uuid = w).filter(Data.timestamp>time_diff).all()
        divider = len(last_data) #length of output
        num = 0
        for last in last_data:
            num = num + last.decibel
        if divider != 0:
            average = num/divider
            return int(average)
        flash("No Data")
def get_average_day(a,w): # getting the average per day
    if a and w:
        a = int(a)
        
        current_time = datetime.now()
        time_diff = current_time - timedelta(days=a)
        last_data = Data.query.filter_by(uuid = w).filter(Data.timestamp>time_diff).all()
        divider = len(last_data)
        num = 0
        for last in last_data:
            num = num + last.decibel
        if divider != 0:
            average = num/divider
            return int(average)
        flash("No Data")
def get_average_week(a,w):  # getting the average per week
    if a and w:
        a = int(a)
        
        current_time = datetime.now()
        time_diff = current_time - timedelta(weeks=a)
        last_data = Data.query.filter_by(uuid = w).filter(Data.timestamp>time_diff).all()
        divider = len(last_data)
        num = 0
        for last in last_data:
            num = num + last.decibel
        if divider != 0:
            average = num/divider
            return int(average)
        flash("No Data")
def get_average(w,y,z): # getting average based on date
    # y is start date
    # z is end date
    if w:
        first = Data.query.filter_by(uuid = w).filter(Data.timestamp.between(y,z)).all()
        firsts = len(first)
        fi = 0
        for firs in first:
            fi = fi + firs.decibel
        if firsts !=0:
            average = fi/firsts   
            return int(average)
        flash('No data')

# average with date   
@app.route('/average')
def average():
    if g.name:
        # per hour
        a = request.args.get('a')
        uuid1 = request.args.get('uuid')
        
        average1 = get_average_hour(a,uuid1)
        if average1:
            if 'hx_request' in request.headers:
                return render_template('avg.html', avg = average1)
            return render_template('average.html', avg = average1)

        # per day
        n = request.args.get('n')
        uuid1 = request.args.get('uuid')
        average2 = get_average_day(n, uuid1)
       
        if average2:
            if 'hx_request' in request.headers:
                return render_template('avn.html', avn = average2)
            return render_template('average.html', avn = average2) 
        # per week
        w = request.args.get('w')
        uuid1 = request.args.get('uuid')
        average3 = get_average_week(w,uuid1)
        if average3:
            if 'hx_request' in request.headers:
                return render_template('avw.html', avw = average3)
            return render_template('average.html', avw = average3)
        uuid3 = request.args.get('uuid')
        startdate = request.args.get('y')
        enddate = request.args.get('z')
        if startdate and enddate:
            if startdate < enddate:
                average4 = get_average(uuid3,startdate,enddate)
            
                if average4:
                    if 'hx_request' in request.headers:
                        return render_template('avf.html', avf = average4)
                    return render_template('average.html', avf = average4)
                flash('No data')
            else:
                flash('Start date must be less than end date')
        return render_template('average.html')
    else:
        flash('Unauthorized access!')
        return(redirect(url_for('login')))

# Daily average
@app.route('/dailyavg')
def dailyavg():
    now = datetime.now()
    diff = now - timedelta(days= 1)
    news = Data.query.filter(Data.timestamp>diff).all()
    num = len(news)
    m = 0
    for new in news:
        m += new.decibel
    if num!=0:
        average = m/num
    else:
        average = 0
    daily = int(average)
    # print(num)
    # print(m)
    # print(daily)
    if 'hx_request' in  request.headers:
        return render_template('avd.html', avd = daily)
    return redirect('/')

# hourly average
@app.route('/houravg')
def houravg():
    now = datetime.now()
    diff = now - timedelta(hours = 1)
    news = Data.query.filter(Data.timestamp>diff).all()
    num = len(news)
    m = 0
    for new in news:
        m += new.decibel
    if num!=0:
        average = m/num
    else:
        average = 0
    daily = int(average)
    if 'hx_request' in  request.headers:
        return render_template('avh.html', avh = daily)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
