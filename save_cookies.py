import time

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
import pickle
import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, help='the url of the page')
    args = parser.parse_args()

    url = args.url

     # get directory for current py file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    driver_path = os.path.join(dir_path, 'msedgedriver.exe')
    profile_path = os.path.join(dir_path, '.profile')

    # disable annoying warnings
    options = EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("start-maximized")
    options.add_argument(f"user-data-dir={profile_path}")

    driver = webdriver.Edge(service=EdgeService(driver_path), options=options)
    driver.get(url)

    # wait for the driver to close
    print('Press any key to close the driver...')
    input()
    
    

