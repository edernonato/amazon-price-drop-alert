import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import lxml
import smtplib
from threading import Thread
import time

global URL
new_url = False


def write_new_url():
    global URL
    global new_url
    URL = input("Type or paste the URL of the Amazon product within 10sec:\n")
    with open("product_url.txt", "w") as new_file:
        new_file.write(URL)
        new_file.close()
        new_url = True


def write_new_price(new_price):
    with open("product_price.txt", "w") as new_price_file:
        new_price_file.write(str(new_price))
        new_price_file.close()


def read_old_url():
    global URL
    with open("product_url.txt", "r") as old_file:
        URL = old_file.read()
        old_file.close()


new_url_thread = Thread(target=write_new_url).start()
time.sleep(5)
if not new_url:
    read_old_url()

headers = {"Accept-Language": "en-US,en;q=0.9", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/53"
                                                              "7.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}

response = requests.get(URL, headers=headers)
website = response.text

soup = BeautifulSoup(website, "lxml")
price_tag = soup.find(name="span", class_="a-offscreen")
product_name = soup.find(name="span", id="productTitle").text.replace("    ", "")
price_text = price_tag.text
price = int(price_text.split("$")[1].replace(",", "").replace(".", ""))
image = soup.find(name="img", id="landingImage").get("data-old-hires")

if new_url:
    write_new_price(price)

html_body = f"""
        <a href='{URL}'><h4>{product_name} is {price_text} on Amazon!</h4></a>
        <img src={image}></img> \n
"""

EMAIL_FROM = "edernonato47teste@hotmail.com"
PASSWORD = "Eder@teste321"
SMTP = "smtp-mail.outlook.com"
PORT = 587
EMAIL_TO = "edernonato@outlook.com"

email_message = MIMEMultipart()
email_message["from"] = EMAIL_FROM
email_message["to"] = EMAIL_TO
email_message["subject"] = f"{product_name} price dropped to : {price_text}!"


html_start = f"""
<html>
    <head> 
        <title>{product_name} price dropped to : {price_text}!</title>
    </head>
    <body>   
"""

html_end = """
    </body>
</html> 
"""

html = html_start + html_body + html_end
email_message.attach(MIMEText(html, "html"))

try:
    with open("product_price.txt", "r") as old_price_file:
        old_price = int(old_price_file.read())
except Exception as exp:
    print(exp)
    with open("product_price.txt", "w") as file:
        write_new_price(price)
        print("File generated")
        old_price = price + 1

if price < old_price or new_url:
    write_new_price(price)
    print(f"Price is lower than it was before. Sending email to {EMAIL_TO}")
    connection = smtplib.SMTP(SMTP, PORT)
    connection.starttls()
    connection.login(user=EMAIL_FROM, password=PASSWORD)
    connection.sendmail(from_addr=EMAIL_FROM, to_addrs=EMAIL_TO, msg=email_message.as_string())
else:
    print("Price is not lower than before. Email not sent")

print(URL)
print(price)
print(new_url)
os._exit(1)
