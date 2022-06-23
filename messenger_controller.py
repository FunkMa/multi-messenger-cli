from datetime import date
from unicodedata import name
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import getpass
import time
import utilities

TIMEOUT = 60


class MessengerController:
    def __init__(self, driver_path, test=False):
        options = webdriver.FirefoxOptions()
        if not test:
            options.add_argument('--headless')
        self.driver = webdriver.Firefox(
            executable_path=driver_path, options=options)
        self.login_state = self.__login()
        if self.login_state:
            self.contacts = self.__get_contacts()

    def __login(self,):
        try:
            login_status = False
            self.driver.get("https://www.messenger.com/login")

            # Wait for Cookie Field
            WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located(
                (By.CLASS_NAME, '_9xo5')))
            number_input = self.driver.find_elements(
                by=By.CLASS_NAME, value='_9xo5')
            number_input[0].click()

            while(not login_status):
                # Wait for Username input field
                WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located(
                    (By.ID, 'email')))
                email_input = self.driver.find_element(
                    by=By.ID, value='email')
                email_input.send_keys(input("Please enter your Username:"))
                # Wait for Password input field
                WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located(
                    (By.ID, 'pass')))
                password_input = self.driver.find_element(
                    by=By.ID, value='pass')
                password_input.send_keys(
                    getpass.getpass("Please Enter your Password:"))
                # Press the "Continue/Weiter" Button
                weiter_button = self.driver.find_elements(
                    by=By.CLASS_NAME, value='_9h74')
                weiter_button[0].click()
                try:
                    self.driver.find_element(
                        by=By.CLASS_NAME, value='_3403 _3404')
                except:
                    login_status = True
                # Error klasse _3403 _3404
# TODO ERROR HANDLING bei falsch eingabe
        except TimeoutException:
            print("Timed out waiting for page to load")
        return login_status

    def __get_contacts(self,):
        contacts = {}
        duplicate_names = []
        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div[1]/div[2]/div/div/div')))
        contacts_added = True
        while contacts_added:
            contacts_added = False
            chatbox = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@aria-label='Chats']/child::*[last()]")))
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", chatbox)
            time.sleep(1)
            chatbox_groups = self.driver.find_elements(
                By.XPATH, "//*[@aria-label='Chats']")
            for chatbox_group in chatbox_groups:
                chatbox = chatbox_group.find_elements(
                    By.XPATH, '//*[@data-testid="mwthreadlist-item-open"]')
                for chats in chatbox:
                    try:
                        while "Facebook" in chats.find_element(
                                By.XPATH, './/div/div[1]/a/div/div/div[2]/div/div/span/span').text:
                            time.sleep(1)
                        chat_name = chats.find_element(
                            By.XPATH, './/div/div[1]/a/div/div/div[2]/div/div/span/span').text
                        id = chats.find_element(
                            By.XPATH, './/div/div[1]/a').get_attribute("href")
                        if not contacts.get(chat_name, None):
                            contacts[chat_name] = id
                            contacts_added = True
                    except:
                        print("error")
        return contacts
# /html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[4]/div[2]/div/div/div[1]

    def open_chat(self, target_url):
        chat_history = []
        self.driver.get(target_url)
        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div[1]/div/div[3]/div/div/div')))
        chat_history = self.__read_chat_history()
        input_field = self.driver.find_element(
            by=By.XPATH, value="/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div[2]/div/div/div[4]/div[2]/div/div/div[1]")

        while True:
            # start new thread to check if new messages arrive
            try:
                utilities.clear_terminal()
                for messages in chat_history:
                    print(messages)

                for key in input("Send message (ctrl + c to quit):"):
                    input_field.send_keys(key)
                input_field.send_keys(Keys.ENTER)
                # wait until new message moved all div container
                time.sleep(1)
                chat_history = self.__read_chat_history()
                print(chat_history)
            except KeyboardInterrupt:
                break

    def __read_chat_history(self):
        message_list = []
        date = ""
        name = ""
        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div[1]/div/div[1]/div[2]/div[2]/span')))
        for message in self.driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div[1]/div/div[3]/div/div/div/div'):
            try:
                # Datum rausfiltern
                if len(message.text.split("\n")) == 1:
                    date = message.text
                elif len(message.text.split("\n")) == 3:
                    if message.text.split("\n")[0][-1] == ":":
                        name = message.text.split("\n")[0][:-1]
                    else:
                        name = message.text.split("\n")[0]
                    message = "[{DATE} {NAME}] {MESSAGE}".format(
                        DATE=date,
                        NAME=name,
                        MESSAGE=message.text.split("\n")[1]
                    )
                    message_list.append(message)
            except:
                # TODO ERROR Handling
                print("error")
        return message_list


# Entry Point
if __name__ == "__main__":
    if os.name == "posix":
        geckodriver_exe = "geckodriver_linux"
    elif os.name in ("nt", "dos", "ce"):
        geckodriver_exe = "geckodriver_win.exe"
    else:
        print("ERROR: No supported driver for Firefox found")
    FIREFOX_PATH = os.path.abspath(geckodriver_exe)
    messenger_ctrl = MessengerController(FIREFOX_PATH, test=True)
    print("Successfully logged in!")
    print("Contacts:")
    contact_list = list(messenger_ctrl.contacts.keys())
    for index, contact_name in enumerate(contact_list, start=1):
        print("\t%i. %s" % (
            index, contact_name))

    while True:
        try:
            message_target = int(
                input("Who do you want to contact? (Enter row index, exit with ctrl + c): "))
            target_name = contact_list[message_target-1]
            target_url = messenger_ctrl.contacts[target_name]
            print("Opening chat with %s" %
                  target_name)
            if not messenger_ctrl.open_chat(target_url):
                # TODO: add error handling
                print("ERROR: Could not open chat")
        except KeyboardInterrupt:
            break
