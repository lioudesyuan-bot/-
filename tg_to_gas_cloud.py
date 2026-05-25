import os
import requests
import re

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
GAS_WEBAPP_URL = os.environ.get("GAS_WEBAPP_URL")

def main():
    if not BOT_TOKEN or not GAS_WEBAPP_URL:
        print("❌ 錯誤：找不到環境變數 TG_BOT_TOKEN 或 GAS_WEBAPP_URL")
        return

    print("🚀 雲端特工啟動，正在主動向 Telegram 撈取最新訊息...")
    
    get_updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(get_updates_url)
        res_data = response.json()
    except Exception as e:
        print(f"❌ 連線至 Telegram 失敗: {e}")
        return

    updates = res_data.get("result", [])
    csv_file_id = None
    csv_file_name = None

    for update in reversed(updates):
        message = update.get("message")
        if message and "document" in message:
            doc = message["document"]
            filename = doc.get("file_name", "")
            if filename.lower().endswith('.csv') and "_assetranking_top100_tw" in filename.lower():
                csv_file_id = doc.get("file_id")
                csv_file_name = filename
                break

    if not csv_file_id:
        print("⚠️ 提示：最近的 Telegram 紀錄中沒有發現符合的金好運 CSV 檔案。")
        return

    print(f"🎯 成功精準鎖定金好運 CSV 檔案: {csv_file_name}")

    # 從檔名開頭精準擷取 8 位數日期
    date_match = re.match(r"^(\d{8})_", csv_file_name)
    if not date_match:
        print(f"❌ 錯誤：檔名 '{csv_file_name}' 開頭不符合 8 位數年月日格式。")
        return
    
    file_date_str = date_match.group(1)  # 取得 "20260520"
    print(f"📅 解析出該 CSV 的資料日期為: {file_date_str[:4]}/{file_date_str[4:6]}/{file_date_str[6:]}")

    # 取得下載路徑
    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={csv_file_id}"
    file_res = requests.get(get_file_url).json()
    file_path = file_res["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    print("📥 正在讀取檔案內容並發送至 Google 試算表...")
    try:
        raw_bytes = requests.get(download_url).content
        csv_text = raw_bytes.decode('utf-8')
        
        # 💡【終極大絕招】：把日期當作 CSV 的第一行文字內容，死死綁定在一起！
        payload_text = f"FILE_DATE:{file_date_str}\n{csv_text}"
        
        headers = {'Content-Type': 'text/plain; charset=utf-8'}
        gas_res = requests.post(GAS_WEBAPP_URL, data=payload_text.encode('utf-8'), headers=headers)
        
        print(f"🎉 Google Apps Script 回應: {gas_res.text}")
    except Exception as e:
        print(f"❌ 轉發至 GAS 時發生異常: {e}")

if __name__ == '__main__':
    main()
