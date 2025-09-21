from dash import html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import json
import os

JSON_FILE = "mqtt_config.json"

layout = dbc.Container([
    html.H2("MQTT Bağlantı Bilgileri", className="mt-4 mb-4", style={'margin-left': '200px'}),

    dbc.Card(
        dbc.CardBody([
            dbc.Form([
                dbc.Row([
                    dbc.Label("Batarya Adı", width=3),
                    dbc.Col(dbc.Input(id="battery-name", placeholder="Batarya adı girin", type="text"), width=9),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Label("Host", width=3),
                    dbc.Col(dbc.Input(id="mqtt-host", placeholder="MQTT host adresi", type="text"), width=9),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Label("Port", width=3),
                    dbc.Col(dbc.Input(id="mqtt-port", placeholder="MQTT port numarası", type="number"), width=9),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Label("Kullanıcı Adı", width=3),
                    dbc.Col(dbc.Input(id="mqtt-username", placeholder="Kullanıcı adı", type="text"), width=9),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Label("Şifre", width=3),
                    dbc.Col(dbc.Input(id="mqtt-password", placeholder="Şifre", type="password"), width=9),
                ], className="mb-3"),
                
                dbc.Button("Kaydet", id="save-btn", color="primary"),
                html.Div(id="save-output", className="mt-3")
            ])
        ]), style={'margin-left': '200px', 'width': '1200px'},
        className="shadow-sm",
    )
], fluid=True)


@callback(
    Output("save-output", "children"),
    Input("save-btn", "n_clicks"),
    State("mqtt-host", "value"),
    State("mqtt-port", "value"),
    State("mqtt-username", "value"),
    State("mqtt-password", "value"),
)
def save_mqtt_config(n_clicks, host, port, username, password):
    if not n_clicks:
        return ""
    
    if not all([host, port]):
        return dbc.Alert("Host ve Port bilgisi zorunludur!", color="danger")
    
    config_data = {
        "host": host,
        "port": port,
        "username": username,
        "password": password
    }
    
    try:
        with open(JSON_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
        return dbc.Alert(f"MQTT bilgileri {JSON_FILE} dosyasına kaydedildi.", color="success")
    except Exception as e:
        return dbc.Alert(f"Hata oluştu: {e}", color="danger")
