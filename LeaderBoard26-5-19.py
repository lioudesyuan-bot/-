#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


# 到了原本的寫檔階段，改成這樣寫：
print("\n------------ 正在透過 GAS 傳送資料至 Google 試算表 ------------")

# 1. 這裡貼上你剛剛在 Google 部署得到的網頁應用程式網址
GAS_WEBAPP_URL = os.environ.get("GAS_WEBAPP_URL")

# 2. 把所有抓到的陣列打包成一個大字典
payload = {
    "n1_Name": n1_Name,
    "n1_Value": n1_Value,
    "n2_Name": n2_Name,
    "n2_Value": n2_Value,
    "n3_Name": n3_Name,
    "n3_Value": n3_Value
}

try:
    # 3. 直接發送 POST 請求給 Google Sheet，免金鑰、免驗證！
    response = requests.post(GAS_WEBAPP_URL, json=payload, timeout=30)
    print("Google 試算表回應：", response.text)
except Exception as e:
    print(f"傳送至試算表失敗: {e}")

print("\n------------ 執行完畢 ------------")
