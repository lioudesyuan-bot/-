#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime
import requests
import json
import gspread
from openpyxl import Workbook
from oauth2client.service_account import ServiceAccountCredentials

# 提早初始化所有陣列，徹底根除 NameError
n1_Name, n1_Value = [], []
n2_Name, n2_Value = [], []
n3_Name, n3_Value = [], []
n5_Name, n5_Value = [], []
n6_Name, n6_Value = [], []

print("正在載入 Selenium 模組... (若在此處卡死，請檢查防毒軟體或將 Python 降版本至 3.12)")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By
    print("Selenium 模組載入成功！")
except KeyboardInterrupt:
    print("\n[錯誤] 使用者手動中止了模組載入。")
    sys.exit()

# 設定 Chrome Options 提高穩定性，防止瀏覽器背景卡死
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')  # 隱藏瀏覽器視窗
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

print("正在啟動 Chrome 瀏覽器(背景隱藏)...")
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

############ 老子有錢 ############
try:
    driver.get("https://www.08online.com/pc/activityRank?tab=3")
    time.sleep(3)

    i = 0
    m = 0
    print ("\n------------老子有錢------------")
    while True:
        i += 1
        try:
            xpath = "//*[@id=\"app\"]/div/div[1]/div/div[3]/div[2]/div[2]/div/div/ul[2]/li[" + str(i) + "]/p[2]/span"
            elem = driver.find_element(By.XPATH, xpath)
            name = elem.get_attribute('innerHTML')
        except:
            try:
                xpath = "//*[@id=\"app\"]/div/div[1]/div/div[3]/div[2]/div[2]/div/div/div/ul/li[" + str(i) + "]/p[2]/span"
                elem = driver.find_element(By.XPATH, xpath)
                name = elem.get_attribute('innerHTML')
            except:
                break

        n1_Name.append(name)

        try:
            xpath = "//*[@id=\"app\"]/div/div[1]/div/div[3]/div[2]/div[2]/div/div/ul[2]/li[" + str(i) + "]/p[4]"
            elem = driver.find_element(By.XPATH, xpath)
            value = elem.get_attribute('innerHTML')
            value_num = value.replace(",", "")
        except:
            try:
                xpath = "//*[@id=\"app\"]/div/div[1]/div/div[3]/div[2]/div[2]/div/div/div/ul/li[" + str(i) + "]/p[4]"
                elem = driver.find_element(By.XPATH, xpath)
                value = elem.get_attribute('innerHTML')
                value_num = value.replace(",", "")
            except:
                value_num = "0"
        
        n1_Value.append(value_num)
        m += 1
        print (m, " ", name," ", value_num)

        if m >= 100 :
            break
except Exception as e:
    print(f"老子有錢爬取失敗: {e}")


############ 滿貫大亨 ############
try:
    driver.get("https://www.gametower.com.tw/Games/tmd/rank/index.aspx?fc=1#rank")
    time.sleep(3)

    print ("\n------------滿貫大亨------------")
    for j in range(0, 5):
        if( j > 0 ):
            try:
                xpath = '//*[@id="rank"]/table/tbody/tr[2]/td/a['
                if( j == 1 ):   xpath += str(j)
                else:           xpath += str(j+1)
                xpath += ']'
                apply_btn = driver.find_element(By.XPATH, xpath)
                WebDriverWait(driver,5).until(lambda driver : apply_btn.is_displayed())
                apply_btn.click()
                time.sleep(1)
            except:
                print("\n無法下一頁......！")

        i = 1
        m = 0
        while True:
            i+=1
            try:
                xpath = "//*[@id='rank']/table/tbody/tr[3]/td/div/ul/li[" + str(i) + "]/span[2]"
                elem = driver.find_element(By.XPATH, xpath)
                name = elem.get_attribute('innerHTML')
                n3_Name.append(name)

                xpath = "//*[@id='rank']/table/tbody/tr[3]/td/div/ul/li[" + str(i) + "]/span[3]"
                elem = driver.find_element(By.XPATH, xpath)
                value = elem.get_attribute('innerHTML')
                if isinstance(value, int):
                    n3_Value.append(value)
                else:
                    n3_Value.append(int(value.replace(",", "")))

                m += 1
                print (m, " ", name," ", value)
            except Exception as e:
                break

            if m >= 20:
                break
