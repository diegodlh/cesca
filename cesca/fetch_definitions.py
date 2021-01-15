"""
Fetches word definitions in CesCa corpus.
"""

from splinter import Browser
import re
import csv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--start', type=int)
args = parser.parse_args()

cesca_url = 'http://clic.ub.edu/mbertran/ancora/cesca/index.php'

browser = Browser('chrome')
browser.visit(cesca_url)
browser.find_option_by_text('definició').click()
browser.find_by_value('Cerca').click()
if args.start:
    browser.visit(browser.url + '?from=' + str(args.start))


def get_lemmatized(analyzed_text):
    lemmas = []
    for token in analyzed_text.find_by_css('span'):
        title = token['title']
        match = re.search('lem="(.*?)"', title)
        if match:
            lemma = match.group(1)
        else:
            continue
        lemmas.append(lemma)
    return ' '.join(lemmas)


def retrieve_data(match):
    dbid = match.find_by_css('li[class="match_attribute_dbid"]').html
    dbid = re.match('^Identificador: (.*)$', dbid).group(1)
    title = match.find_by_css('li[class="match_attribute_titol"]').html
    title = re.match('^Títol: (.*)$', title).group(1)
    age = match.find_by_css('li[class="match_attribute_age"]').html
    age = re.match('^Edat: (.*)$', age).group(1)
    text = match.find_by_css('li[class="text-text"]').html
    text = re.match('^Text: (.*)$', text, re.DOTALL).group(1)
    analyzed_text = match.find_by_css('li[class="text-analisi-sentence"]')
    if analyzed_text:
        lemmatized = get_lemmatized(analyzed_text)
    else:
        lemmatized = ''
    data = {'dbid': dbid,
            'title': title,
            'age': age,
            'text': text,
            'lemmatized': lemmatized}
    return data


with open('definitions.csv', 'a') as csvfile:
    fieldnames = ['dbid', 'title', 'age', 'text', 'lemmatized']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    while True:
        for match in browser.find_by_css('tr[class="search-result-match"]'):
            writer.writerow(retrieve_data(match))

        csvfile.flush()
        next_btn = browser.find_by_name('next')
        if next_btn.has_class('disabled'):
            break
        else:
            next_btn.click()
