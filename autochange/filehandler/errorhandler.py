import os
import exchangelib
import configparser


def send_warning(recipients):
    '''
    Send warning to recipients

    Args:
        recipients (str or list): Recipients of warnings

    '''
    # Get credentials from external ini file
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'config.ini')
    parser = configparser.ConfigParser()
    parser.read(filename)
    username = parser.get("credentials", "username")
    password = parser.get("credentials", "password")
    email = parser.get("credentials", "email")

    # Log in to mail adress with credentials from ini file
    credentials = exchangelib.Credentials(username=username,
                                          password=password)

    config = exchangelib.Configuration(server='mail.statens-it.dk',
                                       credentials=credentials)
    account = exchangelib.Account(primary_smtp_address=email,
                                  config=config,
                                  autodiscover=False,
                                  access_type=exchangelib.DELEGATE)

    if isinstance(recipients, list):
        recipients_list = [exchangelib.Mailbox(email_address=adr)
                           for adr in recipients]
    else:
        recipients_list = [exchangelib.Mailbox(email_address=recipients)]

    # Compose and send message
    m = exchangelib.Message(
        account=account,
        subject="WARNING WARNING WARNING: automated-changes stopped",
        body="",
        to_recipients=recipients_list
    )
    m.send()
