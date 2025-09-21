import torch
import torch.nn as nn
import numpy as np
import pickle
import os

class TimeSeriesTransformer(nn.Module):
    def __init__(self, input_size, nhead=4, num_layers=2, dim_feedforward=64, dropout=0.1):
        super(TimeSeriesTransformer, self).__init__()
        self.input_fc = nn.Linear(input_size, dim_feedforward)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=dim_feedforward,
            nhead=nhead,
            dim_feedforward=dim_feedforward*2,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(dim_feedforward, 1)

    def forward(self, x):
        x = self.input_fc(x)
        out = self.transformer(x)
        out = out[:, -1, :]
        out = self.fc_out(out)
        return out


# ---- Model & scaler yükleme ----
input_size = 6
nhead = 4
num_layers = 2
dim_feedforward = 32
dropout = 0.1

model = TimeSeriesTransformer(
    input_size=input_size,
    nhead=nhead,
    num_layers=num_layers,
    dim_feedforward=dim_feedforward,
    dropout=dropout
)

MODEL_PATH = "/app/models/TimeSeriesTransformer_model.pth"


model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

with open("/app/models/scaler_X.pkl", "rb") as f:
    scaler_X = pickle.load(f)

with open("/app/models/scaler_y.pkl", "rb") as f:
    scaler_y = pickle.load(f)


def predict_soc(data, seq_length=40):
    model.eval()
    
    if isinstance(data, dict):
        try:
            X = np.array([[float(data["voltage_measured"]),
                           float(data["current_measured"]),
                           float(data["temperature_measured"]),
                           float(data["Q_cum_Ah"]),
                           float(data["capacity"]),
                           float(data["dV_dt"])]]).astype(np.float32)
        except Exception as e:
            print("Veri tipi hatası:", e, data)
            return None
    else:
        X = data.values.astype(np.float32)
    
    X_scaled = scaler_X.transform(X)
    
    if len(X_scaled) >= seq_length:
        soc_preds = []
        for i in range(len(X_scaled) - seq_length + 1):
            X_seq = X_scaled[i:i+seq_length]
            X_seq_tensor = torch.tensor(X_seq, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                y_pred_scaled = model(X_seq_tensor).item()
            y_pred = scaler_y.inverse_transform([[y_pred_scaled]])[0, 0]
            soc_preds.append(y_pred)
        return soc_preds
    else:
        X_seq_tensor = torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            y_pred_scaled = model(X_seq_tensor).item()
        y_pred = scaler_y.inverse_transform([[y_pred_scaled]])[0, 0]
        return y_pred
