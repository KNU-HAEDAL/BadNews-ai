# 매개변수: search_word, save_name(==title)
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib.request
import os
import boto3
import json

with open('./secret.json') as f:
    secrets = json.loads(f.read())
IAM_ACCESS_KEY = secrets["IAM_ACCESS_KEY"]
IAM_SECRET_KEY = secrets["IAM_SECRET_KEY"]


def gen_image(id, search_word):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://pollinations.ai/")

    WebDriverWait(driver, 300).until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="root"]/div[2]/div[1]/div/div[2]/div/div[3]/div[2]/button')))
    driver.find_element(
        By.XPATH, '//*[@id="root"]/div[2]/div[1]/div/div[2]/div/div[3]/div[1]/input').send_keys(search_word)
    driver.find_element(
        By.XPATH, '//*[@id="root"]/div[2]/div[1]/div/div[2]/div/div[3]/div[2]/button').click()
    driver.switch_to.window(driver.window_handles[1])

    url = driver.current_url
    save_name = f"C:\images\{id}.png"
    urllib.request.urlretrieve(url, save_name)

    s3 = s3_connect()

    try:
        s3.upload_file(save_name,"badnews-bucket",f"{id}.png")
    except Exception as e:
        print(e)

    # os.remove(save_name)
    driver.quit()
    result = {
        'id': id,
        'path': save_name
    }
    return result



def s3_connect():
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            aws_access_key_id = IAM_ACCESS_KEY,
            aws_secret_access_key = IAM_SECRET_KEY,
            service_name="s3",
            region_name="ap-northeast-2",
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!") 
        return s3