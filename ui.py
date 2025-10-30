import tkinter as tk
import datetime
from sensor import Sensor, RoundedFrame
from mqtt_reporter import MQTTReporter

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BME680 환경 센서")
        self.configure(bg="#000000")
        self._enter_fullscreen()
        self.location = tk.Label(self, text="LIVINGROOM", fg="#87CEEB", bg="#000000", font=("Arial", 40, "bold"))
        self.location.pack(pady=(50,14))
        self.datetime_lbl = tk.Label(self, fg="#FFFFFF", bg="#000000", font=("Arial", 30))
        self.datetime_lbl.pack(pady=(10,34))
        self.row = tk.Frame(self, bg="#000000")
        self.row.pack(fill="x", padx=30, pady=(20,28))
        self.temp_card = self._create_card(self.row, "온도(C)", border="#FF8C00")
        self.hum_card = self._create_card(self.row, "습도(%)", border="#4169E1")
        self.pres_card = self._create_card(self.row, "기압(hPa)", border="#8A2BE2")
        for col in range(3):
            self.row.grid_columnconfigure(col, weight=1, uniform="cards")
        self.row.grid_rowconfigure(0, weight=1)
        self.temp_card["frame"].grid(row=0,column=0,sticky="nsew",padx=10)
        self.hum_card["frame"].grid(row=0,column=1,sticky="nsew",padx=10)
        self.pres_card["frame"].grid(row=0,column=2,sticky="nsew",padx=10)
        self.sensor = Sensor()
        self.mqtt = MQTTReporter()
        self.update_ui()
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F11>", lambda e: self._toggle_fullscreen())
    def _enter_fullscreen(self):
        try: self.attributes("-fullscreen", True)
        except Exception: pass
        self.update_idletasks()
        sw=self.winfo_screenwidth(); sh=self.winfo_screenheight()
        try: self.overrideredirect(True)
        except Exception: pass
        self.geometry(f"{sw}x{sh}+0+0")
    def _exit_fullscreen(self):
        try: self.attributes("-fullscreen", False)
        except Exception: pass
        try: self.overrideredirect(False)
        except Exception: pass
    def _toggle_fullscreen(self):
        fs=False
        try: fs=bool(self.attributes("-fullscreen"))
        except Exception: pass
        if fs: self._exit_fullscreen()
        else: self._enter_fullscreen()
    def _create_card(self, parent, label, border):
        frame = RoundedFrame(parent, radius=18, fill="#2a2a2a", outline=border, outline_width=3, bg="#000000")
        container = frame.inner
        lbl = tk.Label(container, text=label, fg=border, bg="#2a2a2a", font=("Arial", 20, "bold"))
        lbl.pack(pady=(36,0))
        val = tk.Label(container, text="--", fg="#FFFFFF", bg="#2a2a2a", font=("Arial", 64, "bold"))
        val.pack(pady=(20,24))
        return {"frame": frame, "value": val}
    def update_ui(self):
        self.datetime_lbl.config(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        t,h,p = self.sensor.read()
        if t is None:
            t,h,p = 22.7,53.5,1015
        self.temp_card["value"].config(text=f"{t:.1f}")
        self.hum_card["value"].config(text=f"{h:.1f}")
        self.pres_card["value"].config(text=f"{p:.0f}")
        gas = self.sensor.read_gas()
        alt = self.sensor.calc_altitude(p)
        dew = self.sensor.calc_dew_point(t,h)
        if self.mqtt.should_publish():
            self.mqtt.publish(t,h,p,gas,alt,dew)
            self.mqtt.update_publish_time()
        self.after(5000,self.update_ui)
