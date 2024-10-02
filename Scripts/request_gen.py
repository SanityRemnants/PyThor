import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime


def validate_data(hour1: int, hour2: int, minute1: int, minute2: int, interval: int, params: list, lat1: float,
                  lat2: float, lon1: float, lon2: float) -> bool:
    if not params:
        return False
    if hour1 > 23 or hour2 > 23 or hour1 < 0 or hour2 < 0:
        return False
    if minute1 > 59 or minute2 > 59 or minute1 < 0 or minute2 < 0:
        return False
    if interval < 0:
        return False
    if lat1 < - 90 or lat2 < -90 or lat1 > 90 or lat2 > 90:
        return False
    if lon1 < -180 or lon2 < -180 or lon1 > 180 or lon2 > 180:
        return False
    return True


def compile_request(params: list, time_start: int, time_end: int, interval: int, lat_start: float, lat_end: float,
                    lon_start: float, lon_end: float, addr: str) -> str:
    api_query = addr + "/api/weather?variables="
    for param in params:
        api_query += param + ','
    api_query = api_query[:-1]
    api_query += "&latitude_start=" + str(lat_start)
    api_query += "&longitude_start=" + str(lon_start)
    api_query += "&latitude_end=" + str(lat_end)
    api_query += "&longitude_end=" + str(lon_end)
    api_query += "&time_start=" + str(time_start) + "&time_end=" + str(time_end)
    api_query += "&interval=" + str(interval)
    print(api_query)
    return api_query


def convertToTimeEpoch(hour: int, minute: int, date: any) -> int:
    res = int(datetime(date.year, date.month, date.day).timestamp())
    res += hour * 3600
    res += minute * 60
    return res


