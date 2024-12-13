# README

## 專案名稱

使用串口讀取感測器數據並上傳至伺服器

---

## 專案簡介

本專案通過 Python 從串口接收感測器數據，計算電力消耗並將數據以 HTTP POST 請求的方式上傳至伺服器。主要功能包含：

1. 連接兩個感測器，讀取電壓（Voltage）、電流（Current）及功率（Power）。
2. 計算累積電力消耗。
3. 定期將數據傳送至伺服器。

---

## 目錄結構

```plaintext
├── main.py           # 主程式碼
├── README.md         # 使用說明文件
└── poetry.lock       # Poetry 鎖定檔案
```

---

## 系統需求

- Python 版本 >= 3.7
- 串口硬體設備與感測器
- 安裝依賴庫

---

## 安裝與執行

### 1. 安裝 Poetry

請依照 Poetry 官方文件進行安裝：[Poetry 官方網站](https://python-poetry.org/docs/)

### 2. 建立虛擬環境並安裝依賴

```bash
poetry install
```

### 3. 配置環境

將以下變數修改成你的系統配置：

- `DATA_POST_CUSTOM`：伺服器的 HTTP 接口地址。
- `SERIAL_PORT`：串口端口，例如 `COM3` 或 `/dev/ttyUSB0`。
- `BAUD_RATE`：串口波特率，預設為 9600。

### 4. 執行程式

```bash
poetry run python main.py
```

---

## 程式碼說明

### `main.py`

#### 全域變數

- `DATA_POST_CUSTOM`：伺服器的 POST 地址。
- `SERIAL_PORT`：串口設備名稱。
- `BAUD_RATE`：串口波特率。
- `accumulated_power_1` 與 `accumulated_power_2`：分別記錄兩個感測器的累積功耗。

#### 函式解說

1. **`send_data()`**
   - 將感測器的數據格式化後以 JSON 格式透過 HTTP POST 發送至伺服器。
   - 處理傳輸過程中的異常情況，確保穩定性。

2. **`read_from_serial()`**
   - 從串口讀取一行數據並解析為 JSON 格式。
   - 處理數據解析錯誤及其他異常情況。

3. **`main()`**
   - 主程式執行邏輯，負責：
     - 初始化串口連接。
     - 循環讀取感測器數據，計算功耗，並通過 `send_data()` 發送數據。
     - 每 0.1 秒更新一次數據。

---

## 範例輸出

當程式正常運行時，終端會輸出如下格式的數據：

```plaintext
Voltage_1: 12.3V, Current_1: 1.5mA, Power_1: 18.45mW, Voltage_2: 11.7V, Current_2: 2.1mA, Power_2: 24.57mW
```

---

## 注意事項

1. 確保感測器與串口設備正常連接。
2. 如果接收到的 JSON 數據格式不正確，程式會忽略該數據並繼續執行。
3. 設定的伺服器地址應可正常接收 POST 請求。

---

## 開發與維護

### 開發環境

1. Python
2. Poetry

### 測試建議

- 測試不同的感測器輸入數據，檢查數據解析是否正確。
- 測試伺服器是否正確接收與處理數據。

---

## 常見問題

1. **無法連接串口**
   - 檢查 `SERIAL_PORT` 是否正確。
   - 確保程式具有讀取串口的權限。

2. **數據格式錯誤**
   - 確認感測器發送的數據是否符合 JSON 格式。
   - 使用其他工具檢查串口數據輸出。