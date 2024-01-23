# copyright Ruben Decrop 2012 - 2021
# copyright Chessdevil Consulting BVBA 2015 - 2020

# this file is written by Ruben Decrop, and is derived from source code
# written by Chessdevil Consulting BVBA
# This file can only be used as is for the frbe-kbsb-ksb.be website
# for any other use a written agreement is required by Chessdevil Consulting

import logging
from markdown2 import Markdown
from io import BytesIO
from typing import List, Any
import os.path
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from kbsb import settings

# from kbsb.models.md_book100 import Book100Optional

from .mailbackend import backends

log = logging.getLogger(__name__)
md = Markdown()


def test_mail():
    """
    send a test mail
    """
    try:
        sender = settings.EMAIL["sender"]
        receiver = "ruben.decrop@gmail.com"
        msg = MIMEMultipart("relate1")
        msg["Subject"] = "Testmail 2"
        msg["From"] = sender
        msg["To"] = receiver
        if settings.EMAIL.get("blindcopy"):
            msg["Bcc"] = settings.EMAIL["blindcopy"]
        msg.preamble = "This is a multi-part message in MIME format."
        msgAlternative = MIMEMultipart("alternative")
        msgText = MIMEText("Hi it is I Leclercq, I am in disguise")
        msgAlternative.attach(msgText)
        msgText = MIMEText("Hi, It is I <b>Leclercq</b> I am in disguise", "html")
        msgAlternative.attach(msgText)
        msg.attach(msgAlternative)
        backend = backends[settings.EMAIL["backend"]]()
        backend.send_message(msg)
        log.info(f"testmail sent for {receiver}")
    except Exception:
        log.exception("failed")


title_100 = (
    "Bestelling boek 100 jaar / Commende du liver 100 ans / Bestellung Buch 100 Jahre"
)
message_100 = """
Bedankt voor je bestelling / Merci pour votre commande / Danke für Ihre Bestellung

## Details

Naam / Nom / Name: **{name}**

E-mail: **{email}**

GSM / Handy: **{mobile}** 

Adres / Adresse: **{address}**

Taal / Langue/ Sprache: **{books}**


## Levering / Livraison / Lieferung
 - Luc Cornet: luc.cornet@frbe-kbsb-ksb.be, +32474995274
 - Philippe Vukojevic: philippe.vukojevic@frbe-kbsb-ksb.be, +32497166318
 - Bernard Malfliet: bernard.malfliet@frbe-kbsb-ksb.be, +32471983387
 - Ruben Decrop: ruben.decrop@frbe-kbsb-ksb.be, +32477571313
 - Laurent Wery: laurent.wery@frbe-kbsb-ksb.be, +32491736871
 - Gûnter Delhaes: delhaes.g@skynet.be
 - Frank Hoffmeister: Frank.HOFFMEISTER@ec.europa.eu
 - DPD

Jij hebt gekozen / Vous avez choisi / Sie haben gewählt: **{distribution}**

## Betaling / Paiement/ Zahlung

Bedrag / Montant / Betrag: **{cost} Euro**

Rekeningnummer / Compte / Konto: **BE76 0015 9823 0095**

Naam / Nom / Name: **FRBE-KBSB-KSB**

Mededeling / Communication / Mitteilung:  **Book 100 / {ordernr}**
"""


# def sendconfirmation_book100(b: Book100Optional):
#     """
#     send confirmation email
#     :param b:  The order
#     :return: None
#     """
#     log.info(f"sending mail for {b}")
#     order = {
#         "idbel": b.id_bel,
#         "address": b.address,
#         "books": ", ".join(b.books.split(",")),
#         "cost": b.cost,
#         "distribution": b.distribution.upper(),
#         "email": b.email,
#         "name": f"{b.first_name} {b.last_name}",
#         "mobile": b.mobile,
#         "ordernr": b.order,
#     }
#     log.info(f"order {order}")
#     tolist = [b.email]
#     text = message_100.format(**order)

#     # fetch the subject from the first line
#     htmltext = md.convert(text)

#     # create message and send it
#     try:
#         msg = MIMEMultipart("related")
#         msg["Subject"] = title_100
#         msg["From"] = settings.EMAIL["sender"]
#         msg["To"] = ",".join(tolist)
#         msg["Cc"] = settings.BOOKS_CC
#         msg.preamble = "This is a multi-part message in MIME format."
#         msgAlternative = MIMEMultipart("alternative")
#         msgText = MIMEText(text)
#         msgAlternative.attach(msgText)
#         msgHtml = MIMEText(htmltext, "html")
#         msgAlternative.attach(msgHtml)
#         msg.attach(msgAlternative)
#         backend = backends[settings.EMAIL["backend"]]()
#         backend.send_message(msg)
#         log.info(f"book 100 confirmation mail sent for {b.first_name} {b.last_name}")
#     except:
#         log.exception(f"confirmation mail failed {b.first_name} {b.last_name}")
