import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

TIMEOUT = 10


def clear_terminal():
    if os.name == "posix":
        # Unix/Linux/MacOS/BSD/etc
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        # DOS/Windows
        os.system('CLS')
    else:
        # Fallback for other operating systems.
        print('\n' * 100)

def wait_for_webelement_to_load(driver, type, path):
    loaded = False
    try:
        WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((type, path)))
        loaded = True
    except TimeoutException:
        print("ERROR: Failed to load type %s at path %s" % (type, path))
    return loaded

def get_int_input(min_value=0, max_value=0):
    input_number = 0
    while True:
        try:
            input_number = int(input())
            if min_value <= input_number <= max_value:
                break
            else:
                print("Not a valid number, please enter again (cancel with ctrl + c).")
        except ValueError:
            print("Please enter an integer (cancel with ctrl + c)")
        except KeyboardInterrupt:
            input_number = -1
            # reraise to get back to main function
            raise KeyboardInterrupt()
    return input_number