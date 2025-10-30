## BME680 대시보드 (Tkinter)

라즈베리파이에서 Adafruit CircuitPython BME680 드라이버를 사용해 온도/습도/기압을 풀스크린으로 표시하는 Tkinter 대시보드입니다. 5초마다 자동 갱신합니다.

### 구성
- UI: Tkinter 풀스크린, 다크 테마, 3개 카드 한 줄 고정
- 드라이버: `adafruit-circuitpython-bme680` (주소 0x77 → 실패 시 0x76)
- 가스 히터: 비활성화(온도 영향 최소화)

## 파일 구조 및 주요 내용

```
rasp_bme680_python_web/
├── main.py             # 실행 entry point, 대시보드(GUI) 호출
├── ui.py               # Tkinter 대시보드 화면, 센서 및 MQTT 클래스 연동, 갱신 루프
├── sensor.py           # BME680 센서 초기화, 데이터 읽기, 카드 UI용 RoundedFrame 구현
├── mqtt_reporter.py    # .env 환경 로드, MQTT 접속/전송 및 JSON 생성
├── requirements.txt    # 필요한 파이썬 의존성 목록
├── README.md           # 설치 및 전체 구성 설명, 파일 구조/리팩토링 내역
├── temp_monitor.jpg    # 대시보드 UI 예시 이미지
└── .env                # MQTT 등 환경설정(민감정보/직접생성)
```

### 각 파일 설명

- **main.py**  
  프로그램 실행 진입점. Tk 대시보드 앱을 구동하며, 실제 실행 명령 및 최소 코드만 포함.
- **ui.py**  
  `Dashboard` 클래스를 구현. Tkinter 풀스크린 UI 및 대시보드 카드, 측정값 갱신 루프, 센서·MQTT 연동, 단축키 등. (센서/MQTT 기능은 각 모듈 활용)
- **sensor.py**  
  `Sensor` 클래스(BME680 초기화/데이터 읽기/가스저항/고도/이슬점 계산 등) 및 카드 UI용 `RoundedFrame` 구현 포함.
- **mqtt_reporter.py**  
  `MQTTReporter` 클래스. 환경변수(.env) 처리, 브로커 연결/인증, 페이로드(json) 생성 및 발행, 전송주기 관리 등 포함.
- **requirements.txt**  
  pip로 설치할 필수 python 패키지 목록.
- **README.md**  
  전체 설치/연결 방법, 실행 예시, 파일 구조·기능 설명(현재 문서).
- **temp_monitor.jpg**  
  실제 UI 예시 이미지(설치 또는 개발 참고용).
- **.env**  
  MQTT 접속정보, 센서명·지역 등 환경 기반 설정 (별도 직접 생성 필요/gitinore 추천).

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

