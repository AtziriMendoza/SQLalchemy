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
        f"Dynamic Routes: <br/>"
        f"Enter a date after the /: /api/v1.0/<start> <br/>"
        f"Enter a start (after 1st /) and end date(after 2nd /): /api/v1.0/<start>/<end> <br/>"
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

def tobs():
    session = Session(engine)
    temps = session.query(measurement.tobs).\
        filter(measurement.date >= dt.date(2016, 8, 23)).\
        filter(measurement.station == "USC00519281")
    session.close()
    most_active_station_temps = [temp[0] for temp in temps]  # Flatten the list of tuples- temp[0] is the first index 
    # most_active_station_temps = list(np.ravel(temps))
    # return jsonify(most_active_station_temps)
    return jsonify(most_active_station_temps)

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
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    sel = [measurement.date, 
    func.min(measurement.tobs), 
    func.max(measurement.tobs), 
    func.sum(measurement.tobs)/func.count(measurement.tobs)]

    query_results = session.query(*sel).\
    filter(measurement.date >= start).\
    group_by(measurement.date).all()

    session.close()
    # for x in query_results:
    #    print(x)

    datesNtemps = []
    for date, min_temp, max_temp, avg_temp in query_results:
        start_dict = {}
        start_dict['date'] = date
        start_dict['min_temp'] = min_temp
        start_dict['max_temp'] = max_temp
        start_dict['avg_temp'] = avg_temp
        datesNtemps.append(start_dict)

    return jsonify(datesNtemps)


###this is a way to get the information but it 
# @app.route("/api/v1.0/<start>/<end>")
# def StartEnd(start, end):
#     session = Session(engine)
#     sel = [
#         measurement.date,
#         func.min(measurement.tobs),
#         func.max(measurement.tobs),
#         func.avg(measurement.tobs)
#         ]

#     # Query the database for data starting from the specified date
#     query_result = session.query(*sel).\
#         filter(measurement.date >= start).\
#         filter(measurement.date <= end).\
#         group_by(measurement.date).all()
#     session.close()
#     # Format the results into a list of dictionaries
#     startNend = []
#     for date, min_temp, max_temp, avg_temp in query_result:
#         startNend_dict = {
#             "date": date,
#             "min_temp": min_temp,
#             "max_temp": max_temp,
#             "avg_temp": avg_temp
#             }
#     startNend.append(startNend_dict)
#     return jsonify(startNend)

@app.route("/api/v1.0/<start>/<end>")
def StartEnd(start, end):
    session = Session(engine)
    sel = [
        measurement.date,
        func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)
        ]

    # Query the database for data starting from the specified date
    query_result = session.query(*sel).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).\
        group_by(measurement.date).all()
    session.close()
    # Format the results into a list of dictionaries
    if query_result and query_result[0][0] is not None:
        date, min_temp, max_temp, avg_temp = query_result[0]
        result = {
            "start_date": start,
            "end_date": end,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "avg_temp": avg_temp            
        }
    else:
        result = {
            "start_date": start,
            "end_date": end,
            "message": "No data available for the specified range."
        }
    return jsonify(result)
# @app.route("/api/v1.0/<start>/<end>")
# def StartEnd(start=None, end=None): """Return TMIN, TAVG, TMAX."""
#     session = Session(engine)
#     sel = [
#         measurement.date,
#         func.min(measurement.tobs),
#         func.max(measurement.tobs),
#         func.sum(measurement.tobs) / func.count(measurement.tobs),
#         ]

#     # Query the database for data starting from the specified date
#     query_result = session.query(*sel).\
#         filter(measurement.date >= start).\
#         filter(measurement.date <= end).\
#         group_by(measurement.date).all()
#     session.close()

#     if query_result and query_result[0][0] is not None:
#         date, min_temp, max_temp, avg_temp = query_result[0]
#         result = {
#             "start_date": start,
#             "end_date": end,
#             "min_temp": min_temp,
#             "max_temp": max_temp,
#             "avg_temp": avg_temp            
#         }
#     else:
#         result = {
#             "start_date": start,
#             "end_date": end,
#             "message": "No data available for the specified range."
#         }
#     return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)