import secrets, requests
from flask_session import Session
from dash.exceptions import PreventUpdate
from flask import Flask, session, make_response
from flask import session as flask_session
from tempfile import mkdtemp
from dash import Dash, html, Output, Input, callback, State, dcc, ctx
import dash_bootstrap_components as dbc
from pages import dashboard,sidebar,add_mqtt
from db import create_db
from utils import get_data
from  datetime import datetime

server = Flask(__name__)
server.config["SESSION_TYPE"] = "filesystem"
server.config["SESSION_FILE_DIR"] = mkdtemp()
server.config["SECRET_KEY"] = secrets.token_hex(24)
Session(server)

app = Dash(
    external_stylesheets=[
        dbc.themes.LITERA,
        "https://fonts.googleapis.com/css?family=Poppins",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css",
    ],
    server=server,
    suppress_callback_exceptions=True,
    title="State of Charge Prediction Dashboard",
)

def layout_content():
    return html.Div(
        className="content",
        children=[
            dcc.Location(id="url", refresh=True),
            html.Div(id="page-content"),
            dcc.Store(id='soc-results-store'),
            dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
        ],
    )


layout_main = html.Div([
    dcc.Location(id="url", refresh=True),
    html.Div(
        id="page-content",
        style={
            "backgroundColor": "#f0f0f0",
            "minHeight": "100vh",
            "padding": "20px" 
        }
    )
])


app.layout = html.Div([layout_main])

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    allow_duplicate=True,
)
def display_page(pathname):
    if pathname == "/dashboard":
        return [sidebar.sidebar, dashboard.dashboard()]
    if pathname == "/add_mqtt":
        return [sidebar.sidebar, add_mqtt.layout]

if __name__ == "__main__":
    create_db.create_table()
    data_processor = get_data.getData("data/B0005.mat")
    raw_data = data_processor.parse_data()
    processed_data = data_processor.feature_eng((raw_data))
    processed_data["data_type"] = "train"
    today  = datetime.now().date()
    processed_data["added_date"] = today
    create_db.insert_dataframe_to_db(processed_data)
    app.run(debug=True, host="0.0.0.0", port=8010)
