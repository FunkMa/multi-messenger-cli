from asyncio.windows_events import NULL
from turtle import window_height
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import os
import utilities
import time
from selenium.webdriver.common.action_chains import ActionChains
TIMEOUT = 60

class WhatsAppController:
    def __init__(self, driver_path, test=False):
        self.driver_path = driver_path
        options = webdriver.FirefoxOptions()
        if not test:
            options.add_argument('--headless')
        self.driver = webdriver.Firefox(executable_path=driver_path, options=options)
        self.login_state = self.__login()
        if self.login_state:
            self.contacts = self.__get_contacts()

    def __login(self,):
        login_status = False
        self.driver.get("https://web.whatsapp.com/")
        try:
            # check if QR-Code is loaded then wait and make screenshot
            WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[1]')))
            time.sleep(3)
            qr_element = self.driver.find_element(by= By.XPATH, value="/html/body/div[1]/div/div/div[2]/div[1]")
            qr_element.screenshot("canvas.png")

            print("Scan QR-Code with your device")

            # show image on default OS image viewer
            img = Image.open("canvas.png")
            img.show()

            # when website is changed, the user is succsessfully logged in
            WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[2]')))

            img.close() #Dont work!

            login_status = True
        except TimeoutException:
            print("Timed out waiting for page to load")

        return login_status
    
    def __get_contacts(self,):
        print("Loading contacts...")
        #TODO: remove the sleep
        time.sleep(3)
        contacts = {}

        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[2]/div/div/div')))
        contact_list_row_count = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div/div[3]/div/div[2]/div/div/div').get_attribute("aria-rowcount")
        #self.driver.execute_script()

        old_window_size = self.driver.get_window_size()

        # Since Whatsapp arranges the divs of the contact list in such a way,
        # that only the divs that can be displayed in the window loads into a list,
        # we resize the height of the window by the value of the number of contacts in the list
        # multiplied by the contact WebElement height in pixels.
        # Thus all divs of the contacts are loaded into the list.
        new_window_height = int(contact_list_row_count) * 72
        self.driver.set_window_size(1920, new_window_height)

        contact_scrollbar = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div/div[3]/div/div[2]')

        name_search_bar = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/div/div[2]/div/div[2]')))

        # add all contacts to dict
        i = 1
        new_contact_added = True
        name_list = []
        while new_contact_added:
            new_contact_added = False
            try:
                # find contact element
                #contact = contact_scrollbar.find_element(by=By.XPATH, value='.//div/div/div/div[%i]/div' % i)
                contact_name = contact_scrollbar.find_element(by=By.XPATH, value='.//div/div/div/div[%i]/div/div/div[2]/div[1]/div[1]/span' % i)
                name = contact_name.text

                # add name to contacts list else it's duplicate (get phone number as description)
                if name not in contacts:
                    contacts[name] = {"id": i}
                name_list.append(name)
                new_contact_added = True
                i += 1
            except Exception as e:
                break
        # undo new window size
        self.driver.set_window_size(old_window_size["width"], old_window_size["height"])
        duplicate_names = [x for x in name_list if name_list.count(x) >= 2]

        while duplicate_names:
            for dupe in duplicate_names:
                i = 1
                name_search_bar.send_keys(dupe)
                time.sleep(3)
                for x in range(1, duplicate_names.count(dupe) + 1):
                    
                    
                    #self.driver.find_element(by=By.CSS_SELECTOR, value="div[style*='z-index: %i;']" % i).click()
                    #name_search_bar.click()
                    for x in range(1, x+1):
                        name_search_bar.send_keys(Keys.ARROW_DOWN * x)
                        time.sleep(1)
                    WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/header/div[2]'))).click()
                    time.sleep(1)
                    if x == 1:
                        contacts.pop(dupe)
                    phone_number = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[3]/span/div/span/div/div/section/div[1]/div[2]/div/span/span'))).text
                    name = "%s (%s)" % (dupe, phone_number)
                    contacts[name] = ""
                    # remove all occurrences of the duplicate name from the list
                    i += 1
                duplicate_names = list(filter(lambda x: x != dupe, duplicate_names))
                break

        return contacts

    def open_chat(self, message_target):
        # find search bar and send contact name
        name_search_bar = WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[1]/div/div/div[2]/div/div[2]')))
        name_search_bar.clear()
        # check if name is a duplicate -> number in brackets is appended to name
        if "(+" in message_target and message_target.split("(+")[-1][-1] == ")":
            # remove first and last char (brackets) from number part e.g. (+49123456)
            message_target = message_target.split("(+")[-1][:-1]
        name_search_bar.send_keys(message_target)
        name_search_bar.send_keys(Keys.ENTER)

        chat_history = self.read_chat()
        input_field = self.driver.find_element(by=By.XPATH, value='/html/body/div[1]/div/div/div[4]/div/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[2]')

        while True:
            try:
                utilities.clear_terminal()

                for message in chat_history:
                    print(message + "\n")

                user_message = input("Send message (ctrl + c to quit):")
                if user_message == "/back":
                    break

                input_field.send_keys(user_message)
                input_field.send_keys(Keys.ENTER)
                chat_history = self.read_chat()
            except KeyboardInterrupt:
                break
        return False

    def read_chat(self,):
        time.sleep(1)
        WebDriverWait(self.driver, TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div[3]/div/div[2]/div[3]')))
        message_list = []
        message_webelement_list = self.driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div/div/div[4]/div/div[3]/div/div[2]/div[3]/div')
        for message_webelement in message_webelement_list:
            try:
                timestamp = message_webelement.find_element(by=By.XPATH, value='.//div/div[1]/div[1]/div[1]').get_attribute("data-pre-plain-text")
                message_text = message_webelement.find_element(by=By.XPATH, value='.//div/div[1]/div[1]/div[1]/div/span[1]/span').text
                
                message = "[{TIMESTAMP}] {MESSAGE}".format(
                        TIMESTAMP = timestamp,
                        MESSAGE = message_text
                    )
                if message not in message_list:
                    message_list.append(message)
            except Exception as e:
                continue
        return message_list
        
# entry point for testing
if __name__ == "__main__":
    # init
    FIREFOX_PATH = os.path.abspath("geckodriver.exe")
    whatsapp_ctrl = WhatsAppController(FIREFOX_PATH, test=True)
    if not whatsapp_ctrl.login_state:
        whatsapp_ctrl.driver.quit()
    
    print("Successfully logged in!")
    print("Contacts: ")
    # print contact dict
    for index, key in enumerate(whatsapp_ctrl.contacts.keys(), start=1):
        print("\t%i %s. " % (index, key))

    while True:
        try:
            message_target = int(input("Who do you want to contact? (Enter row index, exit with ctrl + c): "))
            target_name = list(whatsapp_ctrl.contacts.keys())[message_target-1]
            print("Opening chat with %s " %target_name)
            if not whatsapp_ctrl.open_chat(target_name):
                 print("ERROR: Could not open chat")
        except KeyboardInterrupt:
            break