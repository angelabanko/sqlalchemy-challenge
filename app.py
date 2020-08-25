import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base.metadata.tables # Check tables, not much useful
# Base.classes.keys() # Get the table names

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
    return(
        f"Available Routes:<br/>"
        f"<br/>"
        f"The list of precipitation data with dates:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"The list of stations and names:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"The list of temprture observations from a year from the last data point:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Min, Max. and Avg. temperatures for given start date: (please use 'yyyy-mm-dd' format):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Min. Max. and Avg. tempratures for given start and end date: (please use 'yyyy-mm-dd'/'yyyy-mm-dd' format for start and end values):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
        f"i.e. <a href='/api/v1.0/min_max_avg/2012-01-01/2016-12-31' target='_blank'>/api/v1.0/min_max_avg/2012-01-01/2016-12-31</a>"
    )


@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsall = []
    for min, avg, max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start, stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(
            Measurement.date <= stop).all()
    session.close()

    tobsall = []
    for min, avg, max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year - 1, latestdate.month, latestdate.day)
    sel = [Measurement.date, Measurement.tobs]
    queryresult = session.query(
        *sel).filter(Measurement.date >= querydate).all()
    session.close()

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude,
           Station.longitude, Station.elevation]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station, name, lat, lon, el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)


@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date, Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)


if __name__ == '__main__':
    app.run(debug=True)
