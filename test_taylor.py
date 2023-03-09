from crawl import parse_taylor
from selenium import webdriver
import os
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService


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

link = "https://www.tandfonline.com/doi/abs/10.1080/13658816.2023.2183959"

data = parse_taylor(link, driver)
