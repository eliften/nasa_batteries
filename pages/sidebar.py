from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc


sidebar = dbc.Nav(
    [
        html.Br(),
        html.Br(),
        dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
        dbc.NavItem(dbc.NavLink("Connect MQTT", href="/add_mqtt"))
    ],
    vertical=True,
    pills=True,
    className="sidebar"
)