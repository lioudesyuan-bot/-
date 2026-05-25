import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ==================== 🔥 參數設定區 ====================
BOT_TOKEN = "8730203943:AAEwahPleVLjoQWj2EXZVjr6ISYpoh5ib7U"
GAS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbyDrkoCtx8hFBg43NnStpX1hJ6Sr9ZECFxRlOrTBTfjrXINZKBOOKEs7eGu-uXklMnV/exec"

# 💡 精準鎖定你指定的 Windows 本地資料夾（前面加 r 可以防範路徑斜線的跳脫字元報錯）
SAVE_DIR = r"C:\Users\lioudesyuan\Downloads\Telegram Desktop"
# =======================================================

# 防呆：確保該資料夾存在，如果沒有會自動建立
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file_name = document.file_name

    # 防呆：只處理 CSV 檔案
    if file_name.lower().endswith('.csv'):
        print(f" 偵測到新 CSV 檔案: {file_name}")
        
        # 1. 取得 Telegram 檔案遠端下載路徑
        tg_file = await context.bot.get_file(document.file_id)
        local_file_path = os.path.join(SAVE_DIR, file_name)
        
        # 2. 下載並實體儲存到指定的 Telegram Desktop 資料夾
        await tg_file.download_to_drive(custom_path=local_file_path)
        print(f" 實體檔案已成功存入: {local_file_path}")
        
        # 3. 讀取該 CSV 內容，並透過 HTTP POST 轉發給雲端的 Google Apps Script
        try:
            with open(local_file_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            # 將 CSV 純文字內容透過 POST 塞進 Body 送往 GAS
            headers = {'Content-Type': 'text/plain; charset=utf-8'}
            response = requests.post(GAS_WEBAPP_URL, data=csv_content.encode('utf-8'), headers=headers)
            
            print(f" Google Apps Script 回應: {response.text}")
            await update.message.reply_text(f" 檔案已存入 Telegram Desktop 資料夾，並已成功同步匯入 Google 試算表！")
            
        except Exception as e:
            print(f" 轉發給 GAS 時發生錯誤: {e}")
            await update.message.reply_text(f" 本地檔案已儲存，但同步至試算表失敗: {e}")
    else:
        print(f" 忽略非 CSV 檔案: {file_name}")

def main():
    print("🚀 Telegram Bot 本地自動存檔與 GAS 同步監聽中...")
    print(f" 當前指定下載資料夾: {SAVE_DIR}")
    
    # 使用 Polling 輪詢模式，100% 繞過 Webhook 網域與 HTTPS 憑證限制
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 監聽所有文件檔案
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # 開始輪詢
    application.run_polling()

if __name__ == '__main__':
    main()