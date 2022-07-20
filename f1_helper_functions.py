import fastf1
import fastf1.plotting
from calc_splines import calc_splines
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

pd.set_option('display.max_columns', 100)

def cache(cache_dir=None):
    """ Initialize caching

    Keyword Arguments:
        cache_dir (str) - path to cache directory
    """

    if(cache_dir is None):
        cache_dir = "cache"

    # Create cache directory if it does not already exist
    if(cache_dir not in os.listdir()):
        os.mkdir(cache_dir)

    # Enable caching at given directory
    fastf1.Cache.enable_cache(cache_dir)

def get_schedule(year=2022):
    """ Get the schedule for a given season

    Keyword Arguments:
        year (int) - year of season
    """

    schedule = fastf1.get_event_schedule(year)

    return schedule

def display_schedule(schedule):
    """ Display a select few attributes of the schedule for easier viewing

    Keyword Arguments:
        schedule (fastf1.events.EventSchedule) - schedule to display
    """

    print(schedule[["RoundNumber", "EventName", "EventDate", "Country", "Location", "EventFormat", "F1ApiSupport"]])

def get_event(year=2022, gp=1):
    """ Get a specific event/round/weekend from a given season

    Keyword Arguments:
        year (int) - year of season
        gp (int or str) - event/round/weekend identifier (round number or name)
    """

    # gp cannot be a testing session - must be within season
    if(isinstance(gp, int) and gp < 1):
        raise Exception("gp may not be a testing session")

    return fastf1.get_event(year, gp)

def get_session_from_event(event=None, session=5):
    """ Get a specific session from an event

    Keyword Arguments:
        event (fastf1.events.Event) - event to get session from
        session (int or str) - name or number of the session
    """

    if(event is None):
        raise Exception("Must supply an event")

    return fastf1.get_session(event.EventDate.year, event.RoundNumber, session)

def load_session_data(session=None):
    """ Load session data to cache for later use

    Keyword Arguments:
        session (fastf1.core.Session) - session to be loaded
    """

    if(session is None):
        raise Exception("Must supply a session")

    session.load()

    return session

def get_drivers_from_session(session=None):
    """ Get a list of the drivers that participated in the specified session

    Keyword Arguments:
        session (fastf1.core.Session) - session to get list of drivers from
    """

    if(session is None):
        raise Exception("Must supply a session")

    return {list(session.results.FullName)[i]: list(session.results.DriverNumber)[i] for i in range(len(list(session.results.FullName)))}

def get_driver_telemetry(driver=1, session=None):
    """ Get a driver's telemetry of all laps in the session

    Keyword Arguments:
        driver (int or str) - driver name or number
        session (fastf1.core.Session) - session to get telemetry from
    """

    if(session is None):
        raise Exception("Must supply a session")

    d = session.laps.pick_driver(driver)

    return d.get_telemetry()

def get_driver_fastest_lap_telemetry(driver=1, session=None):
    """ Get the telemetry for the fastest lap from a driver in the session

    Keyword Arguments:
        driver (int or str) - driver name or number
        session (fastf1.core.Session) - session to get telemetry from
    """

    if(session is None):
        raise Exception("Must supply a session")

    d = session.laps.pick_driver(driver)

    return d.pick_fastest().get_telemetry()

def get_all_telemetry(session=None):
    """ Get the telemetry for all drivers and all laps in a session

    Keyword Arguments:
        session (fastf1.core.Session) - session to get telemetry from
    """

    if(session is None):
        raise Exception("Must supply a session")

    # Dictionary to store driver : telemetry pairs
    telemetries = {}

    # Loop through drivers and retrieve all of their telemetries
    drivers = get_drivers_from_session(session)
    for driver in drivers:
        telemetries[driver] = session.laps.pick_driver(drivers.get(driver)).get_telemetry()

    return telemetries

def get_track_from_session(session=None):
    """ Get the location of the track driven on during the session

    Keyword Arguments:
        session (fastf1.core.Session) - session to get track from
    """

    if(session is None):
        raise Exception("Must supply a session")

    return session.event.Location

def get_track_from_event(event=None):
    """ Get the location of the track driven on during the event

    Keyword Arguments:
        event (fastf1.events.Event) - event to get track from
    """

    if(event is None):
        raise Exception("Must supply an event")

    return event.Location

def get_track_geospatial(trackname=None):
    """ Get the geospatial data for the track from https://github.com/TUMFTM/racetrack-database

    Keyword Arguments:
        trackname (str) - name of the track
    """
    if(trackname is None):
        raise Exception("Must supply track name")

    return pd.read_csv(f"https://raw.githubusercontent.com/TUMFTM/racetrack-database/master/tracks/{trackname.replace(' ', '').title()}.csv")

