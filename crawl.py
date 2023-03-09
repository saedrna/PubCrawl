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


def format_author_name(name: str) -> str:
    """format the author name, e.g., "John Smith" -> "SMITH, John"

    Args:
        name (str): the name of the author

    Returns:
        str: the formatted name
    """
    if not name:
        return ''

    # split the name by space
    names = name.split(' ')
    # the last name is the first element
    last_name = names[-1]
    # the first name is the rest
    first_name = ' '.join(names[0:-1])
    # return the formatted name
    return f'{last_name.upper()}, {first_name}'


def parse_taylor(link: str, driver: webdriver.Edge) -> dict:
    """parse the taylor page

    Args:
        link (str): the url of the page
        driver (webdriver.Edge): the web driver

    Returns:
        dict: the data    
    """
    data = {'title': '',
            'first author': '',
            'corr author': '',
            'inst1': '',
            'inst2': '',
            'inst3': '',
            'inst4': '',
            'inst5': '',
            'kw1': '',
            'kw2': '',
            'kw3': '',
            'kw4': '',
            'kw5': ''
            }

    # probably not from the corresponding journal
    if not link.startswith("https://www.tandfonline.com/doi/"):
        return data

    driver.get(link)

    time.sleep(0.5)

    # get the page sources
    article_soup = BeautifulSoup(driver.page_source, "html.parser")

    # title is under a span tag with class="NLM_article-title hlFld-title"
    title = article_soup.find(
        'span', {'class': 'NLM_article-title hlFld-title'}).text

    # authors is under a span tag with class="NLM_contrib-group"
    authors = article_soup.find('span', {'class': 'NLM_contrib-group'})

    # first author is the first one with contribDegrees
    first_author = authors.find('a', {'class': 'author'}).text
    first_author = format_author_name(first_author)

    # corresponding author is under a contribDegrees corresponding
    corresponding_author = authors.find(
        'span', {'class': 'contribDegrees corresponding'})
    if corresponding_author is not None:
        corresponding_author = corresponding_author.find(
            'a', {'class': 'author'}).text
    else:
        corresponding_author = ''
    corresponding_author = format_author_name(corresponding_author)

    # get the institutions, they are also under authors
    institutions = []
    for author in authors.find_all('span', {'class': 'contribDegrees'}):
        entry = author.find('div', {'class': 'entryAuthor'})
        entry = entry.find('span', {'class': 'overlay'})
        # get the institution string, the text of the first child
        institution_str = entry.contents[0]

        # split the string with ';'
        institution_list = institution_str.split(';')
    
        for institution in institution_list:
            # trim the first two letters if the starts with prefix 'a ', 'b ', 'c ', 'd ' etc.
            if institution.startswith('a '):
                institution = institution[2:]
            elif institution.startswith('b '):
                institution = institution[2:]
            elif institution.startswith('c '):
                institution = institution[2:]
            elif institution.startswith('d '):
                institution = institution[2:]
            elif institution.startswith('e '):
                institution = institution[2:]

            institutions.append(institution.strip())

    # make the institutions unique, do not change the order
    unique_institutions = list(set(institutions))
    unique_institutions.sort(key=institutions.index)
    institutions = unique_institutions

    # keep at most five institutions, if smaller, fill with empty string
    if len(institutions) > 5:
        institutions = institutions[:5]
    else:
        institutions += [''] * (5 - len(institutions))

    # get the keywords
    kws = []
    keywords = article_soup.find_all('a', {'class': 'kwd-btn keyword-click'})
    for keyword in keywords:
        kws.append(keyword.text)

    # keep at most five keywords, if smaller, fill with empty string
    if len(kws) > 5:
        kws = kws[:5]
    else:
        kws += [''] * (5 - len(kws))

    # fill the data
    data['title'] = title
    data['first author'] = first_author
    data['corr author'] = corresponding_author
    data['inst1'] = institutions[0]
    data['inst2'] = institutions[1]
    data['inst3'] = institutions[2]
    data['inst4'] = institutions[3]
    data['inst5'] = institutions[4]
    data['kw1'] = kws[0]
    data['kw2'] = kws[1]
    data['kw3'] = kws[2]
    data['kw4'] = kws[3]
    data['kw5'] = kws[4]

    return data


