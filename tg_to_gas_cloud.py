import os
import requests

# 🔐 從 GitHub Secrets 安全讀取環境變變數
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
GAS_WEBAPP_URL = os.environ.get("GAS_WEBAPP_URL")

def main():
    if not BOT_TOKEN or not GAS_WEBAPP_URL:
        print("❌ 錯誤：找不到環境變數 TG_BOT_TOKEN 或 GAS_WEBAPP_URL，請檢查 GitHub Secrets 設定。")
        return

    print("🚀 雲端特工啟動，正在主動向 Telegram 撈取最新訊息...")
    
    # 1. 呼叫 getUpdates 獲取最近的聊天紀錄
    get_updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(get_updates_url)
        res_data = response.json()
    except Exception as e:
        print(f"❌ 連線至 Telegram 失敗: {e}")
        return

    if not res_data.get("ok"):
        print(f"❌ Telegram API 回傳錯誤: {res_data}")
        return

    # 2. 从後往前翻，尋找最新且符合特定檔名的金好運 CSV 檔案
    updates = res_data.get("result", [])
    csv_file_id = None
    csv_file_name = None

    for update in reversed(updates):
        message = update.get("message")
        if message and "document" in message:
            doc = message["document"]
            filename = doc.get("file_name", "")
            
            # 🎯【核心修正】：必須是 CSV 檔，且檔名內必須包含指定的關鍵字
            if filename.lower().endswith('.csv') and "_assetranking_top100_tw" in filename.lower():
                csv_file_id = doc.get("file_id")
                csv_file_name = filename
                break  # 精準鎖定最新的那張金好運，直接跳出迴圈

    if not csv_file_id:
        print("⚠️ 提示：最近的 Telegram 紀錄中沒有發現符合 '_AssetRanking_TOP100_TW' 的金好運 CSV 檔案。")
        return

    print(f"🎯 成功精準鎖定金好運 CSV 檔案: {csv_file_name}")

    # 3. 取得該檔案的雲端下載路徑
    get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={csv_file_id}"
    file_res = requests.get(get_file_url).json()
    
    if not file_res.get("ok"):
        print("❌ 無法獲取 Telegram 檔案路徑")
        return
        
    file_path = file_res["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # 4. 下載 CSV 內容並直接轉發給 Google Apps Script
    print("📥 正在讀取檔案內容並發送至 Google 試算表...")
    try:
        csv_content = requests.get(download_url).content
        
        headers = {'Content-Type': 'text/plain; charset=utf-8'}
        gas_res = requests.post(GAS_WEBAPP_URL, data=csv_content, headers=headers)
        
        print(f"🎉 Google Apps Script 回應: {gas_res.text}")
    except Exception as e:
        print(f"❌ 轉發至 GAS 時發生異常: {e}")

if __name__ == '__main__':
    main()
