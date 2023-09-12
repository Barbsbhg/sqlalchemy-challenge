# Import the dependencies.
import datetime as dt
import sqlalchemy
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
Base.prepare(engine, reflect=True)

# Save references to each table
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
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - precipitation data for the last 12 months<br/>"
        f"/api/v1.0/stations - list of stations<br/>"
        f"/api/v1.0/tobs - temperature observations for the most active station (last year of data)<br/>"
        f"/api/v1.0/<start> - temperature stats for a specified start date<br/>"
        f"/api/v1.0/<start>/<end> - temperature stats for a specified start and end range"
    )

# precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    session.close()
    
    precipitation_data = {date: prcp for date, prcp in prcp_data}
    
    return jsonify(precipitation_data)

# stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station, Station.name, Station.latitude, 
                             Station.longitude, Station.elevation).all()
    session.close()
    station_list = [{"Station ID": station, "Station Name": name, 
                     "Station Latitude": latitude, "Station Longitude": longitude,
                     "Station Elevation": elevation} 
                    for station, name, latitude, longitude, elevation in stations]
    return jsonify(station_list)

#tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date >= previous_year).all()
    session.close()
    
    tobs_list = [{"Date": date, "Temperature": tobs} for date, tobs in tobs_data]
    
    return jsonify(tobs_list)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)