def get_track_edges(data=None):
    """ Use helper function from https://github.com/TUMFTM/trajectory_planning_helpers to turn data into track edges.
    Entire solution comes from TUMFTM and Alexander Heilmeier.

    Keyword Arguments:
        data (pd.DataFrame) - data containing middle line, right width, and left width of track
    """

    if(data is None):
        raise Exception("Must supply data")

    track_imp = np.array(data)
    track_imp_cl = np.vstack((track_imp, track_imp[0]))
    el_lengths_imp_cl = np.sqrt(np.sum(np.power(np.diff(track_imp_cl[:, :2], axis=0), 2), axis=1))

    normvecs_normalized_imp = calc_splines(path=track_imp_cl[:, :2],
                                            el_lengths=el_lengths_imp_cl,
                                            use_dist_scaling=True)[3]
    normvecs_normalized_imp_cl = np.vstack((normvecs_normalized_imp, normvecs_normalized_imp[0]))

    # calculate boundaries
    bound_right_imp_cl = track_imp_cl[:, :2] + normvecs_normalized_imp_cl * np.expand_dims(track_imp_cl[:, 2], 1)
    bound_left_imp_cl = track_imp_cl[:, :2] - normvecs_normalized_imp_cl * np.expand_dims(track_imp_cl[:, 3], 1)

    bounds = pd.DataFrame(np.concatenate((bound_left_imp_cl, bound_right_imp_cl), axis=1))
    bounds.columns = ["outside_x", "outside_y", "inside_x", "inside_y"]

    return bounds

def get_elapsed_seconds(telemetry=None):
    """ For each entry in telemetry, get the number of seconds since the first entry

    Keyword Arguments:
        telemetry (fastf1.core.Telemetry) - telemetry data
    """

    if(telemetry is None):
        raise Exception("Must supply telemetry")

    # Store initial time
    init_time = telemetry.SessionTime.iloc[0]

    seconds_from_start = []
    # Calculate the number of seconds since initial time for each time
    for time in telemetry.SessionTime:
        seconds_from_start.append((time-init_time).total_seconds())

    return seconds_from_start

def get_telemetry_in_intervals(telemetry=None, interval=0.1, until=None, session=None):
    """ Convert telemetry data to have points at specified intervals

    Keyword Arguments:
        telemetry (fastf1.core.Telemetry) - telemetry data
        interval (float) - desired time in seconds between each datapoint
        until (float or str) - end time in number of seconds from start or string describing end point ("data_end" or "session_end")
        session (fastf1.core.Session) - session to get end time from (only needed if until is "session_end")
    """

    if(telemetry is None):
        raise Exception("Must supply telemetry")

    if(until is None):
        until = "data_end"

    if(until == "session_end" and session is None):
        raise Exception("Must supply session when until == \"session_end\"")

    # Get elapsed seconds if not already provided
    if("ElapsedSeconds" not in telemetry.columns):
        telemetry["ElapsedSeconds"] = get_elapsed_seconds(telemetry)

    # Get end time based on until value
    if(until == "data_end"):
        end = list(telemetry["ElapsedSeconds"])[-1]
    elif(until == "session_end"):
        end = get_session_length(session)
    elif(isinstance(until, float) or isinstance(until, int)):
        end = until
    else:
        raise Exception("Invalid value specified for until")

    telemetry.reset_index(drop=True, inplace=True)

    # Get times separated by interval as list
    intervals = np.arange(0, end, interval)

    # Numeric columns
    num_cols = ["X", "Y"]#, "Throttle", "RPM", "Speed"]
    # Categorical columns
    cat_cols = []#"Brake", "nGear", "Status"]

    # Dictionary that contains all new columns
    interval_telemetry = {key:[] for key in ["ElapsedSeconds"]+num_cols+cat_cols}

    cur_index = 0
    for interval in intervals:
        if(interval % 50 == 0):
            print((interval/end)*100)
        # Iterate through the dataframe for each interval (with minimum index to reduce size)
        for index in telemetry[cur_index:].index:
            if(telemetry.iloc[index]["ElapsedSeconds"] > interval):
                # Handle numeric columns with weighted averaging
                for col in num_cols:
                    interval_telemetry[col] += [timing_weighted_average(
                                                                       interval,
                                                                       list(telemetry["ElapsedSeconds"])[index-1] if index != 0 else 0,
                                                                       telemetry.iloc[index]["ElapsedSeconds"],
                                                                       list(telemetry[col])[index-1],
                                                                       telemetry.iloc[index][col]
                    )]
                # Handle categorical columns by maintaining previous value
                for col in cat_cols:
                    interval_telemetry[col] += [list(telemetry[col])[index-1]]

                # Update ElapsedSeconds and current index, then break because values were found
                interval_telemetry["ElapsedSeconds"] += [interval]
                cur_index = index
                break

            # If the end of the data has been reached, continue apppending the most recent data
            elif(all(float(k) < interval for k in list(telemetry["ElapsedSeconds"].iloc[cur_index:])) and interval < end):
                for col in num_cols+cat_cols:
                    interval_telemetry[col] += [telemetry.iloc[index][col]]
                interval_telemetry["ElapsedSeconds"] += [interval]
                break

    return pd.DataFrame(interval_telemetry).reset_index(drop=True)

