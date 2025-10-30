# 라즈베리파이 + BME680 기반 실내 환경 대시보드 구축

이 문서에서는 BME680 센서를 사용하여 라즈베리파이 기반 환경 데이터 대시보드(Tkinter GUI)를 구현하는 과정을 기술적으로 정리한다.

## 1. 시스템 개요

- **센서**: BME680 (온도, 습도, 기압, 가스저항값 측정 지원)
- **플랫폼**: Raspberry Pi (I2C 통신)
- **UI 프레임워크**: Python Tkinter (풀스크린/다크테마/카드형 레이아웃)
- **통신**: MQTT (옵션)
- **주기적 데이터 업데이트**: 기본 5초간격 자동 갱신

## 2. 하드웨어 및 회로 연결

- BME680 → Raspberry Pi 커넥션: VCC(3.3V), GND, SDA(GPIO2), SCL(GPIO3)
- I2C 활성화 필요 (`sudo raspi-config` ⇒ Interface Options ⇒ I2C Enable)
- I2C 주소: 보통 0x77, 일부 보드는 0x76 (드라이버에서 자동 처리)

## 3. 주요 소프트웨어 구조 및 모듈별 기능

- `main.py`: 대시보드 실행 진입점, 최소 실행로직만 포함
- `ui.py`: Tkinter 기반 Dashboard 구현, 센서·MQTT 연동, 전체화면 카드UI, 자동 갱신 루프(5초마다)
- `sensor.py`: 센서 제어 및 데이터 획득. BME680 초기화, 원시데이터 읽기, 이슬점·가스저항·고도 계산 포함
- `mqtt_reporter.py`: 환경파일(.env)에서 변수 로드, MQTT 브로커 연결/인증, 페이로드(JSON) 전송
- `.env`: MQTT 서버주소, 센서명, 지역 등 환경변수 정의(사용자가 수동 작성 필요)

## 4. BME680 센서 기능 요약

- **온도**: -40~85℃의 정밀 온도정보 제공
- **습도**: 0~100% 상대습도 지원
- **기압**: 300~1100hPa 측정 가능(간이 고도계로 활용 가능)
- **가스**: VOC 등 가스 농도에 비례하는 저항값 제공(공기질 지표 산출 가능)
- **알고리즘**: 센서 드라이버에서 보정·계산, 추가적으로 이슬점, 고도 계산 구현

## 5. 시스템 소프트웨어 설치 및 실행 과정

### 패키지 설치
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- 주요 의존성: `adafruit-circuitpython-bme680`, `adafruit-blinka`, `tkinter`

### 실행
```bash
python /home/pi/works/rasp_bme680_python_web/main_tk.py
```
- 기본 전체화면
- Esc 키로 종료

### 예시 UI

![UI 예시](/home/pi/works/rasp_bme680_python_web/temp_monitor.jpg)

## 6. MQTT 연동

- `.env`에 브로커 주소/포트/토픽/인증 등 설정 필요
- 센서 측정값을 JSON 데이터로 MQTT 발행
- 발행 주기: 일반적으로 5초(수정 가능)

## 7. 서비스형 구동 (systemd)

- systemd unit 파일 작성하여 부팅, 네트워크 연결 후 자동 실행 설정
- 예시: `/etc/systemd/system/bme680-dashboard.service` 파일 참고

## 8. 문제 해결 및 참고사항

- I2C 미감지: 배선, 센서, I2C 활성상태 확인
- 비정상 값: 발열, 배선, 환경 잡음 원인 검토
- 라이브러리 오류: 드라이버 패키지 업그레이드

## 9. 라이선스 및 확장

- 본 프로젝트는 교육 및 기술연구 목적에 한해 자유롭게 사용/수정/재배포 가능.
- 데이터 전송, 원격 모니터링, 사용자 경보 등 추가 확장 가능함.
