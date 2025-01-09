import time
import board
import busio
from adafruit_sht31d import SHT31D
import subprocess
import json

# SHT31の初期化
i2c = busio.I2C(board.SCL, board.SDA)
sht31 = SHT31D(i2c)

# CO2濃度を取得する関数（subprocessを使用）
def get_co2_concentration():
    try:
        # subprocessでmh_z19の結果を取得
        result = subprocess.check_output(['sudo', 'python3', '-m', 'mh_z19'], text=True)
        co2_data = json.loads(result)
        return co2_data.get("co2", "N/A")  # CO2濃度を取得
    except Exception as e:
        print(f"CO2データ取得エラー: {e}")
        return "N/A"

# メインループ
try:
    while True:
        # SHT31から温湿度を取得
        temperature = sht31.temperature  # 温度 (℃)
        humidity = sht31.relative_humidity  # 湿度 (%)

        # subprocessを使用してCO2濃度を取得
        co2_ppm = get_co2_concentration()

        # コンソールに出力
        print(f"温度: {temperature:.2f}℃, 湿度: {humidity:.2f}%, CO2濃度: {co2_ppm} ppm")

        # 2秒ごとに更新
        time.sleep(2)

except KeyboardInterrupt:
    print("終了します...")