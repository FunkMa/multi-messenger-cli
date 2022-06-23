from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import sys
import time

import whatsapp_controller
import telegram_controller
import messenger_controller
import utilities

messenger_services = ["Whatsapp", "Telegram", "Messenger"]
if os.name == "posix":
    geckodriver_exe = "geckodriver_linux"
elif os.name in ("nt", "dos", "ce"):
    geckodriver_exe = "geckodriver_win.exe"
else:
    print("ERROR: No supported driver for Firefox found")
PATH = os.path.abspath(geckodriver_exe)

def add_messenger_service(services={}):
    for index, service in enumerate(messenger_services, start=1):
        print("\t%i. %s" % (index, service))
    print("Which messenger would you like to add?")
    i = utilities.get_int_input(min_value=1, max_value=len(messenger_services)) - 1
    if i != -1:
        if messenger_services[i] == "Whatsapp":
            services["Whatsapp"] = whatsapp_controller.WhatsAppController(PATH)
        elif messenger_services[i] == "Telegram":
            services["Telegram"] = telegram_controller.TelegramController(PATH)
        elif messenger_services[i] == "Messenger":
            services["Messenger"] = messenger_controller.MessengerController(PATH)
    else:
        print("No messenger service added.")
    return services

def message_contact(services_dict):
    try:
        service_list = list(services_dict.keys())
        service_key = 0
        # select messenger service to prevent printing of 100+ contacts
        if len(service_list) != 1:
            for index, service in enumerate(service_list, start=1):
                print("\t%i. %s" % (index, service))
            print("Which service do you want to use? (Enter row index, cancel with ctrl + c): ")
            service_key = utilities.get_int_input(min_value=1, max_value=len(service_list)) - 1
        contact_list = list(services_dict[service_list[service_key]].contacts.keys())
        for index,contact in enumerate(contact_list, start=1):
            print("\t%i. %s" % (index, contact))
        print("Who do you want to contact? (Enter row index, cancel with ctrl + c): ")
        contact_index = utilities.get_int_input(min_value=1, max_value=len(services_dict[service_list[service_key]].contacts)) - 1
        services_dict[service_list[service_key]].open_chat(contact_list[contact_index])
    except KeyboardInterrupt:
        return

if __name__ == "__main__":

    # TODO: add other browser support
    #driver = webdriver.Firefox(executable_path=PATH)

    # get dictionary containing one messenger service
    services_dict = add_messenger_service()
    try:
        while True:
            print("""
        + \t to add messenger
        m \t to message contacts
        - \t to log out messenger
        ctrl + c to quit
            """)
            nav_char = input().lower()
            if nav_char == "+":
                contacts_dict = add_messenger_service(services_dict)
            elif nav_char == "m":
                message_contact(services_dict)
            elif nav_char == "-":
                print("TODO: logout")
    except KeyboardInterrupt:
        sys.exit()
