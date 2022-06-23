#!/usr/bin/python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import utilities
import os
import time

# Maximum wait time to load a website
MAX_TIMEOUT = 60
# Maximum wait time to load a single website element (e.g. a button)
TIMEOUT = 10

TELEGRAM_URL = "https://web.telegram.org/k/"

class TelegramController:
    """
    Class used to interact with the telegram web ui
    ...
    Attributes
    ----------
    phone_number : str
        the phone number of the account
    login_state : Webdriver object
        the used webdriver to navigate through telegram
    login_status : bool
        true if the account is logged in, otherwise false
    contacts : dictionary
        contains the contacts user name and their id
    Methods
    -------
    # TODO: document
    """
    def __init__(self, driver_path, debugging=False):
        options = webdriver.FirefoxOptions()
        if not debugging:
            options.add_argument('--headless')
        self.driver = webdriver.Firefox(executable_path=driver_path, options=options)
        self.login_state = False
        while not self.login_state:
            try:
                self.__login()
                if not self.login_state:
                    answer = input("ERROR: login was not successfull. Try again (yes/no)?").lower()
                    if answer in ["yes", "y"]:
                        continue
                    elif answer in ["no", "n"]:
                        break
            except KeyboardInterrupt:
                print("Returning to messenger selection")
                return None
            # Executed if no exception thrown
            else:
                # TODO: offer retry or abort on error
                print("Loading contacts...")
                self.contacts = self.__get_contacts()


    def __login(self,):
        login_status = False
        self.driver.get(TELEGRAM_URL)
        try:
            print("Please enter your phone number with country code, example: +49123456789")
            self.phone_number = input()
            # Click on "Login by phone number" button
            WebDriverWait(self.driver, TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div[2]/button[1]'))).click()
            # Wait for phone number input field76
            WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[3]/div[2]/div[1]')))
            number_input = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[1]/div/div[3]/div[2]/div[1]')
            number_input.send_keys(Keys.CONTROL + "a")
            number_input.send_keys(Keys.DELETE)
            number_input.send_keys(self.phone_number)
            number_input.send_keys(Keys.ENTER)

            auth_code = input("Telegram Authentication Code:\n")
            # Verification code field
            WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[3]/div/div[3]/div/input')))
            auth_code_field = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div[2]/div[3]/div/div[3]/div/input')
            auth_code_field.send_keys(auth_code)
            auth_code_field.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div')))
            self.login_state = True
        except TimeoutException:
            print("Timed out waiting for page to load")
        return login_status

    def __get_contacts(self,):
        contacts = {}
        duplicate_names = []
        # Add contacts from bottom of list (inactive contacts) to top (online)
        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div')))
        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div'))).send_keys(Keys.PAGE_DOWN)
        new_contact_added = True
        while new_contact_added:
            new_contact_added = False
            contacts_lists = self.driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div')
            for contacts_list in contacts_lists:
                for contact in contacts_list.find_elements(by=By.XPATH, value='.//ul/li'):
                    name = contact.find_element(by=By.XPATH, value='.//div[2]/p[1]/span[1]/span').text
                    id = contact.find_element(by=By.XPATH, value='.//div[2]/p[1]/span[1]/span').get_attribute("data-peer-id")
                    if id not in contacts:
                        contacts[id] = name
                        duplicate_names.append(name)
                        new_contact_added = True
            contacts_lists[0].send_keys(Keys.PAGE_UP)
        # Check if additional information is needed in case of same contact names
        duplicate_names = list(filter(lambda x: len(x)==1, duplicate_names))
        if duplicate_names:
            for dupe in duplicate_names:
                name_search_bar = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[1]/div[1]/div/div/div[1]/div[2]/input')
                name_search_bar.send_keys(Keys.CONTROL + "a")
                name_search_bar.send_keys(Keys.DELETE)
                name_search_bar.send_keys(dupe)
                WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[2]/div[2]/div/div/div[1]/div/div[1]/ul/li[1]/div[1]')))

                # Get contact phone number / id
                search_results = self.driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[2]/div[2]/div/div/div[1]/div/div[1]/ul/li')
                for contact in search_results:
                    id = contact.find_element(by=By.XPATH, value='.//div[2]/p[1]/span[1]/span').get_attribute("data-peer-id")
                    name = "%s (%s)" % (contacts[id], contact.find_element(by=By.XPATH, value='.//div[2]/p[2]/span').text)
                    contacts[id] = name
        WebDriverWait(self.driver, TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div[3]'))).click()
        # swap key (id) and value (name) to be consistent with other messenger services
        return dict((value, key) for key, value in contacts.items())

    def open_chat(self, target_name):
        new_messages = []
        chat_history = []

        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div')))
        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div'))).send_keys(Keys.PAGE_DOWN)
        target_id = self.contacts[target_name]
        target_found = False
        while not target_found:
            contacts_lists = self.driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div[1]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div')
            for contacts_list in contacts_lists:
                for contact in contacts_list.find_elements(by=By.XPATH, value='.//ul/li'):
                    id = contact.find_element(by=By.XPATH, value='.//div[2]/p[1]/span[1]/span').get_attribute("data-peer-id")
                    if target_id == id:
                        contact.click()
                        target_found = True
            if not target_found:
                contacts_lists[0].send_keys(Keys.PAGE_UP)
            else:
                new_messages = self.__read_chat_history()
            chat_history = new_messages
            input_field = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[1]/div[2]/div/div/div[4]/div/div[1]/div/div[8]/div[1]/div[1]')
            while True:
                # start new thread to check if new messages arrive
                try:
                    utilities.clear_terminal()
                    for message in chat_history:
                        print(message)

                    input_field.send_keys(input("Send message (ctrl + c to quit):"))
                    input_field.send_keys(Keys.ENTER)
                    # wait until new message moved all div container
                    time.sleep(2)
                    chat_history = self.__read_chat_history()
                except KeyboardInterrupt:
                    break
        return target_found

    def __read_chat_history(self, max_messages=0):
        message_list = []
        for dategroup_messages in self.driver.find_elements(by=By.CLASS_NAME, value='bubbles-date-group'):
            date = dategroup_messages.find_element(by=By.XPATH, value=".//div[1]/div/div/span").text
            if not date:
                date = dategroup_messages.find_element(by=By.XPATH, value=".//div[2]/div/div/span").text
            time.sleep(1)
            for message_element in dategroup_messages.find_elements(by=By.CLASS_NAME, value='message'):
                if message_element.value_of_css_property("--message-background-color") == "#eeffde":
                    name = "You"
                else:
                    name = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[1]/div[2]/div/div/div[2]/div[1]/div[1]/div/div/div[1]/div/span').text
                message = "[{DATE} {TIME} {NAME}] {MESSAGE}".format(
                        DATE = date
                        , NAME = name
                        , TIME = "".join(message_element.text.split("\n")[-1])
                        , MESSAGE = message_element.text.replace(message_element.text.split("\n")[-1], "")
                    )
                message_list.append(message)
        return message_list


# Entry point for testing
if __name__ == "__main__":
    if os.name == "posix":
        geckodriver_exe = "geckodriver_linux"
    elif os.name in ("nt", "dos", "ce"):
        geckodriver_exe = "geckodriver_win.exe"
    else:
        print("ERROR: No supported driver for Firefox found")
    FIREFOX_PATH = os.path.abspath(geckodriver_exe)
    telegram_ctrl = TelegramController(FIREFOX_PATH, debugging=True)
    if not telegram_ctrl.login_state:
        telegram_ctrl.driver.quit()

    print("Successfully logged in!")

    while True:
        contact_list = list(telegram_ctrl.contacts.keys())
        print("Contacts:")
        for index, key in enumerate(contact_list, start=1):
            print("\t%i. " % index + key)
        try:
            message_target = int(input("Who do you want to contact? (Enter row index, exit with ctrl + c): ")) - 1
            target_name = contact_list[message_target]
            print("Opening chat with %s" % target_name)
            if not telegram_ctrl.open_chat(target_name):
                # TODO: add error handling
                print("ERROR: Could not open chat")
        except KeyboardInterrupt:
            break
