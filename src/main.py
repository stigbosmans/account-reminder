import datetime
import os
import requests
import logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

notion_token = os.getenv("NOTION_TOKEN")
db = os.getenv("DATABASE_ID")
sendgrid_token = os.getenv("SENDGRID_TOKEN")

logging.getLogger().setLevel(logging.INFO)

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


def check_if_payment_is_overtime(page_properties):
    try:
        participant_page_id = page_properties["Deelnemer"]["relation"][0]["id"]
        participant_page = get_notion_page(participant_page_id)
        props = {"payed": page_properties["Betaald"]["checkbox"],
                 "start_date": page_properties["Periode"]["date"]["start"],
                 "end_date": page_properties["Periode"]["date"]["end"],
                 "service": page_properties["Service"]["select"]["name"],
                 "amount": page_properties["Bedrag"]["number"],
                 "participant_name": participant_page["properties"]["Name"]["title"][0]["plain_text"],
                 "participant_email": participant_page["properties"]["Email"]["rich_text"][0]["plain_text"]
                 }
        if not props["payed"]:
            end_date = datetime.strptime(props["end_date"], "%Y-%m-%d")
            today = datetime.now()
            if end_date < today:
                send_mail_reminder(props)
    except KeyError:
        logging.error("Page ignored due to key error", page_properties)


def send_mail_reminder(mail_data):
    message = Mail(
        from_email='noreply@rollo-innovators.be',
        to_emails=("stigbosmans@gmail.com", "stig.bosmans@rollo.ml"),
        subject=f'Tegoed {mail_data["service"]}',
        html_content=f"""
        Beste {mail_data["participant_name"]},
        Uit onze records blijkt dat u nog een tegoed van {mail_data["amount"]} euro verschuldigd bent 
        vanwege het gebruik van {mail_data["service"]} 
        voor de periode van {mail_data["start_date"]} tot {mail_data["end_date"]}.<br/>
        Gelieve, dit spoedig te storten op het rekeningnummer: BE21 9731 3149 0103 en na betaling een Whatsappje te sturen naar
        uw contactpersoon Stig Bosmans.<br/>
        Let op: u kan niet terugmailen op dit adres.
        <br/><br/>
        Stig Bosmans
        stig.bosmans@rollo.ml
        """
    )
    sg = SendGridAPIClient(sendgrid_token)
    sg.send(message)
    logging.info(f"Mail send to {mail_data['participant_email']}")


database = get_notion_database(db)
for i in database["results"]:
    check_if_payment_is_overtime(i["properties"])


