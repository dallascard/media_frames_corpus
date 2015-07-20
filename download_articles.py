import os
import re
import sys
import json
import time
import glob
import codecs
import random
import datetime
import numpy as np
from optparse import OptionParser
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException

import sources
import bulk_downloads
import parse_LN_to_JSON


def main():
    usage = "%prog <issue>"
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='download_dir', default="./downloads",
                  help='Download directory; default=%default')
    parser.add_option('-b', dest='bulk_download_dir', default="./temp",
                  help='Temporary directory for bulk downloads; default=%default')
    parser.add_option('-u', dest='url_base', default="http://www.lexisnexis.com",
                  help='Base URL for accessing Lexis-Nexis; default=%default')

    (options, args) = parser.parse_args()

    if len(args) < 1:
        sys.exit("Please provide an issue (immigration, smoking, or samesex)")
    else:
        subject = args[0]
    
    skip_parsing = False
    if len(args) > 1:
        if args[1] == 'skip':
            skip_parsing = True


    if subject == 'immigration':
        prefix = 'IMM'
    elif subject == 'smoking':
        prefix = 'TOB'
    elif subject == 'samesex':
        prefix = 'SSM'
    else:
        sys.exit("Please specify 'immigration', 'smoking', or 'samesex'")

    url_base = options.url_base

    # create download directory
    if options.download_dir == './downloads':
        download_directory = os.path.join(os.getcwd(), 'downloads', subject)
    else:
        download_directory = os.path.join(options.download_dir, subject)
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    if options.bulk_download_dir == './temp':
        bulk_download_dir = os.path.join(os.getcwd(), 'temp', subject)
    else:
        bulk_download_dir = os.path.join(options.bulk_download_dir, subject)
    if not os.path.exists(bulk_download_dir):
        os.makedirs(bulk_download_dir)        

    index_dir = os.path.join(os.getcwd(), 'indices')
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    
    annotation_filename = os.path.join(os.getcwd(), 'annotations', subject + '.json')
    error_logname = 'error_log.txt'

    with codecs.open(error_logname, 'w') as output_file:
        output_file.write('Starting\n')

    print "Reading annotations"
    with codecs.open(annotation_filename, 'r') as input_file:
        annotations = json.load(input_file, encoding='utf-8')

    index_filename = os.path.join(index_dir, subject + '_index.json')
    bulk_index_filename = os.path.join(index_dir, subject + '_bulk_index.json')

    # Start by downloading batches of article which will cover most of what we want
    n_missing = 1
    while n_missing > 0:
        n_missing = bulk_download(url_base, subject, bulk_download_dir, bulk_index_filename, error_logname)
    
    # search through the bulk downloads for our articles
    if not skip_parsing:
        look_for_relevant_articles(bulk_download_dir, download_directory, index_filename, annotations, prefix)

    # then manually download all missing articles individually
    first_article = 0
    n_missing = check_download(annotations, download_directory, index_filename)
    if n_missing > 0:
        print n_missing, "files needed"
        download_articles(url_base, download_directory, annotations, index_filename, first_article, error_logname)
        time.sleep(2)
        n_missing = check_download(annotations, download_directory, index_filename)
    if n_missing > 0:
        print n_missing, "files STILL needed"
    else:
        print "All files downloaded"



def bulk_download(url_base, subject, download_dir, bulk_index_filename, log_filename):
    first_page = True

    search_strings = bulk_downloads.get_search_strings(url_base, download_dir, subject)

    if os.path.exists(bulk_index_filename):        
        with codecs.open(bulk_index_filename, 'r') as input_file:
            bulk_index = json.load(input_file, encoding='utf-8')
    else:
        bulk_index = {}

    n_missing = check_bulk_downloads(download_dir, bulk_index, search_strings)

    if n_missing > 0:
        print "Doing download of articles in batches"
        print len(search_strings), "total batches;", n_missing, "to be downloaded."

        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", download_dir)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")
        driver = webdriver.Firefox(firefox_profile=fp)

        count = 0
        for search in search_strings:
            if search not in bulk_index:
                print count, datetime.datetime.now(), '\n', search
                process_query(search, driver, first_page, log_filename, bulk_index_filename, download_dir, search, count, bulk_index, modify_filenames=False)
                first_page = False
            else:
                full_filename = os.path.join(download_dir, bulk_index[search])
                if not os.path.exists(full_filename):
                    print count, datetime.datetime.now(), '\n', search
                    process_query(search, driver, first_page, log_filename, bulk_index_filename, download_dir, search, count, bulk_index, modify_filenames=False)
                    first_page = False
            count += 1

        driver.close()

        n_missing = check_bulk_downloads(download_dir, bulk_index, search_strings)
        print n_missing, "files still missing from bulk download."

    return n_missing