except Exception as e:
    print(f"滿貫大亨爬取失敗: {e}")


############ 包你發 (API 模式) ############
print ("\n------------包你發------------")
try:
    show_time = time.strftime("%Y-%m-%d", time.localtime())
    d1 = datetime.datetime.strptime('2018-01-01', '%Y-%m-%d')
    d2 = datetime.datetime.strptime(show_time, '%Y-%m-%d')
    delta = (d2 - d1)/7

    xpath = f'https://cdn-data.online808.com/data/Game/RankService/RankDataRequest/Rich/1/Temp/{delta.days}.json'

    UrlData = requests.get(xpath)
    time.sleep(3)
    JsonData = json.loads( UrlData.text )
    print("包你發資料標籤:", JsonData.get("tag", "無"))

    for j in range(0, min(100, len(JsonData["rankInfoList"]))):
        n2_Name.append(JsonData["rankInfoList"][j]["nickName"])
        n2_Value.append(float(JsonData["rankInfoList"][j]["win"]/100))
        print (j+1, " ", n2_Name[j]," ", n2_Value[j])
except Exception as e:
    print(f"包你發 API 讀取失敗: {e}")


# 關閉瀏覽器
try:
    driver.quit()
except:
    pass


# ====================================================================
# 🎯【全新升級】：健全性檢查與強效防呆打包傳送
# ====================================================================
print("\n------------ 正在優化並檢查資料結構 ------------")

GAS_WEBAPP_URL = os.environ.get("GAS_WEBAPP_URL")

if not GAS_WEBAPP_URL:
    print("❌ 錯誤：環境變數中找不到 GAS_WEBAPP_URL，無法傳送！")
    sys.exit()

# 輔助清理與對齊函數：確保轉成數字、防範 NaN、強迫對齊 100 筆長度
def sanitize_and_pad(raw_values, expected_length=100):
    clean_list = []
    for val in raw_values:
        try:
            # 移除可能殘留的逗號或空白，轉換為浮點數或整數
            if isinstance(val, str):
                val = val.replace(",", "").strip()
            num = float(val) if val else 0.0
            clean_list.append(num)
        except Exception:
            clean_list.append(0.0)
            
    # 如果撈到的數量不夠，自動在後面補 0 直到滿 100 筆（徹底根除 GAS 端因長度不足爆掉的問題）
    while len(clean_list) < expected_length:
        clean_list.append(0.0)
        
    # 截斷多餘的，確保剛好 100 筆
    return clean_list[:expected_length]

# 智慧清理三大娛樂城的數值陣列
clean_n1_value = sanitize_and_pad(n1_Value)
clean_n2_value = sanitize_and_pad(n2_Value)
clean_n3_value = sanitize_and_pad(n3_Value)

# 打包安全無毒的大字典
payload = {
    "n1_Name": n1_Name[:100] if n1_Name else ["無"]*100,
    "n1_Value": clean_n1_value,
    "n2_Name": n2_Name[:100] if n2_Name else ["無"]*100,
    "n2_Value": clean_n2_value,
    "n3_Name": n3_Name[:100] if n3_Name else ["無"]*100,
    "n3_Value": clean_n3_value
}

print(f"📊 檢查完畢！老子有錢: {len(payload['n1_Value'])}筆, 包你發: {len(payload['n2_Value'])}筆, 滿貫大亨: {len(payload['n3_Value'])}筆")
print("🚀 正在透過 GAS 安全傳送資料至 Google 試算表...")

try:
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    # 加上 timeout 防止 GitHub Actions 遇到 Google 伺服器抽風時無限卡死
    response = requests.post(GAS_WEBAPP_URL, data=json.dumps(payload), headers=headers, timeout=45)
    
    print("================================================")
    print("🎉 Google 試算表雲端回應：")
    print(response.text)
    print("================================================")
except Exception as e:
    print(f"❌ 傳送至試算表時發生網路異常: {e}")

print("\n------------ 執行完畢 ------------")
