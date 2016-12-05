import os
import re
import sys
import json
import time
import codecs
import logging
import calendar
import datetime
from optparse import OptionParser

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException

logging.basicConfig(filename='get_news_articles.log', level=logging.INFO)

def main():
    usage = "%prog config_file.json"
    parser = OptionParser(usage=usage)
    parser.add_option('-c', dest='chrome_driver', default="chrome/chromedriver",
                      help='Location of chrome driver; default=%default')
    parser.add_option('-u', dest='url_base', default="http://www.lexisnexis.com",
                      help='Base URL for accessing Lexis-Nexis; default=%default')

    (options, args) = parser.parse_args()

    if len(args) < 1:
        sys.exit("Please provide a config file (e.g. immigration_config.json")
    config_file = args[0]
    with codecs.open(config_file, 'r') as input_file:
        config = json.load(input_file)
    name = config['name']

    keywords = []
    search_terms = config['search terms']
    for keyword_list, threshold in search_terms:
        keywords_and_list = []
        for keyword in keyword_list:
            keyword = re.sub(' ', '+', keyword)
            keyword = re.sub('&', '%26', keyword)
            keywords_and_list.append('(' + keyword + '+%23' + str(threshold) + 'PLUS%23)')
        keywords.append('(' + '+AND+'.join(keywords_and_list) + ')')
    keywords = '+OR+'.join(keywords)
    print "keywords =", keywords

    newspapers = config['newspaper csis']

    sd = config['first date']
    ed = config['last date']

    start_date = datetime.date(int(sd['year']), int(sd['month']), int(sd['day']))
    final_end_date = datetime.date(int(ed['year']), int(ed['month']), int(ed['day']))

    url_base = options.url_base
    chrome_driver = options.chrome_driver

    records_dir = 'records'
    if not os.path.exists(records_dir):
        os.makedirs(records_dir)
    records_filename = os.path.join(records_dir, name + '.log')

    download_dir = os.path.join('downloads', name)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    output_filelist = []

    download(url_base, keywords, newspapers, start_date, final_end_date, download_dir, chrome_driver, records_filename, output_filelist)

    for f in output_filelist:
        if not os.path.exists(f):
            print f, "missing!"


def make_date_string(date):
    return '%s+%i+%i' % (calendar.month_name[date.month], date.day, date.year)


def download(url_base, keywords, newspapers, orig_start_date, final_end_date, download_dir, chrome_driver, record_filename, output_filelist):
    first_page = True

    #if os.path.exists(record_filename):
    #    with open(record_filename, 'r') as input_file:
    #        records = input_file.readlines()
    #else:
    #    records = []

    records = []
    with open(record_filename, 'a') as output_file:
        output_file.write("Records:\n")

    print "Starting chrome"
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_dir}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=chrome_driver, chrome_options=chromeOptions)
    driver.get('http://google.com')

    total_articles_found = 0

    for newspaper in newspapers:
        print 'Searching newspaper %d' % newspaper
        start_date = orig_start_date
        end_date = final_end_date
        diff = (end_date-start_date).days
        days_left = diff
        date_span = diff

        print "days left =", days_left

        while days_left > 0:
            search_end_date = end_date + datetime.timedelta(1)
            print 'Searching %s to %s' % (start_date, search_end_date)
            logging.info('Searching %s to %s' % (start_date, search_end_date))

            search_string = '%s/hottopics/lnacademic/?verb=sr&csi=%d&sr=SUBJECT(%s)+AND+GEOGRAPHIC(UNITED+STATES)+AND+DATE+AFTER+%s+AND+DATE+BEFORE+%s' % (url_base, newspaper, keywords, make_date_string(start_date), make_date_string(search_end_date))
            destination_filename = str(newspaper) + "_" + str(start_date) + "_to_" + str(end_date) + ".txt"
            nDocuments = process_query(search_string, driver, first_page, download_dir, record_filename, destination_filename, output_filelist)

            if nDocuments < -1:
                print "Problem loading page; refreshing browser"
                driver.refresh()

            elif nDocuments <= 0:
                if days_left > 0:
                    print 'No documents found in range %s to %s' % (start_date, end_date)
                    logging.info('No documents found in range %s to %s' % (start_date, end_date))
                    logging.info("Going to next search period")
                    start_date = start_date + datetime.timedelta(date_span)
                    days_left -= date_span
                    date_span = min(date_span, days_left)
                    end_date = start_date + datetime.timedelta(date_span)
                else:
                    print "Complete"
                    print "%d articles downloaded" % total_articles_found
                    logging.info("Complete!")
                    sys.exit()

            elif nDocuments > 500:
                if date_span < 2:
                    logging.error("Search span reduced to below 1 day!")
                    sys.exit()
                else:
                    logging.info("Shrinking search range")
                    date_span = int(date_span / 2)
                    end_date = start_date + datetime.timedelta(date_span)
                    time.sleep(2)
            else: 
                total_articles_found += nDocuments

                if days_left > 0:
                    logging.info("Going to next search period")
                    
                    # update the start date based on the previous date span
                    start_date = start_date + datetime.timedelta(date_span)

                    # decrease the number of days left
                    days_left -= date_span

                    # increase the date span if we found less than 100 documents
                    if nDocuments < 100:
                        date_span = int(date_span * 2)

                    # cap the date span at the number of days left
                    date_span = min(date_span, days_left)

                    # adjust the end date
                    end_date = start_date + datetime.timedelta(date_span)                                            

                    first_page = False


            print "%d days left" % days_left

    print "Waiting..."
    time.sleep(10)
    print "Complete!"
    print "%d articles downloaded" % total_articles_found
    driver.close()


