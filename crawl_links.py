from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import pandas as pd
import csv

import os
import re

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--journal', type=str, help='Journal name')
    parser.add_argument('-s', '--start', type=str,
                        help='Start year', default='2019')
    parser.add_argument('-e', '--end', type=str,
                        help='End year', default='2022')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file name', default='output.csv')

    args = parser.parse_args()
    journal = args.journal
    start_year = args.start
    end_year = args.end
    output = args.output

    # replace the space with '+'
    journal = journal.replace(' ', '+')

    # get directory for current py file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    driver_path = os.path.join(dir_path, 'msedgedriver.exe')
    profile_path = os.path.join(dir_path, '.profile')

    # disable annoying warnings
    options = EdgeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("start-maximized")
    # options.add_argument(f"user-data-dir={profile_path}")

    driver = webdriver.Edge(service=EdgeService(driver_path), options=options)

    # start from the first page, each page has 10 items
    start = 0

    # data for the table
    columns = ['links']
    df = pd.DataFrame(columns=columns)

    # wait for crawlling all the data
    while True:
        # time.sleep(random.uniform(1, 10))
        # each google page has 10 items
        url = f'https://scholar.google.com/scholar?start={start}&q=source:"{journal}"&as_ylo={start_year}&as_yhi={end_year}'
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all the links
        search_results = soup.find_all('div', class_='gs_r gs_or gs_scl')
        if len(search_results) == 0:
            print(f'Finishing...')
            break

        # use the href to open the elsevier pages
        print(f'Start crawling {start} to {start + 10}')
        print(f'\tCrawled {len(df)} items')
        for result in search_results:
            try:
                link = result.select_one(".gs_rt a")["href"]
                data = {'links': link}
                df = pd.concat(
                    [df, pd.DataFrame(data, index=[0])], ignore_index=True
                )

            except Exception as e:
                # print the exception
                print(e)
                continue
        # time.sleep(random.uniform(1, 5))
        start = start + 10

    df.to_csv(output, index=False, quoting=csv.QUOTE_ALL, columns=columns)

if __name__ == '__main__':
    main()
