#! /usr/bin/env python

"""Download files to onedrive offline.

Usage:
  offline_download.py [--name=FILENAME] <url>
  offline_download.py (-h | --help)
  offline_download.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""

import os
import urllib

import requests
from docopt import docopt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_auth_code(
        username, password, client_id, redirect_uri,
        url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize", time_wait=60):
    """https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/getting-started/authentication?view=odsp-graph-online"""
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": 'Files.ReadWrite',
    }

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('{}?{}'.format(url, urllib.parse.urlencode(params)))

    try:
        element = WebDriverWait(driver, time_wait).until(
            EC.element_to_be_clickable((By.NAME, "loginfmt"))
        )
        element.clear()
        element.send_keys(username)
        element.send_keys(Keys.RETURN)

        element = WebDriverWait(driver, time_wait).until(
            EC.element_to_be_clickable((By.NAME, "passwd"))
        )
        element.clear()
        element.send_keys(password)
        element.send_keys(Keys.RETURN)

        element = WebDriverWait(driver, time_wait).until(
            EC.element_to_be_clickable((By.ID, "idBtn_Accept"))
        )
        element.send_keys(Keys.RETURN)

        location = driver.current_url
        driver.close()
    except Exception as e:
        print(e)
        exit()
    finally:
        driver.quit()
    return urllib.parse.parse_qs(urllib.parse.urlparse(location).query)['code'][0]


def redeem_token(code, client_id, redirect_uri,
                 url="https://login.microsoftonline.com/common/oauth2/v2.0/token"):
    data = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": code,
        "grant_type": "authorization_code",
    }
    return requests.post(url, data).json()


def auth(username, password, client_id,
         redirect_uri="https://login.microsoftonline.com/common/oauth2/nativeclient"):
    code = get_auth_code(username, password, client_id, redirect_uri)
    return redeem_token(code, client_id, redirect_uri)['access_token']


def offline_download(token, target_url, file_name=None,
                     url="https://graph.microsoft.com/v1.0/me/drive/items/root/children"):
    """https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/driveitem_upload_url?view=odsp-graph-online"""

    if not file_name:
        file_name = os.path.basename(urllib.parse.urlparse(target_url).path)

    data = {
        "@microsoft.graph.sourceUrl": target_url,
        "name": file_name,
        "file": {}
    }

    headers = {
        "Prefer": "respond-async",
        "Authorization": "Bearer {}".format(token),
    }

    r = requests.post(url, json=data, headers=headers)
    return r.headers['Location']


def main(url, file_name=None):
    token = auth(
        os.getenv("MS_USERNAME"),
        os.getenv("MS_PASSWORD"),
        os.getenv("MS_CLIENT_ID"),
    )
    return offline_download(token, url, file_name)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Offline Download 1.0.0')
    monitor_url = main(arguments['<url>'], arguments['--name'])
    print(monitor_url)