def process_query(url, driver, first_page, download_dir, record_filename, destination_filename, output_filelist):
    # load the webpage
    print url
    logging.info("loading %s" % url)
    got_url = False
    for j in range(10):
        try:
            logging.info('trying url')
            driver.get(url)
            got_url = True
            break
        except WebDriverException, e:
            logging.warning(str(e))
            print "waiting for Chrome to find url"
            time.sleep(2)

    if not got_url:
        print '** FAILED ** on getting url'
        logging.error('** FAILED ** on getting url')
        return -1

    # look for the main frame (which contains the download button)
    frame_ready = False
    for j in range(5):
        try:
            logging.info('finding mainFrame')
            driver.find_element_by_name('mainFrame')
            frame_ready = True
            break
        except WebDriverException, e:
            logging.warning(str(e))
            print "waiting to find mainFrame"
            time.sleep(2)

    if not frame_ready:
        print '** FAILED ** on finding mainFrame'
        logging.error('** FAILED ** on finding mainFrame')
        return -2

    logging.info('switching to mainFrame')
    driver.switch_to.frame('mainFrame')

    source_text = driver.page_source
    match = re.search('var documentCount = (\d+);', source_text)
    nDocuments = int(match.groups(0)[0])
    logging.info('%d articles found' % nDocuments)
    print nDocuments, "articles found"

    # if no articles were found, return immediately
    if nDocuments == 0:
        return 0

    if nDocuments < 500:
        # look for the download button and click it
        script_ready = False
        for j in range(10):
            try:
                logging.info('attempting to open delivery window')
                driver.execute_script("javascript:openDeliveryWindow(this, 'delivery_DnldRender');")
                script_ready = True
                break
            except WebDriverException, e:
                logging.warning(str(e))
                logging.info("waiting to open delivery window")
                time.sleep(2)

        if not script_ready:
            print '** FAILED ** on opening delivery window'
            logging.error('** FAILED ** on opening delivery window')
            return -1

        # switch to the download popup window
        logging.info('switching to delivery window')
        driver.switch_to.window(driver.window_handles[1])

        # for the first article, choose text format (will remain as default for the rest)
        count = 0
        if first_page:
            page_loaded = False
            while not page_loaded:
                try:
                    logging.info('attempting to find delFmt')
                    select = Select(driver.find_element_by_name("delFmt"))
                    select.select_by_value("QDS_EF_GENERICTYPE")
                    page_loaded = True
                except WebDriverException, e:
                    logging.warning(str(e))
                    print "waiting on find delFmt"
                    time.sleep(2)
                count += 1
                if count > 10:
                    print '** FAILED ** on finding delFmt'
                    logging.error('** FAILED ** on finding delFmt')
                    return -1

        # look for the download button in the popup window and click it
        script_ready = False
        for j in range(10):
            try:
                logging.info('attempting to find execute delivery_DnldForm')
                driver.execute_script("javascript:onAction('delivery_DnldForm');")
                script_ready = True
                break
            except WebDriverException, e:
                logging.warning(str(e))
                print "waiting on to find delivery_DnldForm"
                time.sleep(2)

        if not script_ready:
            print '** FAILED ** on executing delivery_DnldForm'
            logging.error('** FAILED ** on executing delivery_DnldForm')
            return -1

        link_found = False
        download_name = None
        for j in range(10):
            try:
                logging.info('attempting to find download link')
                elements = driver.find_elements_by_css_selector("a[href*='Download']")
                if len(elements) > 0:
                    first_link = elements[0]
                    download_name = first_link.text

                    first_link.click()
                    link_found = True
                    break
                else:
                    time.sleep(3)

            except WebDriverException, e:
                logging.warning(str(e))
                print "waiting for download link outside"
                time.sleep(3)
                print e

        if not link_found:
            print '** FAILED ** on finding download link'
            logging.error('** FAILED ** on finding download link')
            return -1

        # wait for the file to appear, then change its name
        full_download_name = os.path.join(download_dir, download_name)
        print "Downloading", full_download_name
        while not os.path.exists(full_download_name):
            time.sleep(2)
            print '.'

        time.sleep(2)

        print "Renaming", full_download_name, "to", destination_filename
        os.rename(full_download_name, os.path.join(download_dir, destination_filename))
        output_filelist.append(os.path.join(download_dir, destination_filename))

        with open(record_filename, 'a') as output_file:
            output_file.write(url + ' ' + destination_filename + ' ' + str(nDocuments) + '\n')

        # if we haven't seen this file before, add it to the index
        #if k not in filename_index:
        #    filename_index[k] = download_name

        #if unicode(filename_index[k]) != unicode(download_name):
        #    log_message(log_filename, k, '* Changing name of downloaded file from ' + unicode(download_name) + ' to ' + filename_index[k])
        #    time.sleep(2)
        #    if os.path.exists(os.path.join(download_dir, download_name)):
        #        print "Renaming", unicode(download_name), "to", filename_index[k]
        #        os.rename(os.path.join(download_dir, download_name), os.path.join(download_dir, unicode(filename_index[k])))

        # close the pop-up window
        logging.info('closing popup')
        driver.close()

        logging.info('Finished with ' + url)

        # Switch back to the main window
        logging.info('switching to main window')
        driver.switch_to.window(driver.window_handles[0])
        return nDocuments

    else:
        logging.info("more than 500 documents found")
        return nDocuments


def change_old_filename(download_dir, old_name):
    
    new_name = os.path.splitext(old_name)[0] + 'z' + '.TXT'

    full_old_name = os.path.join(download_dir, old_name)
    full_new_name = os.path.join(download_dir, new_name)

    print "Changing name from", old_name, "to", new_name
    if os.path.exists(full_old_name):
        os.rename(full_old_name, full_new_name)

    return new_name



if __name__ == '__main__':
    main()

