import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)

# Now that you’ve completed your initial analysis, you’ll design a Flask API based on the queries that you just developed. 
# To do so, use Flask to create your routes as follows:
# Start at the homepage. List all the available routes.

@app.route("/")
def welcome():
    return  (f"Available Routes:<br/>"
            f"/api/v1.0/preceipitation - last year of preceipitation data<br/>"
            f"/api/v1.0/station - list of stations in all weather<br/>"
            f"/api/v1.0/tobs - last year of temperature of the most-active station<br/>"
            f"/api/v1.0/start - 2016-01-01/<br/>"
            f"/api/v1.0/end - 2017-12-31/<br/>")

#---------------------------------------------------------------------------------------------
@app.route("/api/v1.0/precipitaton")
def precipitation():
    # I think want to be describe() = .desc() in measurement
   
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp

    print(precipitation_data)
    return jsonify(precipitation_data)

#---------------------------------------------------------------------------------------------
@app.route("/api/v1.0/station")
def station():
    
    station_results = session.query(Station.station, Station.name).all()

     # Convert the query results to a list of dictionaries
    stations_data = []
    for station, name in station_results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations_data.append(stations_dict)

    print(stations_data)
    return jsonify(stations_data)
#---------------------------------------------------------------------------------------------

@app.route("/api/v1.0/tobs")
def tobs():
    # again 1 year ago df
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()
        

    # Perform a query result
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station[0]).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Convert the query results to a list of dictionaries
    temperature_data = []
    for date, tobs in tobs_results:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["tobs"] = tobs
        temperature_data.append(temperature_dict)

    print(tobs_results)
    return jsonify(temperature_data)

#---------------------------------------------------------------------------------------------
@app.route('/api/v1.0/temperatures/<start_date>')
def temperature_stats(start_date):
    # Convert the start date string to a datetime object
    start_date = '2016-01-01'
    start = dt.datetime.strptime(start_date, "%Y-%m-%d")

    # Query the temperature observations for the date range
    start_stats_results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Convert the query results to a dictionary
    temperature_stats = {}
    temperature_stats["TMIN"] = start_stats_results[0][0]
    temperature_stats["TAVG"] = start_stats_results[0][1]
    temperature_stats["TMAX"] = start_stats_results[0][2]

    print(temperature_stats)
    return jsonify(temperature_stats)
#---------------------------------------------------------------------------------------------
@app.route('/api/v1.0/temperatures_v1/<end_date>')
def temperature_stats_v1(end_date):
    # Convert the start and end date strings to datetime objects
    end_date = '2017-01-01'
    end = dt.datetime.strptime(end_date, "%Y-%m-%d")

    temperature_stats_end_results = session.query(func.min(Measurement.tobs), 
                            func.avg(Measurement.tobs), 
                            func.max(Measurement.tobs)).\
        filter(Measurement.date <= end).all()
    
    end_temperature_stats = {}
    end_temperature_stats["TMIN"] = temperature_stats_end_results[0][0]
    end_temperature_stats["TAVG"] = temperature_stats_end_results[0][1]
    end_temperature_stats["TMAX"] = temperature_stats_end_results[0][2]

    print(end_temperature_stats)
    return jsonify(end_temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)