def parse_elsevier(link: str, driver: webdriver.Edge) -> dict:
    """
    parse the elsevier page

    Args:
        link (str): the url of the page
        driver (webdriver.Edge): the web driver

    Returns:
        dict: the data    
    """
    # initialize the data
    data = {'title': '',
            'first author': '',
            'corr author': '',
            'inst1': '',
            'inst2': '',
            'inst3': '',
            'inst4': '',
            'inst5': '',
            'kw1': '',
            'kw2': '',
            'kw3': '',
            'kw4': '',
            'kw5': ''
            }

    # probably not from the corresponding journal
    if not link.startswith("https://www.sciencedirect.com/science/article/"):
        return data

    driver.get(link)

    time.sleep(0.5)

    # find the element with id "show-more-btn" and click on it to expand the information
    button = driver.find_element("id", "show-more-btn")
    button.click()

    # get the page sources
    article_soup = BeautifulSoup(driver.page_source, "html.parser")

    # get the informations
    title = article_soup.find('span', {'class': 'title-text'}).text

    affiliations = []
    for dl in article_soup.find_all("dl", class_="affiliation"):
        # affl in dd
        for dd in dl.find_all("dd"):
            affiliations.append(dd.text)
    if len(affiliations) > 5:
        affiliations = affiliations[:5]
    else:
        affiliations += [''] * (5 - len(affiliations))

    # Get the author name and corr name
    author_given_name = article_soup.find('span', {'class': 'given-name'}).text
    author_sur_name = article_soup.find('span', {'class': 'text surname'}).text
    first_author = format_author_name(
        author_given_name + " " + author_sur_name)

    # Corr name is under a person symbol
    svg = article_soup.find('svg', {'aria-label': 'Person'})
    if svg is not None:
        react_element = svg.find_parent('span', {'class': 'button-link-text'})
        give_name = react_element.find('span', {'class': 'given-name'}).text
        surname = react_element.find('span', {'class': 'text surname'}).text
        corresponding_author = format_author_name(give_name + " " + surname)
    else:
        corresponding_author = ""

    # Get the keywords
    kws = []
    keywords = article_soup.find_all('div', {'class': 'keyword'})
    if keywords is not None:
        for keyword in keywords:
            keyword = keyword.find('span').text
            kws.append(keyword)
    if len(kws) > 5:
        kws = kws[:5]
    else:
        kws += [''] * (5 - len(kws))

    # fill the data
    data['title'] = title
    data['first author'] = first_author
    data['corr author'] = corresponding_author
    data['inst1'] = affiliations[0]
    data['inst2'] = affiliations[1]
    data['inst3'] = affiliations[2]
    data['inst4'] = affiliations[3]
    data['inst5'] = affiliations[4]
    data['kw1'] = kws[0]
    data['kw2'] = kws[1]
    data['kw3'] = kws[2]
    data['kw4'] = kws[3]
    data['kw5'] = kws[4]
    return data


def parse_springer(url: str, driver: webdriver.Edge) -> dict:
    # initialize the data
    data = {'title': '',
            'first author': '',
            'corr author': '',
            'inst1': '',
            'inst2': '',
            'inst3': '',
            'inst4': '',
            'inst5': '',
            'kw1': '',
            'kw2': '',
            'kw3': '',
            'kw4': '',
            'kw5': ''
            }

    # probably not from the corresponding journal
    if not url.startswith("https://link.springer.com/article/"):
        return data

    driver.get(url)
    time.sleep(0.5)
    article_soup = BeautifulSoup(driver.page_source, "html.parser")
    title = article_soup.find('h1', {'class': 'c-article-title'}).text
    affiliations = []
    for affiliation in article_soup.find_all("p", class_="c-article-author-affiliation__address"):
        affiliations.append(affiliation.text)
    if len(affiliations) > 5:
            affiliations = affiliations[:5]
    else:
        affiliations += [''] * (5 - len(affiliations))

    # Get the author name and corr name
    first_author_text= article_soup.find('a', {'data-test': 'author-name'}).text
    

    first_author = format_author_name(first_author_text)
    
    corresp_c1 = article_soup.find('a', {'id': 'corresp-c1'})
    if corresp_c1 is not None:
        corresponding_author_text = corresp_c1.text
        corresponding_author = format_author_name(corresponding_author_text)
    else:
        corresponding_author = "None"
    keywords = []
    for li_element in article_soup.find_all("li", class_="c-article-subject-list__subject"):
        keyword=li_element.find('span')
        keywords.append(keyword.text)
    if len(keywords) > 5:
        keywords = keywords[:5]
    else:
        keywords += [''] * (5 - len(keywords))
    # fill the data
    data['title'] = title
    data['first author'] = first_author
    data['corr author'] = corresponding_author
    data['inst1'] = affiliations[0]
    data['inst2'] = affiliations[1]
    data['inst3'] = affiliations[2]
    data['inst4'] = affiliations[3]
    data['inst5'] = affiliations[4]
    data['kw1'] = keywords[0]
    data['kw2'] = keywords[1]
    data['kw3'] = keywords[2]
    data['kw4'] = keywords[3]
    data['kw5'] = keywords[4]
    return data

    pass


