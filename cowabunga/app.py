# 1 Import the dependencies.
import numpy as np

from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    return (
        f"Welcome to the Homepage! This page is an analysis of Hawaii's climate <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end> <br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    session = Session(engine)
    sel = [measurement.date,
       measurement.prcp]

    precipitation_scores = session.query(*sel).\
        filter(measurement.date >=prev_year).\
        order_by(measurement.date)
    
    session.close()
    ##made it into a list of dictionaries
    prcp_data= []
    for date, prcp in precipitation_scores:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        prcp_data.append(prcp_dict)
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(station.station).all()
    session.close()
    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")

#####DEBUG THIS CODE###
def tobs():
    session = Session(engine)
    temps = session.query(measurement.tobs).\
        filter(measurement.date >= dt.date(2016, 8, 23)).\
        filter(measurement.station == "USC00519281")
    session.close()
    # most_active_station_temps = list(np.ravel(temps))
    # return jsonify(most_active_station_temps)
    return jsonify(temps)

########
# @app.route("/api/v1.0/<start>")
# def start(start):
#     session = Session(engine)
#     prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
#     sel = [measurement.date, 
#        func.min(measurement.tobs), 
#        func.max(measurement.tobs), 
#        func.sum(measurement.tobs)/func.count(measurement.tobs)]
#     start = session.query(*sel).\
#         filter(measurement.date >= prev_year)
#     session.close()    
#     starting = list(np.ravel(start))
#     canon = start.replace().lower()
#     return jsonify(starting)    
#####
# @app.route("/api/v1.0/<start>")
# def Start(start):
#     canon = real_name.replace
# @app.route("/api/v1.0/<start>/<end>")
if __name__ == "__main__":
    app.run(debug=True)