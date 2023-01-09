from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import lxml
import smtplib

URL = input("Type or paste the URL of the Amazon product:\n")

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
    with open("product_price.txt", "r") as old_file:
        old_price = int(old_file.read())
except Exception as exp:
    print(exp)
    with open("product_price.txt", "w") as file:
        file.write(str(price))
        print("File generated")
        old_price = price + 1

if price < old_price:
    with open("product_price.txt", "w") as file:
        file.write(str(price))
    print(f"Price is lower than it was before. Sending email to {EMAIL_TO}")
    connection = smtplib.SMTP(SMTP, PORT)
    connection.starttls()
    connection.login(user=EMAIL_FROM, password=PASSWORD)
    connection.sendmail(from_addr=EMAIL_FROM, to_addrs=EMAIL_TO, msg=email_message.as_string())
else:
    print("Price is not lower than before. Email not sent")
