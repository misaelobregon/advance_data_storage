#Import dependencies
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime
from datetime import date

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Base.classes.keys()
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

# #################################################
# # Flask Routes
# #################################################

@app.route("/")
def Welcome():
    return(
        f"Welcome! Hope you enjoy the Hawaii Climate ApPI<br/>"
        f"Available Routes:<br/>"
        f"<b>../api/v1.0/precipitation</b><br/>"
            "<ul>"
            "<li>Convert the query results to a Dictionary using date as the key and prcp as the value.</li><br/>"
            "<li>Return the JSON representation of your dictionary.</li><br/>"
            "</ul>"
            "<br>"
        f"<b>../api/v1.0/stations</b><br/>"
            "<ul>"
            "<li>Return a JSON list of stations from the dataset.</li><br/>"
            "</ul>"
            "<br>"
        f"<b>../api/v1.0/tobs</b><br/>"
            "<ul>"
            "<li>Query for the dates and temperature observations from a year from the last data point.</li><br/>"
            "<li>Return a JSON list of Temperature Observations (tobs) for the previous year.</li><br/>"
            "</ul>"
            "<br>"
        f"<b>../api/v1.0/start and /api/v1.0/start/end</b><br/>"
            "<ul>"
            "<li>The date should be as form YYYY-mm-dd.</li><br/>"
            "<li>Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.</li><br/>"
            "<li>When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.</li><br/>"
            "<li>When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.</li><br/>"
            "</ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    prcp_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > '2016-08-22').all()
    session.close()
    data_dict = []
    for data in prcp_query:
        newdict = {data[0]:data[1]}
        data_dict.append(newdict)
    return(jsonify(data_dict))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_ct_list = session.query(Measurement.station).all()
    session.close()
    station = list(np.ravel(station_ct_list))
    return(jsonify(station))
    

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    from_date = datetime.strptime(str(last_date),"%Y-%m-%d") - dt.timedelta(days=365)
    one_year_tobs = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= from_date.strftime("%Y-%m-%d")).all()
    session.close()
    data_dict = []
    for data in one_year_tobs:
        newdict = {data[0]:data[1]}
        data_dict.append(newdict)
    return(jsonify(data_dict))
   
@app.route("/api/v1.0/<start>")
def start_func(start):
    start = start.replace("<","")
    start = start.replace(">","")
    session = Session(engine)
    date_list = session.query(Measurement.date).all()
    datelist = list(np.ravel(date_list))
    if start in datelist:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        session.close()
        result = list(np.ravel(results))
        return(jsonify({"1 tmin": result[0],"2 tavg":result[1], "3 tmax": result[2]}))
    else:
        session.close() 
        return(jsonify({"error": f"The date entered is not valid."}), 404)

@app.route("/api/v1.0/<start>/<end>")
def start_end_func(start,end):
    start = start.replace("<","")
    start = start.replace(">","")

    end = end.replace("<","")
    end = end.replace(">","")

    session = Session(engine)
    date_list = session.query(Measurement.date).all()
    datelist = list(np.ravel(date_list))
    if (start in datelist) and (end in datelist):
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        session.close()
        result = list(np.ravel(results))
        return jsonify({"1 tmin": result[0],"2 tavg":result[1], "3 tmax": result[2]})
    elif start in datelist:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        session.close() 
        result = list(np.ravel(results))
        return jsonify({"1 error": "End date is not valid.","2 Results":"Calculated within start date to most recent valid date","3 tmin":result[0],"4 tavg":result[1],"5 tmax":result[2]}), 404
    else: 
        session.close() 
        return(jsonify({"error": f"The dates entered are not valid."}), 404)
    
if __name__ == '__main__':
    app.run(debug=True)