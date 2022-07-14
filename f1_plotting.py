import f1_helper_functions as f1help
import plotly.graph_objects as go
import time

def proof_of_concept_plot():
    f1help.cache()
    session = f1help.get_session_from_event(f1help.get_event(2022, 11), "Race")
    f1help.load_session_data(session)
    data = f1help.get_driver_fastest_lap_telemetry(driver=44, session=session)

    data["elapsed_time"] = f1help.get_elapsed_seconds(data)
    print(data.columns)
    trackname = f1help.get_track_from_session(session)
    track = f1help.get_track_geospatial(trackname)
    bounds = f1help.get_track_edges(track)
    print(bounds)

    data["X"] = (data["X"] - list(data["X"])[0]-150)/10
    data["Y"] = (data["Y"] - list(data["Y"])[0]-100)/10

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
                                                                  {"frame": {"duration":100, "redraw":False}}
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
                                                  marker=dict(size=[10],color=["rgba(255, 0, 0, .6)"])
                                           )
                                    ]
                    ) for i in range(len(data["X"]))]

          )

    #fig.add_trace(go.Scatter(x=bounds["outside_x"], y=bounds["outside_y"], mode="lines", line_color="#222222", line_width=2, fill="toself", fillcolor="rgba(200,200,200,.5)"))
    #fig.add_trace(go.Scatter(x=bounds["inside_x"], y=bounds["inside_y"], mode="lines", line_color="#222222", line_width=2, fill="toself", fillcolor="#ffffff"))
    #fig.add_trace(go.Scatter(x=data["X"], y=data["Y"], mode="lines", line_width=2))

    #fig.update_layout(template="simple_white")
    #fig.update_layout(showlegend=False)
    #fig.update_xaxes(visible=False)
    #fig.update_yaxes(visible=False)

    fig.show()
    #time.sleep(10)


if __name__ == "__main__":
    proof_of_concept_plot()
