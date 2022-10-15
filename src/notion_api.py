import os
import requests
import logging
notion_token = os.getenv("NOTION_TOKEN")

headers = {
    "Authorization": "Bearer " + notion_token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def get_notion_database(db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    res = requests.request("POST", url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return data
    else:
        logging.error(f"Couldn't retrieve data for db {db_id}. Status code: ", res.status_code)


def get_notion_page(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    res = requests.request("GET", url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        return data
    else:
        logging.error(f"Couldn't retrieve data for page {page_id}. Status code: ", res.status_code)
