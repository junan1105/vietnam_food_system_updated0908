
系統檔案完整版下載連結，https://drive.google.com/drive/folders/1-iOOaTePYz7AT5D0nL8B7HzbJUlovZBR?usp=drive_link

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
