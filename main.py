import time
import board
import busio
from adafruit_sht31d import SHT31D
import subprocess
import json
import requests
import netifaces



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

# en0のMACアドレスを取得
def get_en0_mac_address():
    # 利用可能なすべてのネットワークインターフェースを取得
    interfaces = netifaces.interfaces()
    
    # en0のMACアドレスを取得
    for interface in interfaces:
        if interface == "en0":
            try:
                # インターフェースのアドレス情報を取得
                addrs = netifaces.ifaddresses(interface)
                # MACアドレスはAF_LINK (17) に格納されています
                if netifaces.AF_LINK in addrs:
                    return addrs[netifaces.AF_LINK][0]['addr']
            except Exception as e:
                print(f"en0のMACアドレス取得中にエラーが発生: {e}")
                return None
    
    return None

if __name__ == "__main__":


    # en0のMACアドレスを取得
    mac_address = get_en0_mac_address()
    print(f"en0のMACアドレス: {mac_address}")
    try:
        response = requests.get(f"https://akioka.cloud/getPlaceId", params={"mac_address": mac_address})
        if response.status_code == 200:
            print("場所IDの取得に成功しました")
            place_id = response.json()
            print(f"場所ID: {place_id}")
            # SHT31の初期化
            i2c = busio.I2C(board.SCL, board.SDA)
            sht31 = SHT31D(i2c)

            count = 0

            while count < 5:
                try:
                        # SHT31から温湿度を取得
                        temperature = sht31.temperature  # 温度 (℃)
                        humidity = sht31.relative_humidity  # 湿度 (%)

                        # subprocessを使用してCO2濃度を取得
                        co2_ppm = get_co2_concentration()

                        if temperature and humidity and co2_ppm:

                            # コンソールに出力
                            print(f"温度: {temperature:.2f}℃, 湿度: {humidity:.2f}%, CO2濃度: {co2_ppm} ppm")
                            break
                        else:
                            count += 1

                        # サーバーにデータを送信
                        try:
                            url = "https://akioka.cloud/data"  # サーバーのURLを設定
                            data = {
                                "temperature": round(temperature, 2),
                                "humidity": round(humidity, 2), 
                                "co2": co2_ppm,
                                "place_id": place_id,
                            }
                            
                            response = requests.post(url, json=data)
                            if response.status_code == 200:
                                print("データの送信に成功しました")
                            else:
                                print(f"データの送信に失敗しました: {response.status_code}")
                                
                        except Exception as e:
                            print(f"データ送信エラー: {e}")
                            count += 1
                        
                        time.sleep(2)  # 2秒待機
                except KeyboardInterrupt:
                    print("終了します...")

        else:
            print(f"場所IDの取得に失敗しました: {response.status_code}")
    except Exception as e:
        print(f"場所ID取得エラー: {e}")


