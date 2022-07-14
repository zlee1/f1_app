import fastf1
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


if __name__ == "__main__":
    cache()
    #display_schedule(get_schedule(2022))
    session = get_session_from_event(event=get_event(2022, 11))
    load_session_data(session)
    drivers = get_drivers_from_session(session)
    print(drivers)
    #print(get_driver_telemetry(driver=drivers.get(list(drivers.keys())[0]), session=session))
    print(get_driver_fastest_lap_telemetry(driver=drivers.get(list(drivers.keys())[0]), session=session))