def look_for_relevant_articles(bulk_download_dir, main_download_dir, index_filename, annotations, prefix):
    article_directory = make_article_directory(annotations)

    with codecs.open(index_filename, 'r', encoding='utf-8') as input_file:
        input_text = input_file.read()
        filename_index = json.loads(input_text, encoding='utf-8')

    files = glob.glob(os.path.join(bulk_download_dir, '*.TXT'))
    for f in files:
        print "Parsing", f
        parse_LN_to_JSON.search_LN_file_for_articles(f, filename_index, main_download_dir, article_directory, prefix=prefix)


def download_articles(url_base, download_dir, annotations, index_filename, first_article, log_filename):

    first_page = True
    title_sublist = get_title_sublist()

    with codecs.open(index_filename, 'r', encoding='utf-8') as input_file:
        input_text = input_file.read()
        filename_index = json.loads(input_text, encoding='utf-8')

    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", download_dir)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")
    driver = webdriver.Firefox(firefox_profile=fp)

    keys = annotations.keys()
    keys.sort()
    for iteration, k in enumerate(keys[first_article:]):

        if k in filename_index:
            target_filename = os.path.join(download_dir, filename_index[k])
            if os.path.exists(target_filename):
                continue

        print iteration+first_article, k, datetime.datetime.now()

        # construct a url for this article
        # first replace problematic punctuation with spaces in title and byline
        invalid_chars = '[\(\)<>:;?!]'
        title = re.sub(invalid_chars, ' ', annotations[k]['title']).lower()
        title = re.sub(' o ', ' * ', title)
        if k in title_sublist:
            title = title_sublist[k][1]            
        
        byline = re.sub(invalid_chars, ' ', annotations[k]['byline']).lower()
        if re.search('[a-z]', byline) is None:
            byline = ''
        if '#name' in byline:
            byline = ''
        byline = re.sub(" and ", " 'and' ", byline)
        if ' o ' in byline:
            parts = byline.split(' o ')
            byline = parts[0]
        if ' & ' in byline:
            parts = byline.split(' & ')
            byline = parts[0]
        if '  ' in byline:
            parts = byline.split('  ')
            byline = parts[0]


        # then extract the longest subsequence of the title that avoids certain problems (like numbers)
        # first pad with spaces on either side
        title = ' ' + title + ' '
        # find all matching substrings
        title_substrings_list = re.findall('\s([a-zA-Z\s"`.,]+)\s', title)
        # take the longest
        if len(title_substrings_list) > 0:
            lengths = [len(i) for i in title_substrings_list]
            substring_index = np.argmax(lengths)
            title_substring = title_substrings_list[substring_index]
            # put "not" in quotes because it has a meaning in urls            
            title_substring = ' ' + title_substring + ' '
            print title_substring
            title_substring = re.sub(" not ", " 'not' ", title_substring)
            title_substring = re.sub(" and ", " 'and' ", title_substring)
            title_substring = re.sub(" or ", " 'or' ", title_substring)
            title_substring = re.sub('"', '\'', title_substring)
            title_substring = title_substring.lstrip()
            title_substring = title_substring.rstrip()
        else:
            title_substring = ''

        if title_substring == 'the':
            title_substring = ''
        if title_substring == 'where':
            title_substring = ''
        if title_substring == 'to':
            title_substring = ''
        if title_substring == 'do':
            title_substring = ''


        # construct the url with the information that is available
        url = url_base + '/hottopics/lnacademic/?verb=sr&csi=' \
            + str(annotations[k]['csi']) + '&sr='
        if len(byline) > 0:
            url += 'BYLINE(' + byline + ')+AND+'
        if len(annotations[k]['length']) > 0:
            url += 'LENGTH+IS+' + annotations[k]['length'] + '+AND+'
        if len(title_substring) > 0:
            url += 'HLEAD(' + title_substring + ')+AND+'
        url += 'DATE+IS+' + annotations[k]['date']
        print url

        process_query(url, driver, first_page, log_filename, index_filename, download_dir, k, iteration+first_article, filename_index)
        first_page = False

    driver.close()


