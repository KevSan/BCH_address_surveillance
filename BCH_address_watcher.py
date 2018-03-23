import smtplib
import psycopg2
import time
from email.mime.text import MIMEText


with open("passwords.keys", "r") as my_file:
    private_keys = my_file.readlines()
    password = private_keys[0]
    POSTGRES_DB = private_keys[1]


def send_email_notification(mssg):

    sender = "alerts@altcoinadvisors.com"
    receivers = ["kevin@altcoinadvisors.com"]

    subject = "Stack Overflow Test"
    msg = MIMEText(mssg)
    msg['Subject'] = subject
    msg['To'] = ",".join(receivers)
    msg['From'] = sender

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receivers, msg.as_string())
        server.close()

    except Exception as e:
        print("Error: email has not gone through.")
        print(e)


def get_current_block_num(cursor):

    query = "select max(block_num) from bchblockchain.block_info"
    cursor.execute(query)
    current_block_num = cursor.fetchone()[0]

    return current_block_num


def check_for_address(cursor, block_num, address):
    query = "select * from (" + \
            "select * from bchblockchain.tx_inputs where block_num = " + \
            str(block_num) + ") as sub where sub.vin_address = '" + address + "'"

    cursor.execute(query)
    current_reults = cursor.fetchall()

    return current_reults


if __name__ == '__main__':

    connection = psycopg2.connect(POSTGRES_DB)
    cur = connection.cursor()

    block_num = get_current_block_num(cur) - 1

    while True:
        while block_num == get_current_block_num(cur):
            time.sleep(10)

        block_num = get_current_block_num(cur)

        list_of_transactions = check_for_address(cur, block_num, "1NrMNvxsDwsQ9DA4styegmTue9tPPsV9bg")

        if len(list_of_transactions) != 0:
            send_email_notification("Movement on this address")  # need to make a specific email for the movement
        else:
            send_email_notification("test")
            pass