def create_window():
    def create_request():
        selected_params = []
        for option, data in weather_chk.items():
            if data['var'].get():
                selected_params.append(option)

        date_start = cal_start.get_date()
        hour_start = int(hours_start_s.get())
        minute_start = int(minutes_start_s.get())

        date_end = cal_end.get_date()
        hour_end = int(hours_end_s.get())
        minute_end = int(minutes_end_s.get())

        interval = int(interval_e.get())

        lat_start = float(latitude_start_s.get())
        lon_start = float(longitude_start_s.get())

        lat_end = float(latitude_end_s.get())
        lon_end = float(longitude_end_s.get())

        if not validate_data(hour_start, hour_end, minute_start, minute_end, interval, selected_params, lat_start,
                             lat_end, lon_start, lon_end):
            return
        epoch_start = convertToTimeEpoch(hour_start, minute_start, date_start)
        epoch_end = convertToTimeEpoch(hour_end, minute_end, date_end)
        result_t['state'] = 'normal'
        result_t.insert('1.0', compile_request(selected_params, epoch_start, epoch_end, interval, lat_start, lat_end,
                                               lon_start, lon_end, addr_val.get()))
        result_t['state'] = 'disabled'

    # root window
    root = tk.Tk()
    root.title('PyThor Request Generator')

    # root frame
    root_frame = tk.Frame(root)
    root_frame.pack(expand=True, fill='both')

    weather_chk = {}
    weather_params = [
        "wave_direction",
        "wave_height",
        "wave_period",
        "wind_direction",
        "wind_speed",
        "sea_current_speed",
        "sea_current_direction",
        "tide_height",
    ]

    # params frame
    params_frame = tk.Frame(root_frame)
    params_frame.grid(row=0, column=0, sticky='w' + 'e' + 'n', padx=10, pady=10)

    # label
    label = ttk.Label(params_frame, text="Select weather parameters:")
    label.grid(column=0, row=0)

    # radio buttons
    for param in weather_params:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(params_frame, text=param, variable=var)
        chk.grid(sticky="w")
        weather_chk[param] = {'var': var, 'chk': chk}

    # right frame
    right_frame = tk.Frame(root_frame)
    right_frame.grid(row=0, column=1, sticky='w' + 'e' + 'n', padx=10, pady=10)

    # dates frame
    dates_frame = tk.Frame(right_frame)
    dates_frame.grid(row=0, column=0, sticky='w' + 'e' + 'n', padx=10, pady=10)

    cal_start = DateEntry(dates_frame, selectmode='day')
    cal_start.grid(row=0, column=0, sticky="n")

    label = ttk.Label(dates_frame, text="h:")
    label.grid(row=0, column=1)
    hours_start_s = tk.Spinbox(dates_frame, from_=0, to=23, width=4, wrap=True)
    hours_start_s.grid(row=0, column=2, sticky="n")

    label = ttk.Label(dates_frame, text="m:")
    label.grid(row=0, column=3)
    minutes_start_s = tk.Spinbox(dates_frame, from_=0, to=59, width=4, wrap=True)
    minutes_start_s.grid(row=0, column=4, sticky="n")

    cal_end = DateEntry(dates_frame, selectmode='day')
    cal_end.grid(row=1, column=0, sticky="n")

    label = ttk.Label(dates_frame, text="h:")
    label.grid(row=1, column=1)
    hours_end_s = tk.Spinbox(dates_frame, from_=0, to=23, width=4, wrap=True)
    hours_end_s.grid(row=1, column=2, sticky="n")

    label = ttk.Label(dates_frame, text="m:")
    label.grid(row=1, column=3)
    minutes_end_s = tk.Spinbox(dates_frame, from_=0, to=59, width=4, wrap=True)
    minutes_end_s.grid(row=1, column=4)

    label = ttk.Label(dates_frame, text="interval in minutes:")
    label.grid(row=2, column=0)
    interval_e = tk.Spinbox(dates_frame, from_=0, to=float("inf"), width=4)
    interval_e.grid(row=2, column=2)

    # coords frame
    coords_frame = tk.Frame(right_frame)
    coords_frame.grid(row=1, column=0, sticky='n' + 'w' + 'e' + 's', padx=10, pady=10)

    label = ttk.Label(coords_frame, text="latitude start:")
    label.grid(row=0, column=0)
    latitude_start_s = tk.Spinbox(coords_frame, from_=-90, to=90, width=6, wrap=True, format="%.2f", increment=0.5)
    latitude_start_s.grid(row=0, column=1, sticky="n")
    label = ttk.Label(coords_frame, text="longitude start:")
    label.grid(row=0, column=2)
    longitude_start_s = tk.Spinbox(coords_frame, from_=-180, to=180, width=7, wrap=True, format="%.2f", increment=0.5)
    longitude_start_s.grid(row=0, column=3)

    label = ttk.Label(coords_frame, text="latitude end:")
    label.grid(row=1, column=0)
    latitude_end_s = tk.Spinbox(coords_frame, from_=-90, to=90, width=6, wrap=True, format="%.2f", increment=0.5)
    latitude_end_s.grid(row=1, column=1, sticky="n")
    label = ttk.Label(coords_frame, text="longitude end:")
    label.grid(row=1, column=2)
    longitude_end_s = tk.Spinbox(coords_frame, from_=-180, to=180, width=7, wrap=True, format="%.2f", increment=0.5)
    longitude_end_s.grid(row=1, column=3)

    # address frame
    address_frame = tk.Frame(right_frame)
    address_frame.grid(row=2, column=0, sticky='n' + 'w' + 'e' + 's', padx=10, pady=10)
    label = ttk.Label(address_frame, text="PyThor address:")
    label.grid(row=0, column=0)
    addr_val = tk.StringVar()
    addr_val.set("http://127.0.0.1:5000")
    entry = ttk.Entry(address_frame, textvariable=addr_val)
    entry.grid(row=0, column=1, padx=10)

    # confirm button
    button = ttk.Button(
        root,
        text="Create request",
        command=create_request)

    button.pack()

    result_t = tk.Text(root, height=4, width=15,state=tk.DISABLED)
    result_t.pack(fill="x", pady=5, padx=10)
    root.mainloop()


create_window()
