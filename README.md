## BME680 대시보드 (Tkinter)

라즈베리파이에서 Adafruit CircuitPython BME680 드라이버를 사용해 온도/습도/기압을 풀스크린으로 표시하는 Tkinter 대시보드입니다. 5초마다 자동 갱신합니다.

### 구성
- UI: Tkinter 풀스크린, 다크 테마, 3개 카드 한 줄 고정
- 드라이버: `adafruit-circuitpython-bme680` (주소 0x77 → 실패 시 0x76)
- 가스 히터: 비활성화(온도 영향 최소화)

---

### 1) 준비물
- 라즈베리파이 (I2C 지원)
- BME680 센서 모듈 (I2C)
- 점퍼 케이블

### 2) 배선
- VCC → 3.3V
- GND → GND
- SDA → GPIO2 (핀 3)
- SCL → GPIO3 (핀 5)

### 3) I2C 활성화 및 확인
```bash
sudo raspi-config    # Interface Options → I2C → Enable
sudo apt-get install -y i2c-tools python3-tk
sudo i2cdetect -y 1  # 0x77 또는 0x76이 보여야 정상
```

### 4) 설치
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` 내용:
```
adafruit-circuitpython-bme680>=3.5.0
adafruit-blinka>=8.45.0
```

### 5) 실행
```bash
python /home/pi/works/rasp_bme680_python_web/main_tk.py
```
- 종료: 키보드 `Esc`
- 전체 화면이 기본이며 5초마다 자동으로 값이 업데이트됩니다.

### 6) 부팅 시 자동 실행(선택)
`/etc/systemd/system/bme680-dashboard.service` 예시:
```
[Unit]
Description=BME680 Tk Dashboard
After=network-online.target

[Service]
User=pi
WorkingDirectory=/home/pi/works/rasp_bme680_python_web
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/pi/works/rasp_bme680_python_web/venv/bin/python /home/pi/works/rasp_bme680_python_web/main_tk.py
Restart=always

[Install]
WantedBy=graphical.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable bme680-dashboard.service
sudo systemctl start bme680-dashboard.service
```

### 문제 해결
- `i2cdetect -y 1`에서 0x77/0x76이 보이지 않음: 배선/전원 점검, I2C 활성화 확인
- 값이 비정상적으로 높음: 센서 주변 발열·케이스 영향 확인, 배선 길면 간헐적 노이즈 가능
- 라이브러리 오류: `pip install --upgrade adafruit-circuitpython-bme680 adafruit-blinka`

### 라이선스
본 예제는 교육/개인용으로 자유롭게 수정/사용할 수 있습니다.