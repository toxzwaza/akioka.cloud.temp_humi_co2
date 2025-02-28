import time
import board
import busio
from adafruit_sht31d import SHT31D
import subprocess
import json
import requests
import netifaces
import sys
from notify import send_notify
import random


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

# wlan0のMACアドレスを取得
def get_mac_address():
    # 利用可能なすべてのネットワークインターフェースを取得
    interfaces = netifaces.interfaces()
    
    # wlan0のMACアドレスを取得
    try:
        # インターフェースのアドレス情報を取得
        addrs = netifaces.ifaddresses('wlan0')
        # MACアドレスはAF_LINK (17) に格納されています
        if netifaces.AF_LINK in addrs:
            return addrs[netifaces.AF_LINK][0]['addr']
    except Exception as e:
        print(f"wlan0のMACアドレス取得中にエラーが発生: {e}")
    
    return None


if __name__ == "__main__":

    wait_time = random.randint(0, 60)
    print(f"{wait_time}秒待機します...")
    time.sleep(wait_time)
    

    
    mac_address = get_mac_address()
    #print(f'mac_address: {mac_address}')
    #mention_ids = ['to-murakami@akioka-ltd.jp']
    #send_notify(mention_ids, f'{mac_address}でデータを取得しました。')
    
    
    try:
        response = requests.get(f"https://akioka.cloud/getPlaceId", params={"mac_address": mac_address})
        if response.status_code == 200:
            place_id = response.json()
            
            # SHT31の初期化
            i2c = busio.I2C(board.SCL, board.SDA)
            sht31 = SHT31D(i2c)

            count = 0

            while count < 5:
                try:
                        # SHT31から温湿度を取得
                        temperature = round(sht31.temperature, 0)  # 温度 (℃)
                        humidity = round(sht31.relative_humidity, 0)  # 湿度 (%)

                        # subprocessを使用してCO2濃度を取得
                        co2_ppm = get_co2_concentration()

                        
                        if temperature and humidity and co2_ppm:
                            # コンソールに出力
                            print(f"温度: {temperature:.2f}℃, 湿度: {humidity:.2f}%, CO2濃度: {co2_ppm} ppm")
                        else:
                            # センサー取得エラー
                            print('センサー取得エラー:')
                            count += 1
                        

                        # サーバーにデータを送信
                        try:
                            url = "https://akioka.cloud/data"  # サーバーのURLを設定
                            params = {
                                "temperature": round(temperature, 2),
                                "humidity": round(humidity, 2), 
                                "co2": co2_ppm,
                                "place_id": place_id,
                            }
                            
                            response = requests.get(url, params=params)
                            response_json = response.json()
                            if response_json.get('status') == True:
                                print("データ送信に成功しました")
                                break
                            else:
                                # サーバーサイドエラー
                                print(f'サーバーサイドエラー:{response_json.get("msg")}')
                                count += 1
                                
                        except Exception as e:
                            # リクエストエラー
                            print(f"データリクエストエラー: {e}")
                            count += 1
                        
                        time.sleep(5)

                except KeyboardInterrupt:
                    print("終了します...")

        else:
            print(f"場所IDの取得に失敗しました")
    except Exception as e:
        print(f"場所ID取得エラー: {e}")


