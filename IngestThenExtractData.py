import os
import re
from datetime import datetime
import datetime as DT
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import json

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def function():
    path = os.getcwd() + "/matches/"
    raw = os.listdir(path)[-1]
    regex_date = re.search(r'\d{4}-\d{2}-\d{2}', raw)
    latest_date = datetime.strptime(regex_date.group(), '%Y-%m-%d').date()
    print("Get the match data from factor.gg")
    matches = []
    today = DT.date.today()
    mainline = "https://www.factor.gg/schedule?region=all&date="
    latest_date = latest_date + DT.timedelta(days=1)
    mainline += str(latest_date)
    while str(today) > str(latest_date):
        driver.get(mainline)
        try:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div/main/div[1]/div[2]/div/div[3]/div[2]/div/a/div')))
        except Exception:
            past = latest_date
            print("Day will be incremented: " + mainline)
            latest_date = latest_date + DT.timedelta(days=1)
            mainline = mainline.replace(str(past), str(latest_date))
            continue
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div[1]/div[2]/div/div[3]/div[2]/div/a/div')
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('a')
        links = [link.get("href") for link in links]
        links = [link for link in links if '/match/' in link]
        match_urls = [f"https://www.factor.gg/{link}" for link in links]
        distinct_match_urls = list(dict.fromkeys(match_urls))
        matches.append(distinct_match_urls)
        print(distinct_match_urls)

        for url in distinct_match_urls:
            team = url.split("/")[-1]
            url = url + "/1/statistics"
            driver.get(url)
            try:
                WebDriverWait(driver, 50).until(EC.presence_of_element_located(
                    (By.ID, '__NEXT_DATA__')))
            except Exception as e:
                print(e)
                continue
            driver.find_element(By.ID, '__NEXT_DATA__')
            html = driver.page_source

            soup = BeautifulSoup(html, 'lxml')
            data = soup.find("script", {"id": "__NEXT_DATA__"})
            data = data.text
            if data.startswith('<script id="__NEXT_DATA__" type="application/json">'):
                data = data[len('<script id="__NEXT_DATA__" type="application/json">'):]
            if data.endswith('</script>'):
                data = data[:len('</script>')]
            json_data = json.loads(data)
            formatted = json.dumps(json_data, sort_keys=True, indent=4)
            flattened = flatten_json(json.loads(formatted))
            tmp = pd.json_normalize(flattened)
            if not os.path.isfile(os.getcwd() + "/new_matches/match" + str(latest_date) + team + ".csv"):
                tmp.to_csv(os.getcwd() + "/new_matches/match" + str(latest_date) + team + ".csv")
                oldestmatch = (os.listdir(os.getcwd() + "/matches/"))[0]
                os.remove(os.getcwd() + "/matches/" + oldestmatch)
                print("Success removing: " + oldestmatch)
        past = latest_date
        latest_date = latest_date + DT.timedelta(days=1)
        mainline = mainline.replace(str(past), str(latest_date))
    today = DT.date.today()
    today = today + DT.timedelta(days=1)
    mainline = "https://www.factor.gg/schedule?region=all&date="
    mainline += str(today)
    future = today + DT.timedelta(days=6)
    future = str(future)
    print("Get the future match data from factor.gg")
    while str(today) < future:
        driver.get(mainline)
        try:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div/main/div[1]/div[2]/div/div[3]/div[2]/div/a/div')))
        except Exception:
            past = today
            print("Day will be incremented: " + mainline)
            today = today + DT.timedelta(days=1)
            mainline = mainline.replace(str(past), str(today))
            continue
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div[1]/div[2]/div/div[3]/div[2]/div/a/div')
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('a')
        links = [link.get("href") for link in links]
        links = [link for link in links if '/match/' in link]
        match_urls = [f"https://www.factor.gg/{link}" for link in links]
        distinct_match_urls = list(dict.fromkeys(match_urls))
        matches.append(distinct_match_urls)
        print(distinct_match_urls)
        for url in distinct_match_urls:
            team = url.split("/")[-1]
            url = url + "/1/statistics"
            driver.get(url)
            try:
                WebDriverWait(driver, 50).until(EC.presence_of_element_located(
                    (By.ID, '__NEXT_DATA__')))
            except Exception as e:
                print(e)
                continue
            driver.find_element(By.ID, '__NEXT_DATA__')
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            data = soup.find("script", {"id": "__NEXT_DATA__"})
            data = data.text
            if data.startswith('<script id="__NEXT_DATA__" type="application/json">'):
                data = data[len('<script id="__NEXT_DATA__" type="application/json">'):]
            if data.endswith('</script>'):
                data = data[:len('</script>')]
            json_data = json.loads(data)
            formatted = json.dumps(json_data, sort_keys=True, indent=4)
            flattened = flatten_json(json.loads(formatted))
            tmp = pd.json_normalize(flattened)
            if not os.path.isfile(os.getcwd() + "/future/match" + str(today) + team + ".csv"):
                tmp.to_csv(os.getcwd() + "/future/match" + str(today) + team + ".csv")
        past = today
        print("Day will be incremented: " + mainline)
        today = today + DT.timedelta(days=1)
        mainline = mainline.replace(str(past), str(today))


function()