def process_query(url, driver, first_page, log_filename, index_filename, download_dir, k, count, filename_index, modify_filenames=True):
    # load the webpage
    log_message(log_filename, k, 'loading ' + url)
    got_url = False
    for j in range(10):        
        try:
            log_message(log_filename, k, 'trying url')
            driver.get(url)
            got_url = True
            break
        except WebDriverException, e:
            log_message(log_filename, k, str(e))
            time.sleep(2)

    if not got_url:
        log_message(log_filename, k, '** FAILED ** on getting url')
        print("Failed on " + str(count) + ', ' + k)
        return

    # look for the main frame (which contains the download button)
    frame_ready = False
    for j in range(10):
        try:
            log_message(log_filename, k, 'finding mainFrame')
            driver.find_element_by_name('mainFrame')
            frame_ready = True
            break
        except WebDriverException, e:
            log_message(log_filename, k, str(e))
            time.sleep(2)

    if not frame_ready:
        log_message(log_filename, k, '** FAILED ** on finding mainFrame')
        print("Failed on " + str(count) + ', ' + k)
        return

    log_message(log_filename, k, 'switching to mainFrame')
    driver.switch_to.frame('mainFrame')

    # look for the download button and click it
    script_ready = False
    for j in range(10):
        try:
            log_message(log_filename, k, 'attempting to open delivery window')
            driver.execute_script("javascript:openDeliveryWindow(this, 'delivery_DnldRender');")
            script_ready = True
            break
        except WebDriverException, e:
            log_message(log_filename, k, str(e))
            time.sleep(2)

    if not script_ready:
        log_message(log_filename, k, '** FAILED ** on opening delivery window')
        print("Failed on " + str(count) + ', ' + k)
        return


    # switch to the download popup window
    log_message(log_filename, k, 'switching to delivery window')
    driver.switch_to.window(driver.window_handles[1])

    # for the first article, choose text format (will remain as default for the rest)
    count = 0
    if first_page:
        page_loaded = False
        while not page_loaded:
            try:
                log_message(log_filename, k, 'attempting to find delFmt')
                select = Select(driver.find_element_by_name("delFmt"))
                select.select_by_value("QDS_EF_GENERICTYPE")
                page_loaded = True
            except WebDriverException, e:
                log_message(log_filename, k, str(e))
                time.sleep(2)
            count += 1
            if count > 10:
                log_message(log_filename, k, '** FAILED ** on finding delFmt')
                sys.exit("Failed on " + k)

    # look for the download button in the popup window and click it
    script_ready = False
    for j in range(10):
        try:
            log_message(log_filename, k, 'attempting to find execute delivery_DnldForm')
            driver.execute_script("javascript:onAction('delivery_DnldForm');")
            script_ready = True
            break
        except WebDriverException, e:
            log_message(log_filename, k, str(e))
            time.sleep(2)

    if not script_ready:
        log_message(log_filename, k, '** FAILED ** on executing delivery_DnldForm')
        return


    # Look for the link to the text file and click it
    link_found = False
    for j in range(10):
        try:
            log_message(log_filename, k, 'attempting to find download link')
            elements = driver.find_elements_by_css_selector("a[href*='Download']")
            if len(elements) > 0:
                first_link = elements[0]
                download_name = first_link.text
                full_download_name = os.path.join(download_dir, download_name)

                # if we haven't seen this file before, check for name conflicts
                if k not in filename_index:
                    # change any old conflicting names if necessary
                    if os.path.exists(full_download_name) and download_name in filename_index.values():
                        change_old_filename(download_dir, filename_index, download_name)
                # otherwise, assume we know what the name SHOULD be, and change it below, if necessary

                first_link.click()
                link_found = True
                break
            else:
                time.sleep(2)
        except WebDriverException, e:
            log_message(log_filename, k, str(e))
            print e


    if not link_found:
        log_message(log_filename, k, '** FAILED ** on finding download link')
        return

    # if we haven't seen this file before, add it to the index
    if k not in filename_index:
        filename_index[k] = download_name 

    if unicode(filename_index[k]) != unicode(download_name):
        log_message(log_filename, k, '* Changing name of downloaded file from ' + unicode(download_name) + ' to ' + filename_index[k])
        time.sleep(2)
        if os.path.exists(os.path.join(download_dir, download_name)):
            print "Renaming", unicode(download_name), "to", filename_index[k]            
            os.rename(os.path.join(download_dir, download_name), os.path.join(download_dir, unicode(filename_index[k])))

    # close the pop-up window
    log_message(log_filename, k, 'closing popup')
    driver.close()

    # write an updated index to downloaded filenames
    with codecs.open(index_filename, 'w', encoding='utf-8') as output_file:
        json.dump(filename_index, output_file, indent=2, encoding='utf-8')

    log_message(log_filename, k, 'Finished with ' + filename_index[k])

    # Switch back to the main window
    log_message(log_filename, k, 'switching to main window')
    driver.switch_to.window(driver.window_handles[0])


