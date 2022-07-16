import f1_helper_functions as f1help
import plotly.graph_objects as go
import time

def proof_of_concept_plot():
    f1help.cache()
    session = f1help.get_session_from_event(f1help.get_event(2022, 11), "Race")
    f1help.load_session_data(session)
    
    data = f1help.get_driver_fastest_lap_telemetry(driver=44, session=session)

    data["ElapsedTime"] = f1help.get_elapsed_seconds(data)
    data = f1help.get_telemetry_in_intervals(data, 0.05)

    trackname = f1help.get_track_from_session(session)
    track = f1help.get_track_geospatial(trackname)
    bounds = f1help.get_track_edges(track)

    data["X"] = (data["X"] - list(data["X"])[0]-150)/10
    data["Y"] = (data["Y"] - list(data["Y"])[0]-100)/10

    fastest_lap = f1help.get_overall_fastest(session)

    drivers = f1help.get_drivers_from_session(session)

    driver_data = f1help.get_all_telemetry(session)
    """
    for driver in list(driver_data.keys())[:1]:
        print(driver)
        d = driver_data.get(driver)
        d = f1help.get_telemetry_in_intervals(d, 0.1, until="data_end", session=session)
        print(d)
        d["X"] = (d["X"]-list(fastest_lap["X"])[0] - 150)/10
        d["Y"] = (d["Y"]-list(fastest_lap["Y"])[0] - 150)/10
        print(f"{driver} done")
    print(driver_data.get(list(driver_data.keys())[0]).head(20))"""

    fig = go.Figure(
                    data=[
                          go.Scatter(
                                     x=bounds["outside_x"],
                                     y=bounds["outside_y"],
                                     mode="lines",
                                     line_color="rgba(85, 85, 85, 0)",
                                     line_width=2,
                                     #fill="toself",
                                     #fillcolor="rgba(170,170,170,.5)"
                          ),
                          go.Scatter(
                                     x=bounds["outside_x"],
                                     y=bounds["outside_y"],
                                     mode="lines",
                                     line_color="rgba(85, 85, 85, .6)",
                                     line_width=2,
                                     #fill="toself",
                                     #fillcolor="rgba(170,170,170,.5)"
                          ),
                          go.Scatter(
                                     x=bounds["inside_x"],
                                     y=bounds["inside_y"],
                                     mode="lines",
                                     line_color="rgba(85, 85, 85, .6)",
                                     line_width=2,
                                     #fill="toself",
                                     #fillcolor="#ffffff"
                          ),
                          go.Scatter(
                                     x=[data["X"].iloc[0]],
                                     y=[data["Y"].iloc[0]],
                                     mode="markers",
                                     visible=False
                          )
                    ],
                    layout=go.Layout(
                                     height=900,
                                     width=1350,
                                     template="simple_white",
                                     showlegend=False,
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
                                                                  {"frame": {"duration":50, "redraw":False}}
                                                                  ]
                                                       )
                                                   ]
                                                  }
                                     ]
                    ),
                    frames=[go.Frame(
                                     data=[
                                           go.Scatter(
                                                  x=[data["X"].iloc[i]],
                                                  y=[data["Y"].iloc[i]],
                                                  mode="markers",
                                                  marker=dict(size=[10],color=[f"rgba({int(data['Brake'].iloc[i])*255}, {data['Throttle'].iloc[i]*2.55}, 0, .6)"])
                                           )
                                    ]
                    ) for i in range(len(data["X"]))]

          )

    fig.show()


if __name__ == "__main__":
    proof_of_concept_plot()
