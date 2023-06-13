# Import the dependencies.

import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
year_ago = dt.date(2017,8,23)-dt.timedelta(days=366) 

# Create our session (link) from Python to the DB
#session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#create the lists of all available api routes
@app.route("/")
def home():
     
    return ("""
    Available Routes:<br/>
    -api/v1.0/precipitation<br/>
    -api/v1.0/stations<br/>
    -api/v1.0/tobs<br/>
    -api/v1.0/<'start'><br/>
    -/api/v1.0/<'start'>/<'end'>
    """
    )

#Precipitation Dictionary  
@app.route("/api/v1.0/precipitation")
def precipitation():
#create engine
    session = Session(engine)
# Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017,8,23)-dt.timedelta(days=366)   
# Perform a query to retrieve the data and precipitation scores
    scores = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date>year_ago).\
    order_by(Measurement.date).all()
#creating dictionary
    precipitation_dict = {}
    for date, prcp in scores:
        precipitation_dict[date]=prcp
#close the session
    session.close() 
#return a json representation of dictionary
    return jsonify(precipitation_dict)   

@app.route("/api/v1.0/stations")
def stations():
#create engine
    session = Session(engine)
#query the station names
    station_names = session.query(Station.station,Station.name).all()
#Creating the dictionary
    station_list = []
    for station, name in station_names:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        station_list.append(station_dict)
#close the session
    session.close() 
#return a json representation of dictionary
    return jsonify(station_list) 

@app.route("/api/v1.0/tobs")
def tobs():
#create engine
    session = Session(engine)
#query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()
# Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
#Query the last 12 months of temperature observation
    temp = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.station == most_active_station[0]).all()
#create the dictionary
    tobs_list = []
    for date, tobs in temp:
      tobs_dict ={}
      tobs_dict['date']= date
      tobs_dict['tobs']= tobs
      tobs_list.append(tobs_dict)
#close the session
    session.close() 
#return a json representation of dictionary
    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_temp(start):
#create engine
    session = Session(engine)
#query the min,max,avg temp for the dates greater than or equal to start date
    result =session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
#create a dictionary for temp observations
    temp_dict ={
        'TMIN': result[0][0],
        'TAVG': result[0][1],
        'TMAX': result[0][2]
    }
#close the session
    session.close() 
#return a json representation of dictionary
    return jsonify(temp_dict)



@app.route("/api/v1.0/<start>/<end>")
def temp(start,end):               
#create engine
    session = Session(engine)
#query the min,max,avg temp for the dates between  start date and end date
    result =session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
#create a dictionary for temp observations
    temp_dict ={
        'TMIN': result[0][0],
        'TAVG': result[0][1],
        'TMAX': result[0][2]
    }
#close the session
    session.close() 
#return a json representation of dictionary
    return jsonify(temp_dict)


##Run Development server
if __name__ == '__main__':
    app.run(debug=True)