def change_old_filename(download_dir, filename_index, old_name):
    
    keys = [k for (k, v) in filename_index.items() if v == old_name]
    assert len(keys) == 1
    k = keys[0]
    
    new_name = os.path.splitext(old_name)[0] + '_' + str(random.randint(0,1000)) + '.TXT'
    while new_name in filename_index.values():
        new_name = os.path.splitext(old_name)[0] + '_' + str(random.randint(0,1000)) + '.TXT'

    full_old_name = os.path.join(download_dir, old_name)
    full_new_name = os.path.join(download_dir, new_name)

    print "Changing name from", old_name, "to", new_name
    if os.path.exists(full_old_name):
        os.rename(full_old_name, full_new_name)

    filename_index[k] = new_name
    return new_name


def check_download(annotations, download_directory, index_filename):
    keys = annotations.keys()
    keys.sort()

    n_missing = 0

    with codecs.open(index_filename, 'r') as input_file:
        input_text = input_file.read()
        filename_index = json.loads(input_text)

    for iteration, k in enumerate(keys):
        if k in filename_index:
            target_filename = os.path.join(download_directory, filename_index[k])
            if not os.path.exists(target_filename):
                n_missing += 1
        else:
            n_missing += 1

    return n_missing


def check_bulk_downloads(download_dir, filename_index, search_strings):
    keys = filename_index.keys()
    count = 0
    for k in search_strings:
        if k in filename_index:
            full_filename = os.path.join(download_dir, filename_index[k])
            if not os.path.exists(full_filename):
                count += 1
        else: 
            count += 1
    return count


def log_message(log_filename, article, message):
    lines = message.split('\n')
    with codecs.open(log_filename, 'a', encoding='utf-8') as output_file:
        output_file.write(str(datetime.datetime.now()) + ',' + article + ': ' + lines[0] + '\n')


def get_title_sublist():
    sub_list = {}
    sub_list['Immigration1.0-32282'] = ('community news roundup', 'in your community')
    sub_list['Immigration1.0-31889'] = ('community news roundup', 'in your community')
    return sub_list


def make_article_directory(metadata):
    keys = metadata.keys()

    articles = {}

    for k in keys:
        if k not in metadata:
            print k, "not found in metadata"
        else:
            csi = metadata[k]['csi']
            year = metadata[k]['year']
            length = metadata[k]['length']
            title = metadata[k]['title']     
            in_bulk = metadata[k]['in_bulk']

            if k == 'Immigration1.0-19780':
                print k, in_bulk
                if in_bulk:
                    print title

            if len(title) > 0 and in_bulk:
                if csi not in articles:
                    articles[csi] = {}

                if year not in articles[csi]:
                    articles[csi][year] = {}

                if length not in articles[csi][year]:
                    articles[csi][year][length] = {}            

                articles[csi][year][length][title] = k

    return articles

if __name__ == '__main__':
    main()

