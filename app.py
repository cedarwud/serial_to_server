import serial  # 用於處理串列埠通訊
import requests  # 用於發送 HTTP POST 請求
import time  # 用於計時和延遲
import json  # 用於處理 JSON 數據格式

# REST API 的目標 URL
DATA_POST_CUSTOM = "http://localhost:3000/api/data"

# 串列埠的參數設定
SERIAL_PORT = "COM3"  # 指定串列埠（需要根據設備實際情況調整）
BAUD_RATE = 9600  # 串列埠的波特率

# 初始化累積功率的全域變數
accumulated_power_1 = 0.0  # 感測器 1 的累積功率
accumulated_power_2 = 0.0  # 感測器 2 的累積功率


def send_data(sensor_data_1, sensor_data_2, acc_power_1, acc_power_2):
    """
    將感測器數據與累積功率數據格式化為 JSON，並透過 HTTP POST 發送到伺服器。

    :param sensor_data_1: 感測器 1 的數據字典
    :param sensor_data_2: 感測器 2 的數據字典
    :param acc_power_1: 感測器 1 的累積功率
    :param acc_power_2: 感測器 2 的累積功率
    """
    data = {
        "data": [
            {
                "type": "BATTERY_VOLTAGE",
                "value": sensor_data_1["voltage"],
                "channel": 0,
            },
            {
                "type": "ELECTRIC_CURRENT",
                "value": sensor_data_1["current"],
                "channel": 0,
            },
            {
                "type": "ELECTRICAL_CONSUMPTION",
                "value": sensor_data_1["power"],
                "channel": 0,
            },
            {"type": "ELECTRICAL_CONSUMPTION", "value": acc_power_1, "channel": 2},
            {
                "type": "BATTERY_VOLTAGE",
                "value": sensor_data_2["voltage"],
                "channel": 1,
            },
            {
                "type": "ELECTRIC_CURRENT",
                "value": sensor_data_2["current"],
                "channel": 1,
            },
            {
                "type": "ELECTRICAL_CONSUMPTION",
                "value": sensor_data_2["power"],
                "channel": 1,
            },
            {"type": "ELECTRICAL_CONSUMPTION", "value": acc_power_2, "channel": 3},
            {
                "type": "ELECTRICAL_CONSUMPTION",
                "value": acc_power_1 + acc_power_2,
                "channel": 4,
            },
            {
                "type": "ELECTRICAL_CONSUMPTION",
                "value": sensor_data_1["power"] + sensor_data_2["power"],
                "channel": 5,
            },
        ]
    }
    try:
        # 發送 HTTP POST 請求
        requests.post(DATA_POST_CUSTOM, json=data)
    except requests.RequestException as e:
        print(f"Failed to send data: {e}")


def read_from_serial(ser):
    """
    從串列埠讀取一行數據並解析為 JSON 格式。

    :param ser: 串列埠對象
    :return: 解碼後的字典格式數據，若讀取或解析失敗則返回 None
    """
    try:
        if ser.in_waiting > 0:  # 檢查是否有可讀數據
            line = ser.readline().decode("utf-8").strip()  # 讀取一行並去除多餘空白
            return json.loads(line)  # 將讀取的字串轉為 JSON 格式
    except json.JSONDecodeError:
        print("Received malformed JSON.")  # 提示 JSON 格式錯誤
    except Exception as e:
        print(f"Error reading from serial: {e}")  # 提示其他串列讀取錯誤
    return None


def main():
    """
    主函式：初始化串列埠，循環讀取感測器數據，進行功率計算並發送到伺服器。
    """
    global accumulated_power_1, accumulated_power_2

    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        start_time = time.time()  # 紀錄起始時間
        while True:
            sensor_data = read_from_serial(ser)  # 讀取感測器數據
            if sensor_data:  # 若成功讀取數據
                try:
                    # 提取感測器 1 和 2 的數據
                    sensor_data_1 = sensor_data.get("sensor_1")
                    voltage_1 = float(sensor_data_1.get("voltage", 0))
                    current_1 = float(sensor_data_1.get("current", 0))
                    power_1 = float(sensor_data_1.get("power", 0))
                    sensor_data_2 = sensor_data.get("sensor_2")
                    voltage_2 = float(sensor_data_2.get("voltage", 0))
                    current_2 = float(sensor_data_2.get("current", 0))
                    power_2 = float(sensor_data_2.get("power", 0))

                    # 輸出即時數據
                    print(
                        f"Voltage_1: {voltage_1}V, Current_1: {current_1}mA, Power_1: {power_1}mW, "
                        f"Voltage_2: {voltage_2}V, Current_2: {current_2}mA, Power_2: {power_2}mW"
                    )

                    # 計算時間間隔與累積功率
                    current_time = time.time()
                    time_interval = current_time - start_time
                    accumulated_power_1 += (
                        power_1 / 1000
                    ) * time_interval  # 累積功率，單位 kWh
                    accumulated_power_2 += (power_2 / 1000) * time_interval
                    start_time = current_time  # 更新時間

                    # 發送數據至伺服器
                    send_data(
                        sensor_data_1,
                        sensor_data_2,
                        accumulated_power_1,
                        accumulated_power_2,
                    )
                except (ValueError, TypeError) as e:
                    print(f"Error parsing sensor data: {e}")  # 處理解析錯誤

            time.sleep(0.1)  # 每次循環延遲 100 毫秒


if __name__ == "__main__":
    main()
