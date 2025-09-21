from dash import html, dcc, callback, Output, Input
import requests
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from collections import deque
import dash_bootstrap_components as dbc

voltage_history = deque(maxlen=50)
temperature_history = deque(maxlen=50)
capacity_history = deque(maxlen=50)
current_history = deque(maxlen=50)
soc_history = deque(maxlen=50)

def dashboard():
    return html.Div(children=[
        html.Br(),

        dbc.Row(
            justify="start",
            children=[
                html.Div(
                    id="soc-display",
                    style={
                        "width": "200px",
                        "height": "200px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "fontSize": "30px",
                        "fontWeight": "bold",
                        "margin-left": "200px",
                        'margin-top':'10px',
                        "color": "black",
                        "borderRadius": "40px",
                        "backgroundColor": "white",
                        "boxShadow": "0 0 20px gray",
                        "transition": "all 0.5s"
                    },
                )
            ]
        ),

        dbc.Row(
            justify="start",
            children=[
                dbc.Card(
                    dbc.CardBody(dcc.Graph(id="voltage-graph", style={'height': '400px'})),
                    style={'margin-left': '200px', 'margin-top':'10px', 'width': '1200px'}
                )
            ]
        ),
        dbc.Row(
            justify="start",
            children=[
                dbc.Card(
                    dbc.CardBody(dcc.Graph(id="temperature-graph", style={'height': '400px'})),
                    style={'margin-left': '200px', 'margin-top':'10px', 'width': '1200px'}
                )
            ]
        ),
        dbc.Row(
            justify="start",
            children=[
                dbc.Card(
                    dbc.CardBody(dcc.Graph(id="capacity-graph", style={'height': '400px'})),
                    style={'margin-left': '200px', 'margin-top':'10px', 'width': '1200px'}
                )
            ]
        ),
        dbc.Row(
            justify="start",
            children=[
                dbc.Card(
                    dbc.CardBody(dcc.Graph(id="current-graph", style={'height': '400px'})),
                    style={'margin-left': '200px', 'margin-top':'10px', 'width': '1200px'}
                )
            ]
        ),

        dcc.Interval(
            id="interval-component",
            interval=2000,
            n_intervals=0
        )
    ])



prev_soc = None

@callback(
    Output("soc-display", "children"),
    Output("soc-display", "style"),
    Output("voltage-graph", "figure"),
    Output("temperature-graph", "figure"),
    Output("capacity-graph", "figure"),
    Output("current-graph", "figure"),
    Input("interval-component", "n_intervals")
)
def update_soc(n):
    global prev_soc
    try:
        resp = requests.get("http://api_server:5000/latest_soc", timeout=5).json()
        soc = resp.get("latest_soc")
        data = resp.get("data")
        batarya = resp.get("battery_name")
        print(batarya)

        if soc is None or data is None:
            raise PreventUpdate

        if soc != prev_soc:
            prev_soc = soc

        if soc >= 70:
            shadow_color = "green"
        elif soc >= 30:
            shadow_color = "goldenrod"
        else:
            shadow_color = "darkred"

        style = {
            "width": "200px",
            "height": "200px",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "fontSize": "30px",
            "fontWeight": "bold",
            "margin-left": "200px",
            "color": "black",
            "borderRadius": "40px",
            "backgroundColor": "white",
            "boxShadow": f"0 0 20px {shadow_color}",
            "transition": "all 0.5s"
        }

        voltage_measured = data.get("voltage_measured")
        temperature_measured = data.get("temperature_measured")
        capacity = data.get("capacity")
        current_measured = data.get("current_measured")
        print(capacity)

        if voltage_measured is not None:
            voltage_history.append(voltage_measured)
            soc_history.append(soc)
        if temperature_measured is not None:
            temperature_history.append(temperature_measured)
        if capacity is not None:
            capacity_history.append(capacity)
        if current_measured is not None:
            current_history.append(current_measured)

        fig_voltage = go.Figure()
        fig_voltage.add_trace(go.Scatter(
            y=list(voltage_history),
            mode="lines+markers",
            name="Voltage Measured",
            line=dict(color="blue")
        ))
        fig_voltage.update_layout(
            title="Voltage Measured (Son 50 veri)",
            xaxis_title="Zaman (Son veri sayısı)",
            yaxis_title="Voltage (V)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )

        fig_voltage.update_xaxes(showgrid=False, zeroline=False)
        fig_voltage.update_yaxes(showgrid=False, zeroline=False)

        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            y=list(temperature_history),
            mode="lines+markers",
            name="Temperature Measured",
            line=dict(color="red")
        ))
        fig_temp.update_layout(
            title="Temperature Measured (Son 50 veri)",
            xaxis_title="Zaman (Son veri sayısı)",
            yaxis_title="Temperature (°C)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )


        fig_temp.update_xaxes(showgrid=False, zeroline=False)
        fig_temp.update_yaxes(showgrid=False, zeroline=False)

        fig_capacity = go.Figure()
        fig_capacity.add_trace(go.Scatter(
            y=list(capacity_history),
            mode="lines+markers",
            name="Capacity",
            line=dict(color="orange")
        ))
        fig_capacity.update_layout(
            title="Capacity (Son 50 veri)",
            xaxis_title="Zaman (Son veri sayısı)",
            yaxis_title="Capacity",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )

        fig_capacity.update_xaxes(showgrid=False, zeroline=False)
        fig_capacity.update_yaxes(showgrid=False, zeroline=False)

        fig_current = go.Figure()
        fig_current.add_trace(go.Scatter(
            y=list(current_history),
            mode="lines+markers",
            name="Current Measured",
            line=dict(color="green")
        ))
        fig_current.update_layout(
            title="Current Measured (Son 50 veri)",
            xaxis_title="Zaman (Son veri sayısı)",
            yaxis_title="Current (A)",
            template="plotly_white",
            margin=dict(l=20, r=20, t=40, b=20)
        )

        fig_current.update_xaxes(showgrid=False, zeroline=False)
        fig_current.update_yaxes(showgrid=False, zeroline=False)

        return f"SOC: {float(soc):.2f} %", style, fig_voltage, fig_temp, fig_capacity, fig_current

    except:
        raise PreventUpdate
