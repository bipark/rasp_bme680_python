import tkinter as tk
import time
import datetime
import logging

# Adafruit CircuitPython BME680만 사용
import board
import busio
import adafruit_bme680

logging.basicConfig(level=logging.INFO)
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
        # 내부 컨텐츠 프레임 (실제 위젯을 배치할 곳)
        self.inner = tk.Frame(self.canvas, bg=fill, bd=0)
        self.canvas.bind("<Configure>", self._redraw)

    def _redraw(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        r = max(0, min(self.radius, w // 2, h // 2))

        # 둥근 사각형 채우기 (4개의 arc + 5개의 rectangle)
        # 모서리 원호
        self.canvas.create_arc(0, 0, 2 * r, 2 * r, start=90, extent=90, fill=self.fill, outline=self.fill)
        self.canvas.create_arc(w - 2 * r, 0, w, 2 * r, start=0, extent=90, fill=self.fill, outline=self.fill)
        self.canvas.create_arc(0, h - 2 * r, 2 * r, h, start=180, extent=90, fill=self.fill, outline=self.fill)
        self.canvas.create_arc(w - 2 * r, h - 2 * r, w, h, start=270, extent=90, fill=self.fill, outline=self.fill)
        # 중앙과 변 채우기
        self.canvas.create_rectangle(r, 0, w - r, h, fill=self.fill, outline=self.fill)
        self.canvas.create_rectangle(0, r, w, h - r, fill=self.fill, outline=self.fill)

        # 외곽선 (라운드)
        if self.outline_width > 0:
            ow = self.outline_width
            # 사각형 외곽선을 원호와 선으로 구성
            self.canvas.create_arc(ow/2, ow/2, 2 * r - ow/2, 2 * r - ow/2, start=90, extent=90, style="arc", outline=self.outline, width=ow)
            self.canvas.create_arc(w - 2 * r + ow/2, ow/2, w - ow/2, 2 * r - ow/2, start=0, extent=90, style="arc", outline=self.outline, width=ow)
            self.canvas.create_arc(ow/2, h - 2 * r + ow/2, 2 * r - ow/2, h - ow/2, start=180, extent=90, style="arc", outline=self.outline, width=ow)
            self.canvas.create_arc(w - 2 * r + ow/2, h - 2 * r + ow/2, w - ow/2, h - ow/2, start=270, extent=90, style="arc", outline=self.outline, width=ow)
            # 직선 부분
            self.canvas.create_line(r, ow/2, w - r, ow/2, fill=self.outline, width=ow)
            self.canvas.create_line(r, h - ow/2, w - r, h - ow/2, fill=self.outline, width=ow)
            self.canvas.create_line(ow/2, r, ow/2, h - r, fill=self.outline, width=ow)
            self.canvas.create_line(w - ow/2, r, w - ow/2, h - r, fill=self.outline, width=ow)

        # 내부 컨텐츠 위치/크기 조정
        pad = max(6, self.outline_width + 4)
        self.canvas.create_window(pad, pad, anchor="nw", window=self.inner, width=max(0, w - 2 * pad), height=max(0, h - 2 * pad))

def init_bme680():
    """Adafruit BME680만 초기화 (0x77 → 0x76 순서)."""
    i2c = busio.I2C(board.SCL, board.SDA)
    for addr in (0x77, 0x76):
        try:
            dev = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=addr)
            # 가스 히터 비활성화(온도 영향 최소화)
            try:
                dev.gas_heater_temperature = 0
                dev.gas_heater_duration = 0
            except Exception:
                pass
            logger.info(f"Adafruit BME680 연결 성공 (0x{addr:02X})")
            return dev
        except Exception as e:
            logger.warning(f"Adafruit 초기화 실패(0x{addr:02X}): {e}")
    return None


def read_sensor_data(dev):
    if dev is None:
        return None, None, None
    try:
        return float(dev.temperature), float(dev.relative_humidity), float(dev.pressure)
    except Exception as e:
        logger.error(f"센서 읽기 실패: {e}")
        return None, None, None


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BME680 환경 센서")
        self.configure(bg="#000000")
        self._enter_fullscreen()

        # 헤더
        self.location = tk.Label(self, text="LIVINGROOM", fg="#87CEEB", bg="#000000",
                                 font=("Arial", 40, "bold"))
        self.location.pack(pady=(50, 14))
        self.datetime_lbl = tk.Label(self, fg="#FFFFFF", bg="#000000",
                                     font=("Arial", 30))
        self.datetime_lbl.pack(pady=(10, 34))

        # 카드 컨테이너
        self.row = tk.Frame(self, bg="#000000")
        self.row.pack(fill="x", padx=30, pady=(20, 28))

        self.temp_card = self._create_card(self.row, "온도(C)", border="#FF8C00")
        self.hum_card = self._create_card(self.row, "습도(%)", border="#4169E1")
        self.pres_card = self._create_card(self.row, "기압(hPa)", border="#8A2BE2")

        # 동일한 폭을 보장하기 위해 grid 배치 사용
        for col in range(3):
            self.row.grid_columnconfigure(col, weight=1, uniform="cards")
        self.row.grid_rowconfigure(0, weight=1)
        self.temp_card["frame"].grid(row=0, column=0, sticky="nsew", padx=10)
        self.hum_card["frame"].grid(row=0, column=1, sticky="nsew", padx=10)
        self.pres_card["frame"].grid(row=0, column=2, sticky="nsew", padx=10)

        # 센서
        self.sensor = init_bme680()

        # 갱신 루프
        self.update_ui()

        # 단축키
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F11>", lambda e: self._toggle_fullscreen())

    def _enter_fullscreen(self):
        """가능한 모든 방법으로 전체 화면 진입 (라즈비안 WM 호환)."""
        try:
            self.attributes("-fullscreen", True)
        except Exception:
            pass
        # 일부 WM에서 -fullscreen이 먹지 않을 때 대안
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        try:
            self.overrideredirect(True)
        except Exception:
            pass
        self.geometry(f"{sw}x{sh}+0+0")

    def _exit_fullscreen(self):
        try:
            self.attributes("-fullscreen", False)
        except Exception:
            pass
        try:
            self.overrideredirect(False)
        except Exception:
            pass

    def _toggle_fullscreen(self):
        # F11 토글용
        fs = False
        try:
            fs = bool(self.attributes("-fullscreen"))
        except Exception:
            pass
        if fs:
            self._exit_fullscreen()
        else:
            self._enter_fullscreen()

    def _create_card(self, parent, label, border):
        frame = RoundedFrame(parent, radius=18, fill="#2a2a2a", outline=border, outline_width=3, bg="#000000")

        container = frame.inner

        lbl = tk.Label(container, text=label, fg=border, bg="#2a2a2a",
                       font=("Arial", 20, "bold"))
        lbl.pack(pady=(16, 0))

        val = tk.Label(container, text="--", fg="#FFFFFF", bg="#2a2a2a",
                       font=("Arial", 64, "bold"))
        val.pack(pady=(20, 24))

        return {"frame": frame, "value": val}

    def update_ui(self):
        # 시간
        self.datetime_lbl.config(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

        # 센서
        t, h, p = read_sensor_data(self.sensor)
        if t is None:
            t, h, p = 22.7, 53.5, 1015

        self.temp_card["value"].config(text=f"{t:.1f}")
        self.hum_card["value"].config(text=f"{h:.1f}")
        self.pres_card["value"].config(text=f"{p:.0f}")

        # 5초마다 갱신
        self.after(5000, self.update_ui)


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()


