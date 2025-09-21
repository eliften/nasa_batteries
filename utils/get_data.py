import scipy.io,pandas as pd, datetime, numpy as np


class getData:
    def __init__(self, path):
        self.mat = scipy.io.loadmat(path)
        self.data = {"cycle_id": [], "type": [], "ambient_temperature": [], "date_time": [], "voltage_measured": [], "current_measured": [], "temperature_measured": [], "current_charge": [], "voltage_charge": [], "time": [], "capacity": []}

    def parse_data(self):
        id = 0
        key = list(self.mat.keys())[3]
        for i in range(len(self.mat[key][0, 0]['cycle'][0])):
            row = self.mat[key][0, 0]['cycle'][0, i]
            d = row["data"]

            cycle_type = row['type'][0]
            ambient_temp = row['ambient_temperature'][0][0] if row['ambient_temperature'].size else None
            date_time = datetime.datetime(int(row['time'][0][0]),
                                int(row['time'][0][1]),
                                int(row['time'][0][2]),
                                int(row['time'][0][3]),
                                int(row['time'][0][4])) + datetime.timedelta(seconds=int(row['time'][0][5]))

            if cycle_type in ['discharge']:
                id += 1
                n = len(d[0][0]['Voltage_measured'][0])

                for j in range(n):
                    self.data['cycle_id'].append(id)
                    self.data['type'].append(cycle_type)
                    self.data['ambient_temperature'].append(ambient_temp)
                    self.data['date_time'].append(date_time)

                    self.data['voltage_measured'].append(d[0][0]['Voltage_measured'][0][j])
                    self.data['current_measured'].append(d[0][0]['Current_measured'][0][j])
                    self.data['temperature_measured'].append(d[0][0]['Temperature_measured'][0][j])

                    try:
                        self.data['current_charge'].append(d[0][0]['Current_charge'][0][j])
                    except ValueError:
                        self.data['current_charge'].append(d[0][0]['Current_load'][0][j])

                    try:
                        self.data['voltage_charge'].append(d[0][0]['Voltage_charge'][0][j])
                    except ValueError:
                        self.data['voltage_charge'].append(d[0][0]['Voltage_load'][0][j])

                    self.data['time'].append(d[0][0]['Time'][0][j])

                    if cycle_type == 'charge':
                        self.data['capacity'].append(None)
                    else:
                        try:
                            self.data['capacity'].append(d[0][0]['Capacity'][0][0])
                        except:
                            self.data['capacity'].append(None)
        return self.data


    def feature_eng(self, data):
        data = pd.DataFrame(data)
        data["dt_s"] = (
            data.groupby("cycle_id")["time"]
            .diff()
            .clip(lower=0)
            .fillna(0)
        )
        data["dQ_Ah"] = (-data["current_measured"]) * data["dt_s"] / 3600.0
        data["Q_cum_Ah"] = data.groupby("cycle_id")["dQ_Ah"].cumsum().fillna(0.0)
        data["dV_dt"] = data.groupby("cycle_id")["voltage_measured"].diff() / data["dt_s"]
        data["dV_dt"] = data["dV_dt"].replace([np.inf, -np.inf], 0).fillna(0)

        return data



