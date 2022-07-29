import f1_helper_functions as f1help
import plotly.graph_objects as go
import time
import pickle as pkl
import os

def prep_session(year, gp, event):

    session = f1help.get_session_from_event(f1help.get_event(year, gp), event)

    f1help.load_session_data(session)

    return session

def prep_plotting_data(year, gp, event, interval=.2):

    session = prep_session(year, gp, event)

    track_outline = f1help.get_overall_fastest(session)

    drivers = f1help.get_drivers_from_session(session)
    driver_data = None

    data_filepath=f"race_data/{year}_{gp}_{event}.pkl"
    # Load Data
    if(data_filepath in os.listdir()):
        with open(data_filepath, "rb") as f:
            driver_data = pkl.load(f)
    else:
        driver_data = f1help.get_all_telemetry(session)

        for driver in driver_data:
            print(driver)
            d = driver_data.get(driver)
            d = f1help.get_telemetry_in_intervals(d, interval, until="session_end", session=session)
            d["MarkerColor"].fillna(f1help.get_team_color(driver, session), inplace=True)
            print(f"{driver} done")
            driver_data[driver] = d


        # Save Data
        with open(data_filepath, "wb+") as f:
            pkl.dump(driver_data, f)

    return track_outline, driver_data

def plot(track_outline, driver_data):
    fig = go.Figure(
                    data=[go.Scatter(
                               x=fastest_lap["X"],
                               y=fastest_lap["Y"],
                               mode="lines",
                               line_color="rgba(85, 85, 85, 0)",
                               line_width=6,
                               hoverinfo="skip"
                    ) for i in driver_data] + [
                          go.Scatter(
                                     x=fastest_lap["X"],
                                     y=fastest_lap["Y"],
                                     mode="lines",
                                     line_color="rgba(85, 85, 85, .6)",
                                     line_width=4,
                                     hoverinfo="skip"
                          ),
                          go.Scatter(
                                     x=[0],
                                     y=[0],
                                     mode="markers",
                                     hoverinfo="skip",
                                     visible=False
                          )
                    ],
                    layout=go.Layout(
                                     height=900,
                                     width=1350,
                                     template="simple_white",
                                     showlegend=False,
                                     margin={"r":10, "t":10, "l":10, "b":10},
                                     xaxis={
                                            "visible":False
                                     },
                                     yaxis={
                                            "visible":False
                                     },
                                     updatemenus=[
                                                  {
                                                   "type":"buttons",
                                                   "buttons":[
                                                       dict(
                                                            label="Play",
                                                            method="animate",
                                                            args=[None,
                                                                  {"frame": {"duration":interval*1000, "redraw":False},
                                                                   "transition": {"duration":interval*1000, "easing":"linear"}}
                                                                  ]
                                                       )
                                                   ]
                                                  }
                                     ]
                    ),
                    frames=[go.Frame(
                                     data=[
                                           go.Scatter(
                                                  x=[d["X"].iloc[i]],
                                                  y=[d["Y"].iloc[i]],
                                                  text=driver,
                                                  hoverinfo = "text",
                                                  mode="markers",
                                                  marker=dict(size=[15], color=[d["MarkerColor"].iloc[i]])
                                           ) for driver, d in driver_data.items()
                                    ]
                    ) for i in range(len(driver_data.get(list(driver_data.keys())[0])["X"]))]

          )

    return fig

