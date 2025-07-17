import csv


import requests
from bs4 import BeautifulSoup
import time

from networkx import edges
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from requests.exceptions import Timeout
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import wait
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import EdgeOptions
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def read_urls_from_file(file_path):
    """从文件中读取URL列表"""
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls

def get_web_text(url):
    """获取网页的文本内容"""
    try:


        ques_classes = ['grkj_container','dw','time']
        ans_classes='wdjd_wenti_top_box2_list_content'
        question={
            '问题':'',
            '地点':'',
            '时间':'',
        }
        from selenium.webdriver.chrome.options import Options
        options =EdgeOptions()
        options.add_argument("--headless=new")  # Edge 114+版本推荐使用new模式
        # 关键配置
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)



        # 模拟真实浏览器指纹
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # 禁用图片
            "profile.managed_default_content_settings.stylesheets": 2,  # 禁用CSS
        }
        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Edge(options=options)

        # 删除自动化特征
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                });
            """
        })
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(4)


        if "user/index.shtml" in driver.current_url:
            print("被跳转了！尝试重定向回来")
            driver.get(url)

        print(driver.current_url)

        time.sleep(5)

        lst=['玉米','水稻']
        element=driver.find_element(By.CLASS_NAME, ques_classes[0])


        if element is not None:
            h6_element = element.find_element(By.TAG_NAME, "h6")
            print(h6_element)
            if h6_element is not None:
                question['问题'] = h6_element.text.strip()
                # if not any(element in question['问题'] for element in lst):
                #     return None,None

            address=element.find_element(By.CLASS_NAME,ques_classes[1])
            question['地点'] = address.text.strip()

            times = element.find_element(By.CLASS_NAME,ques_classes[2])
            question['时间'] = times.text.strip()



        elements = driver.find_elements(By.CLASS_NAME, ans_classes)
        num_elements=len(elements)
        answer=[]
        for ele in elements:
            ans={
            '回答':'',
            '地点':'',
            '时间':'',
            }
            anws=ele.find_element(By.CLASS_NAME, 'wdjd_wenti_top_box2_text')
            if anws is not None:
                ans['回答']=anws.text.strip()
            ans['地点']=ele.find_element(By.CLASS_NAME,'dw').text.strip()
            ans['时间']=ele.find_element(By.CLASS_NAME,'time').text.strip()
            answer.append(ans)


        return question,answer
    except WebDriverException as e:
        print(f"Selenium 错误: {e}")
        return None, None
    except Exception as e:
        print(f"其他错误: {e}")
        return None, None
    # finally:
    #     driver.quit()


def save_to_csv(data, csv_file):
    """将数据保存到CSV文件中"""
    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # 写入表头
        # writer.writerow(['URL', 'q','a'])
        # 写入数据
        for url,  qas,ans in data:
            writer.writerow([url, qas,ans])

def main():
    # # 保存结果的CSV文件路径
    csv_file = 'qa.csv'
    csv_file_ = 'kong.csv'

    begin=34600004
    end=34610000

    for i in range(begin,end):
        data = []
        url='https://njtg.nercita.org.cn/tech/question/detail.shtml?quesId='+str(i)
        ques,ans = get_web_text(url)
        if ques:
            data.append([i,ques,ans])
            print(data)
            save_to_csv(data, csv_file)
        else:
            data.append([i,i,i])
            print(data)
            save_to_csv(data, csv_file_)



if __name__ == "__main__":
    main()