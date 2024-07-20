#standard
import argparse
import calendar
import configparser
import datetime
import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#third party
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

def check_permit_availability(group_size, desired_month, desired_day, desired_year, url):
    logging.info(f"Checking Reservation at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    global email_sent  # Ensure we're modifying the global variable
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless Chrome. comment out to see the browser actually open.
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    # Allow some time for the page to load
    time.sleep(5)

    try:
        #locate the dropdown button by its class name. Find it using the "inspect" tab on the webpage
        group_button_xpath = "//button[@data-component='Button' and @type='button' and contains(@class, 'sarsa-button') and contains(@class, 'sarsa-button-subtle') and contains(@class, 'sarsa-button-sm') and @aria-label='Add members']"
        group_button = driver.find_element(By.XPATH, group_button_xpath)
        
        for _ in range(group_size):
            group_button.click() #click the plus button once
            time.sleep(1)
    except Exception as e:
        logging.error(f"Error in group button click: {e}")

    try:
        #now change the month to July if the current month is June. This is the only case I need to handle
        current_date = datetime.datetime.now()
        current_month = current_date.month
        num_clicks=desired_month-current_month
        if num_clicks<0:
            raise ValueError("cannot reserve back in time")
        if num_clicks>0:
            month_button_xpath = "//button[@type='button' and @aria-label='Next' and contains(@class, 'next-prev-button')]"
            month_button = driver.find_element(By.XPATH, month_button_xpath)
            for _ in range(num_clicks):
                month_button.click() #go forward in months
                time.sleep(1)
    except Exception as e:
        logging.error(f"Error in month button click: {e}")

    #format the desired date into how the website accepts it
    date_obj = datetime.date(desired_year, desired_month, desired_day)
    day_name = calendar.day_name[date_obj.weekday()] #e.g., Thursday
    month_name = calendar.month_name[desired_month] #e.g., July
    desired_date = f"{day_name}, {month_name} {desired_day}, {desired_year}"
    try:
        # Locate the specific option within the dropdown
        desired_xpath = f"//div[@tabindex='-1' and @role='button' and @aria-label='{desired_date} - Available' and contains(@class, 'calendar-cell') and contains(@class, 'is-styled-day') and contains(@class, 'available')]"
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, desired_xpath))
        )
        
        logging.info(f"Permits available for {desired_date}. Attempting to notify now.")        
        send_email_notification(group_size, desired_date, url)

    except Exception as e:
        logging.info("Date availability element does not exist.")

    driver.quit()

def send_email_generic(receiver_email, subject, body):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    message.add_header('X-Priority', '1') #add priority. may help to prioritize subsequent notifications depending on your email provider
    # Connect to Gmail's SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    logging.info(f"Email sent successfully to {receiver_email}")

def send_email_notification(spots, desired_date, url):
    """
    Notify that availability was found. Keeping the notification email separate from the status email functionality separate for clarity.
    """
    global email_sent  # Ensure we're modifying the global variable

    subject = "Mt. St. Helens Reservation Alert"
    body = f"Permit availability found for {spots} spots on {desired_date}. Book now at {url}!"

    try:
        for receiver_email in receiver_emails:
            send_email_generic(receiver_email, subject, body)
            email_sent = True  # Set flag to true after email is sent

    except Exception as e:
        logging.error(f"Failed to send notification email: {e}")

def send_status_email():
    """
    Notify everyone that the script is still running in the background.
    """
    subject = "Script Status: Still Checking"
    body = f"The script is still running and checking for reservations as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
    
    try:
        for receiver_email in receiver_emails:
            send_email_generic(receiver_email, subject, body)
    
    except Exception as e:
        logging.error(f"Failed to send status email: {e}")

def main(args):
    #schedule the script to run every few seconds
    schedule.every(args.check_availability_every).seconds.do(check_permit_availability,
                                                            args.group_size, 
                                                            args.month, 
                                                            args.day, 
                                                            args.year,
                                                            args.url)
    #schedule the status email to be sent once a day at a specified time
    schedule.every().day.at(args.send_status_at).do(send_status_email)

    while True:
        schedule.run_pending()
        time.sleep(10)  #sleep for 10 seconds. This hardcoded param is a "safety" feature to not overuse CPU.
        if email_sent:
            logging.info("Breaking loop because a successful email was sent")
            break  # Exit the loop once email is sent successfully

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="parsing arguments for mt st helens ticket bot")
    parser.add_argument('--month', type=int, required=True, help="The month of the reservation you want as an int. e.g., 7 for July.")
    parser.add_argument('--day', type=int, required=True, help="The day of the reservation you want as an int. e.g., 4 for the fourth.")
    parser.add_argument('--year', type=int, required=True, help="The year of the reservation you want as an int. e.g., 2024 for the year 2024.")
    parser.add_argument('--group_size', type=int, required=True, default=1, help="The number of people in your group/tickets you need. Recommended to be 1 because in the case you need 2+, you won't miss out if the tickets become available one at a time.")
    parser.add_argument('--url', type=str, required=True, default="https://www.recreation.gov/permits/4675309", help="URL you want to navigate to.")
    parser.add_argument('--config_file', type=str, required=True, default='config/config.ini', help="Path to config file containing email addresses and passwords.")
    parser.add_argument('--check_availability_every', type=int, default=10, help="In seconds, how often to navigate to the website to check availability.")
    parser.add_argument('--send_status_at', type=str, default="13:00", help="As a string in 24H clock, specify when the daily status update email should be sent. e.g., 13:00 for 1pm.")

    # Parse the arguments
    args = parser.parse_args()

    #global scope
    config = configparser.ConfigParser()
    config.read(args.config_file)

    sender_email = config['sender_email']['sender_email'] #email address that you will send the emails from. Probably your email address
    password = config['sender_email']['password'] #your email address password. not your typical login password, but api password. refer to your email provider's docs

    receiver_emails = [] 
    for idx in range(len(config['receiver_emails'])):
        receiver_emails.append(config['receiver_emails'][f'receiver_email{idx+1}'])
    password = config['sender_email']['password']
    logging.basicConfig(filename='reservation_check.log', level=logging.INFO, 
                        format='%(asctime)s:%(levelname)s:%(message)s')
    email_sent=False #will be modified by other functions on successful email being sent.

    main(args)