import datetime
import os
import logging
from datetime import datetime
import schedule
import time

from notion_api import get_notion_database, get_notion_page
from sendgrid_api import send_mail
db = os.getenv("DATABASE_ID")


logging.getLogger().setLevel(logging.INFO)


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
                send_reminder(props)
    except KeyError:
        logging.error("Page ignored due to key error", page_properties)


def send_reminder(mail_data):
    mail_content = f"""
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
    send_mail("noreply@rollo-innovators.be", ["stigbosmans@gmail.com", mail_data["participant_email"]],
              f'Tegoed {mail_data["service"]}', mail_content)


def check_late_payers():
    logging.info(f'Checking datebase for late payers at {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    database = get_notion_database(db)
    for i in database["results"]:
        check_if_payment_is_overtime(i["properties"])


schedule.every(1).week.do(check_late_payers)
check_late_payers()

logging.info("Schedule is running")
while 1:
    schedule.run_pending()
    time.sleep(1)