def proof_of_concept_plot():
    f1help.cache()
    year=2022
    gp=9
    event="Race"
    session = f1help.get_session_from_event(f1help.get_event(year, gp), event)
    f1help.load_session_data(session)

    """data = f1help.get_driver_fastest_lap_telemetry(driver=44, session=session)

    data["ElapsedTime"] = f1help.get_elapsed_seconds(data)
    data = f1help.get_telemetry_in_intervals(data, 0.05)"""

    trackname = f1help.get_track_from_session(session)
    """track = f1help.get_track_geospatial(trackname)
    bounds = f1help.get_track_edges(track)"""


    """div_x, div_y, diff_x, diff_y = f1help.get_track_fit_values(trackname)
    print(div_x, div_y, diff_x, diff_y)"""
    div_x = 1
    div_y = 1
    diff_x = 0
    diff_y = 0

    """data["X"] = (data["X"] - list(data["X"])[0]-150)/10
    data["Y"] = (data["Y"] - list(data["Y"])[0]-100)/10"""

    fastest_lap = f1help.get_overall_fastest(session)

    drivers = f1help.get_drivers_from_session(session)
    driver_data = None
    interval = .2

    data_filepath=f"race_data/{year}_{gp}_{event}.pkl"
    # Load Data
    if(data_filepath in os.listdir()):
        with open(data_filepath, "rb") as f:
            driver_data = pkl.load(f)
    else:
        driver_data = f1help.get_all_telemetry(session)

        for driver in driver_data:
            print(driver)
            d = driver_data.get(driver)
            d = f1help.get_telemetry_in_intervals(d, interval, until="session_end", session=session)
            d["MarkerColor"].fillna(f1help.get_team_color(driver, session), inplace=True)
            print(f"{driver} done")
            driver_data[driver] = d


        # Save Data
        with open(data_filepath, "wb+") as f:
            pkl.dump(driver_data, f)

    data = driver_data.get(list(driver_data.keys())[0])

    print(driver_data)

    driver_team_colors = {driver: f1help.get_team_color(driver, session) for driver in driver_data}
    print(driver_team_colors)

    fig = go.Figure(
                    data=[go.Scatter(
                               x=fastest_lap["X"],
                               y=fastest_lap["Y"],
                               mode="lines",
                               line_color="rgba(85, 85, 85, 0)",
                               line_width=6,
                               hoverinfo="skip",
                               #fill="toself",
                               #fillcolor="rgba(170,170,170,.5)"
                    ) for i in driver_data] + [
                          #go.Scatter(
                            #         x=bounds["outside_x"],
                            #         y=bounds["outside_y"],
                            #         mode="lines",
                            #         line_color="rgba(85, 85, 85, .6)",
                            #         line_width=2,
                                     #fill="toself",
                                     #fillcolor="rgba(170,170,170,.5)"
                          #),
                          #go.Scatter(
                            #         x=bounds["inside_x"],
                            #         y=bounds["inside_y"],
                            #         mode="lines",
                            #         line_color="rgba(85, 85, 85, .6)",
                            #         line_width=2,
                                     #fill="toself",
                                     #fillcolor="#ffffff"
                          #),
                          go.Scatter(
                                     x=fastest_lap["X"],
                                     y=fastest_lap["Y"],
                                     mode="lines",
                                     line_color="rgba(85, 85, 85, .6)",
                                     line_width=4,
                                     hoverinfo="skip"
                                     #fill="toself",
                                     #fillcolor="rgba(170,170,170,.5)"
                          ),
                          go.Scatter(
                                     x=[0],
                                     y=[0],
                                     mode="markers",
                                     hoverinfo="skip",
                                     visible=False
                          )
                    ],
                    layout=go.Layout(
                                     height=900,
                                     width=1350,
                                     template="simple_white",
                                     showlegend=False,
                                     margin={"r":10, "t":10, "l":10, "b":10},
                                     xaxis={
                                            "visible":False
                                     },
                                     yaxis={
                                            "visible":False
                                     },
                                     updatemenus=[
                                                  {
                                                   "type":"buttons",
                                                   "buttons":[
                                                       dict(
                                                            label="Play",
                                                            method="animate",
                                                            args=[None,
                                                                  {"frame": {"duration":interval*1000, "redraw":False},
                                                                   "transition": {"duration":interval*1000, "easing":"linear"}}
                                                                  ]
                                                       )
                                                   ]
                                                  }
                                     ]
                    ),
                    frames=[go.Frame(
                                     data=[
                                           go.Scatter(
                                                  x=[d["X"].iloc[i]],
                                                  y=[d["Y"].iloc[i]],
                                                  text=driver,
                                                  hoverinfo = "text",
                                                  mode="markers",
                                                  marker=dict(size=[15], color=[d["MarkerColor"].iloc[i]])
                                           ) for driver, d in driver_data.items()
                                    ]
                    ) for i in range(len(data["X"]))]

          )

    fig.show()
    fig.write_html(f"html_races/{year}_{gp}_{event}.html")


if __name__ == "__main__":
    proof_of_concept_plot()
