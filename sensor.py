import board
import busio
import adafruit_bme680
import math
import logging
import tkinter as tk

logger = logging.getLogger(__name__)

class RoundedFrame(tk.Frame):
    def __init__(self, master=None, radius=16, fill="#2a2a2a", outline="#FFFFFF", outline_width=3, bg="#000000", **kwargs):
        super().__init__(master, bg=bg, **kwargs)
        self.radius = radius
        self.fill = fill
        self.outline = outline
        self.outline_width = outline_width
        self.bg = bg
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=fill, bd=0)
        self.canvas.bind("<Configure>", self._redraw)
    def _redraw(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        r = max(0, min(self.radius, w // 2, h // 2))
        self.canvas.create_arc(0, 0, 2 * r, 2 * r, start=90, extent=90, fill=self.fill, outline=self.fill)
        self.canvas.create_arc(w - 2 * r, 0, w, 2 * r, start=0, extent=90, fill=self.fill, outline=self.fill)
        self.canvas.create_arc(0, h - 2 * r, 2 * r, h, start=180, extent=90, fill=self.fill, outline=self.fill)
        self.canvas.create_arc(w - 2 * r, h - 2 * r, w, h, start=270, extent=90, fill=self.fill, outline=self.fill)
        self.canvas.create_rectangle(r, 0, w - r, h, fill=self.fill, outline=self.fill)
        self.canvas.create_rectangle(0, r, w, h - r, fill=self.fill, outline=self.fill)
        if self.outline_width > 0:
            ow = self.outline_width
            self.canvas.create_arc(ow/2, ow/2, 2 * r - ow/2, 2 * r - ow/2, start=90, extent=90, style="arc", outline=self.outline, width=ow)
            self.canvas.create_arc(w - 2 * r + ow/2, ow/2, w - ow/2, 2 * r - ow/2, start=0, extent=90, style="arc", outline=self.outline, width=ow)
            self.canvas.create_arc(ow/2, h - 2 * r + ow/2, 2 * r - ow/2, h - ow/2, start=180, extent=90, style="arc", outline=self.outline, width=ow)
            self.canvas.create_arc(w - 2 * r + ow/2, h - 2 * r + ow/2, w - ow/2, h - ow/2, start=270, extent=90, style="arc", outline=self.outline, width=ow)
            self.canvas.create_line(r, ow/2, w - r, ow/2, fill=self.outline, width=ow)
            self.canvas.create_line(r, h - ow/2, w - r, h - ow/2, fill=self.outline, width=ow)
            self.canvas.create_line(ow/2, r, ow/2, h - r, fill=self.outline, width=ow)
            self.canvas.create_line(w - ow/2, r, w - ow/2, h - r, fill=self.outline, width=ow)
        pad = max(6, self.outline_width + 4)
        self.canvas.create_window(pad, pad, anchor="nw", window=self.inner, width=max(0, w - 2 * pad), height=max(0, h - 2 * pad))

class Sensor:
    def __init__(self, sea_level_hpa=1013.25):
        self.sea_level_hpa = sea_level_hpa
        self.device = self._init_sensor()
    def _init_sensor(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        for addr in (0x77, 0x76):
            try:
                dev = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=addr)
                dev.gas_heater_temperature = 0
                dev.gas_heater_duration = 0
                logger.info(f"Adafruit BME680 연결 성공 (0x{addr:02X})")
                return dev
            except Exception as e:
                logger.warning(f"BME680 초기화 실패(0x{addr:02X}): {e}")
        return None
    def read(self):
        if self.device is None:
            return None, None, None
        try:
            t = float(self.device.temperature)
            h = float(self.device.relative_humidity)
            p = float(self.device.pressure)
            return t, h, p
        except Exception as e:
            logger.error(f"센서 읽기 실패: {e}")
            return None, None, None
    def read_gas(self):
        try:
            if hasattr(self.device, "gas"):
                return float(getattr(self.device, "gas")) / 1000.0
        except Exception:
            return None
        return None
    def calc_altitude(self, p):
        try:
            return 44330.0 * (1.0 - pow((p / self.sea_level_hpa), 0.1903))
        except Exception:
            return None
    def calc_dew_point(self, t, h):
        try:
            a, b = 17.27, 237.7
            rh = max(0.1, min(100.0, h))
            alpha = (a * t)/(b + t) + math.log(rh / 100.0)
            return (b * alpha) / (a - alpha)
        except Exception:
            return None
