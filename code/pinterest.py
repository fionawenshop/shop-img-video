import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ==================== 【你只改这里】====================
ROOT_FOLDER = r"C:\Users\wenha\Documents\衣服图片\00ther\ALL"
PINTEREST_EMAIL = "fionawenshop@gmail.com"
PINTEREST_PWD = "wenhao1996"
TARGET_BOARD = "Women Dresses"
BASE_LINK = "https://www.fionawen.com/pages/all"
DESC_SUFFIX = "Wholesale women fashion dress, fast shipping worldwide."

# 随机延时（防封号）
MIN_SLEEP = 2
MAX_SLEEP = 4
MIN_LONG_SLEEP = 5
MAX_LONG_SLEEP = 9
# ======================================================

IMG_SUFFIX = (".jpg", ".jpeg", ".png", ".webp")

def rand_sleep(short=True):
    if short:
        t = random.uniform(MIN_SLEEP, MAX_SLEEP)
    else:
        t = random.uniform(MIN_LONG_SLEEP, MAX_LONG_SLEEP)
    time.sleep(round(t, 2))

def get_all_images(root_path):
    img_list = []
    for dirpath, _, files in os.walk(root_path):
        for f in files:
            if f.lower().endswith(IMG_SUFFIX):
                full_path = os.path.join(dirpath, f)
                img_list.append(full_path)
    return img_list

def init_browser():
    chrome_opts = Options()
    chrome_opts.add_argument("--start-maximized")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_opts.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_opts)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def pinterest_login(driver):
    driver.get("https://www.pinterest.com/login/")
    rand_sleep(short=False)

    email_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "email"))
    )
    email_input.clear()
    email_input.send_keys(PINTEREST_EMAIL)
    rand_sleep()

    pwd_input = driver.find_element(By.ID, "password")
    pwd_input.clear()
    pwd_input.send_keys(PINTEREST_PWD)
    rand_sleep()

    login_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_btn.click()
    rand_sleep(short=False)
    print("✅ 登录成功")

def upload_single_pin(driver, img_path):
    driver.get("https://www.pinterest.com/pin-builder/")
    rand_sleep()

    # 上传图片
    file_input = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(img_path)
    rand_sleep(short=False)

    filename = os.path.splitext(os.path.basename(img_path))[0]
    title_text = filename.replace("-", " ").replace("_", " ").title()

    # 标题
    try:
        title_inp = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, '//textarea[contains(@placeholder,"title")]'))
        )
        title_inp.clear()
        title_inp.send_keys(title_text)
        rand_sleep()
    except:
        pass

    # 描述
    try:
        desc_inp = driver.find_element(By.XPATH, '//textarea[contains(@placeholder,"about")]')
        desc_inp.clear()
        desc_inp.send_keys(f"{title_text}. {DESC_SUFFIX}")
        rand_sleep()
    except:
        pass

    # 外链
    try:
        link_inp = driver.find_element(By.XPATH, '//input[contains(@placeholder,"destination") or contains(@placeholder,"link")]')
        link_inp.clear()
        link_inp.send_keys(BASE_LINK)
        rand_sleep()
    except:
        pass

    # 选择画板（新版Pinterest）
    try:
        board_btn = WebDriverWait(driver,5).until(
            EC.element_to_be_clickable((By.XPATH, f'//div[text()="{TARGET_BOARD}"]'))
        )
        board_btn.click()
        rand_sleep()
    except Exception as e:
        print(f"⚠️  画板已选择或无需选择: {str(e)[:50]}")

    # 发布（新版按钮定位）
    try:
        publish_btn = WebDriverWait(driver,5).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and (contains(.,"Publish") or contains(.,"Save"))]'))
        )
        publish_btn.click()
        rand_sleep(short=False)
        print(f"✅ 发布成功: {os.path.basename(img_path)}")
    except Exception as e:
        print(f"⚠️  发布按钮点击失败: {str(e)[:50]}")

def main():
    img_list = get_all_images(ROOT_FOLDER)
    if not img_list:
        print("❌ 未找到图片")
        return
    print(f"📸 找到图片总数: {len(img_list)}")

    driver = init_browser()
    try:
        pinterest_login(driver)
        for i, img in enumerate(img_list, 1):
            print(f"\n----- 上传 {i}/{len(img_list)} -----")
            upload_single_pin(driver, img)
            rand_sleep(short=False)
    except Exception as e:
        print(f"\n❌ 运行异常: {str(e)[:100]}")
    finally:
        driver.quit()
        print("\n✅ 任务结束")

if __name__ == "__main__":
    main()