def timing_weighted_average(cur_time, old_time, new_time, old_val, new_val):
    """ Calculate an average weighted based on the amount of time between current point and next

    Keyword Arguments:
        cur_time (float) - currently elapsed time
        old_time (float) - elapsed time of previous point
        new_time (float) - elapsed time of next point
        old_val (float) - value at time of previous point
        new_val (float) - value at time of next point
    """

    # Calculate difference between old/new times and current time
    old_diff = cur_time-old_time
    new_diff = new_time-cur_time

    # Return the weighted average - assigning more weight to the closer time
    return ((old_diff*new_val) + (new_diff*old_val))/((old_diff+new_diff))

def get_overall_fastest(session=None):
    """ Get the fastest lap from the session

    Keyword Arguments:
        session (fastf1.core.Session) - session to get fastest lap from
    """
    if(session is None):
        raise Exception("Must supply a session")

    return session.laps.pick_fastest().get_telemetry()

def get_session_length(session=None):
    """ Get the total amount of time that the session took to complete

    Keyword Arguments:
        session (fastf1.core.Session) - session to get time from
    """
    if(session is None):
        raise Exception("Must supply a session")

    return session.results.Time.iloc[0].total_seconds()

def get_driver_color(name=None):
    """ Get the driver color as a hex code

    Keyword Arguments:
        name (str) - name of the driver
    """

    if(name is None):
        raise Exception("Must supply driver name")

    return fastf1.plotting.driver_color(name)

def get_team_color(name=None, session=None):
    """ Get the driver's team color as a hex code

    Keyword Arguments:
        name (str) - name of the driver
        session (fastf1.core.Session) - session to get color from
    """

    if(name is None):
        raise Exception("Must supply driver name")

    if(session is None):
        raise Exception("Must supply a session")

    return "#" + session.results[session.results["FullName"] == name]["TeamColor"].iloc[0]

def get_track_fit_values(track_name):
    """ Returns values used to fit car positional data to track bound data.
    Returned as (div_x, div_y, diff_x, diff_y)
    Where div variables are the value to divide the column by and diff variables
    are the values to add to the column. Divide first, then add.

    Keyword Arguments:
        track_name (str) - name of the track to fit the data to
    """
    # Values must be manually calculated and added to dictionary because of
    # unpredictability in track layout and driver behavior
    fit_dict = {
                "spielberg":(10.05, 10.05, -130, 115),
                "catalunya":(10.05, 10.05, -90, 30)
    }

    return fit_dict.get(track_name.lower())

# Testing functions
if __name__ == "__main__":
    cache()
    #display_schedule(get_schedule(2022))
    session = get_session_from_event(event=get_event(2022, 11))
    load_session_data(session)
    #print(get_session_length(session))
    #drivers = get_drivers_from_session(session)
    #print(drivers)
    #print(get_driver_color(list(drivers.keys())[0]))
    #print(get_driver_telemetry(driver=drivers.get(list(drivers.keys())[0]), session=session))
    #telem = get_driver_fastest_lap_telemetry(driver=drivers.get(list(drivers.keys())[0]), session=session)
    #telem["ElapsedSeconds"] = get_elapsed_seconds(telem)
    #print(telem)
    #print(get_overall_fastest(session))
    #print(get_all_telemetry(session=session))
    #print(get_telemetry_in_intervals(telem))
    print(get_team_color("Carlos Sainz", session=session))
    #sainz = get_driver_telemetry(driver=55, session=session)
    #print(sainz)
    #print(get_telemetry_in_intervals(sainz, interval=0.5, until="session_end", session=session).tail(20))
