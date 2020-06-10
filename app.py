import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']= True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weatherinfo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=cd495ad0382849f8f5b423ab9cf80372'
    r = requests.get(url).json()
    return r

@app.route('/')
def index_get():
    cities=City.query.all()
    weather_data=[]
   
    for city in cities:

        r = get_weather_data(city.name)
        weather = {
            'city' : city.name,
            'temperature': r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        
        weather_data.append(weather)
  

    return render_template('weatherinfo.html', weather_data=weather_data)
    
@app.route('/', methods=['POST'])
def index_post():
    error_message = ''
    new_city = request.form.get('city')
       
    if new_city:
        added_city = City.query.filter_by(name=new_city).first()
        if not added_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod']==200:
                new_city_obj = City(name=new_city)
                
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                error_message = 'Please enter a valid city name!'
        else:
            error_message='City is already added!'

    if error_message:
        flash(error_message, 'error')
    else:
        flash('City added!')



    return redirect(url_for('index_get'))

@app.route('/remove/<name>')
def remove_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully removed {city.name}', 'success')

    return redirect(url_for('index_get'))
    