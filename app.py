from os import name
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify
from sqlalchemy.orm.session import make_transient

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    test = (
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start>/<end><br/>"
    )

    return(test)

@app.route("/api/v1.0/precipitation")
def precip():

    session = Session(engine)
    
    # Perform a query to retrieve the data and precipitation
    first_date = dt.date(2017,8,23)
    year_ago = first_date - dt.timedelta(days=365)

    prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago).\
    order_by(Measurement.date).all()
    
    session.close()
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #define dict
    precip_dict = {date: prcp for date, prcp in prcp}
    return jsonify(precip_dict)
    
#set up function for stations, temp, tobs
@app.route("/api/v1.0/stations")
def station_func():
    
    session = Session(engine)
    station_data = session.query(Station.name, Station.station).all()
    session.close()

    station_dict = {station: name for station, name in station_data}
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    first_date = dt.date(2017,8,23)
    year_ago = first_date - dt.timedelta(days=365)

    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).first()

    # Perform a query to retrieve the data and precipitation
    temps = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year_ago).\
    filter(Measurement.station == most_active[0]).\
    order_by(Measurement.date).all()

    session.close()

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #define dict
    temp_dict = {date: tobs for date, tobs in temps}
    return jsonify(temp_dict)   

#given both start and end date
@app.route("/api/v1.0/temp/<start>/<end>")
def dates(start="YYYY-MM-DD", end="YYYY-MM-DD"):
    session = Session(engine)

    station_high = session.query(Measurement.date, func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    station_low = session.query(Measurement.date, func.min(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()


    station_avg = session.query(Measurement.date, func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #define dict
    return jsonify(f" the low was {station_low}, the high was {station_high}, and {station_avg} was the average")

#start date
@app.route("/api/v1.0/temp/<start>")
def start_date(start="YYYY-MM-DD"):
    session = Session(engine)

    station_high = session.query(Measurement.date, func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    station_low = session.query(Measurement.date, func.min(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    station_avg = session.query(Measurement.date, func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    session.close()

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #define dict
    return jsonify(f" the low was {station_low}, the high was {station_high}, and {station_avg} was the average")   
#end date
@app.route("/api/v1.0/temp/<end>")
def end_date(end="YYYY-MM-DD"):
    session = Session(engine)

    station_high = session.query(Measurement.date, func.max(Measurement.tobs)).\
    filter(Measurement.date <= end).all()

    station_low = session.query(Measurement.date, func.min(Measurement.tobs)).\
    filter(Measurement.date <= end).all()


    station_avg = session.query(Measurement.date, func.avg(Measurement.tobs)).\
    filter(Measurement.date <= end).all()

    session.close()

    #Convert the query results to a dictionary using date as the key and prcp as the value.
    #define dict
    return jsonify(f" the low was {station_low}, the high was {station_high}, and {station_avg} was the average")

#Return the JSON representation of your dictionary.
if __name__ == '__main__':
    app.run(debug=True)