def parse_wiley(link: str, driver: webdriver.Edge) -> dict:
    """
    parse the elsevier page

    Args:
        link (str): the url of the page
        driver (webdriver.Edge): the web driver

    Returns:
        dict: the data    
    """
    # TODO: Wiley 有反爬虫机制，还没测试成功

    # initialize the data
    data = {'title': '',
            'first author': '',
            'corr author': '',
            'inst1': '',
            'inst2': '',
            'inst3': '',
            'inst4': '',
            'inst5': '',
            'kw1': '',
            'kw2': '',
            'kw3': '',
            'kw4': '',
            'kw5': ''
            }

    # probably not from the corresponding journal
    if "wiley.com" not in link:
        return data

    driver.get(link)

    time.sleep(0.5)

    # get the page sources
    article_soup = BeautifulSoup(driver.page_source, "html.parser")

    # get the title
    title = article_soup.find('h1', {'class': 'citation__title'}).text

    # authors and inistitutions
    authors = article_soup.find('div', {'class': 'desktop-authors'})
    first_author = ''
    corresponding_author = ''
    
    # processing affiliations from author info
    affiliations = []
    authors_infos = authors.find_all('div', {'class': 'author-info'})
    for i, author_info in enumerate(authors_infos) :
        author_type = author_info.find('p', {'class': 'author-type'})
        author_name = author_info.find('p', {'class': 'author-name'}).text
        author_name = format_author_name(author_name)
        if author_type is not None and author_type.text.lower() == 'corresponding author':
            corresponding_author = author_name
        if i == 0:
            first_author = author_name
        
        for content in author_info.contents:
            if content.name != 'p':
                continue
            if 'class' in content.attrs:
                continue
            content_text = content.text
            if 'Correspondence to:' in content_text:
                break
            if 'Contribution' in content_text:
                break
            affiliations.append(content_text)
    # unique and sort affiliations
    unique_affiliations = list(set(affiliations))
    unique_affiliations.sort(key=affiliations.index)
    affiliations = unique_affiliations

    if len(affiliations) > 5:
        affiliations = affiliations[:5]
    else:
        affiliations += [''] * (5 - len(affiliations))
   

    # fill the data
    data['title'] = title
    data['first author'] = first_author
    data['corr author'] = corresponding_author
    data['inst1'] = affiliations[0]
    data['inst2'] = affiliations[1]
    data['inst3'] = affiliations[2]
    data['inst4'] = affiliations[3]
    data['inst5'] = affiliations[4]
    data['kw1'] = kws[0]
    data['kw2'] = kws[1]
    data['kw3'] = kws[2]
    data['kw4'] = kws[3]
    data['kw5'] = kws[4]
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--journal', type=str, help='Journal name')
    parser.add_argument('-s', '--start', type=str,
                        help='Start year', default='2019')
    parser.add_argument('-e', '--end', type=str,
                        help='End year', default='2022')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file name', default='output.csv')
    parser.add_argument('-p', '--publisher', type=str,
                        help='Publisher support in elsevier, taylor, springer, wiley', default='taylor')

    args = parser.parse_args()
    journal = args.journal
    start_year = args.start
    end_year = args.end
    output = args.output
    publisher = args.publisher

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
    options.add_argument(f"user-data-dir={profile_path}")

    driver = webdriver.Edge(service=EdgeService(driver_path), options=options)

    # start from the first page, each page has 10 items
    start = 0

    # data for the table
    columns = ['title', 'first author', 'corr author', 'inst1', 'inst2',
               'inst3', 'inst4', 'inst5', 'kw1', 'kw2', 'kw3', 'kw4', 'kw5']
    df = pd.DataFrame(columns=columns)

    # wait for crawlling all the data
    while True:
        time.sleep(random.uniform(1, 5))
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
                time.sleep(random.uniform(1, 5))

                link = result.select_one(".gs_rt a")["href"]

                if publisher == 'elsevier':
                    data = parse_elsevier(link, driver)
                elif publisher == 'springer':
                    data = parse_springer(link, driver)
                elif publisher == 'wiley':
                    data = parse_wiley(link, driver)
                else:
                    data = parse_taylor(link, driver)

                if data['title'] == '':
                    continue

                df = pd.concat(
                    [df, pd.DataFrame(data, index=[0])], ignore_index=True
                )
            except Exception as e:
                # print the exception
                print(e)
                continue
        start = start + 10
        break

    df.to_csv(output, index=False, quoting=csv.QUOTE_ALL, columns=columns)

if __name__ == '__main__':
    main()
