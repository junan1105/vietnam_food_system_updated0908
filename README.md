# 已更新的越南小吃外帶系統

包含：

- 一張訂單可加入多種餐點
- 取餐姓名（不含桌號）
- 每筆訂單西元日期 `YYYY/MM/DD`
- 後台手動更新「已接單／製作中／已完成可領取」

## 在 VS Code 開啟與執行

1. 在 VS Code 選擇「檔案 → 開啟資料夾」。
2. 選擇本資料夾。
3. 開啟終端機並執行：

```powershell
& ".\.venv\Scripts\python.exe" -m pip install flask
& ".\.venv\Scripts\python.exe" app.py
```

若本資料夾尚無 `.venv`，請先以已安裝的 Python 建立：

```powershell
python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install flask
& ".\.venv\Scripts\python.exe" app.py
```

使用者畫面：`http://127.0.0.1:5000`  
後台管理：`http://127.0.0.1:5000/admin`
