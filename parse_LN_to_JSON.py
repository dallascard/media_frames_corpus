from optparse import OptionParser
from unicodedata import normalize
import codecs
import re, os

import sources

# Tags used at the top and bottom of L-N files
TOP_TAGS = [u'BYLINE', u'DATELINE', u'HIGHLIGHT', u'LENGTH', u'SECTION', u'SOURCE', u'E-mail']
END_TAGS = [u'CATEGORY', u'CHART', u'CITY', u'COMPANY', u'CORRECTION', u'CORRECTION-DATE', u'COUNTRY', u'CUTLINE', u'DISTRIBUTION', u'DOCUMENT-TYPE', u'ENHANCEMENT', u'GEOGRAPHIC',  u'GRAPHIC', u'INDUSTRY', u'JOURNAL-CODE', u'LANGUAGE', u'LOAD-DATE', u'NAME', u'NOTES', u'ORGANIZATION', u'PERSON', u'PHOTO', u'PHOTOS', u'PUBLICATION-TYPE', u'SERIES', u'STATE', u'SUBJECT', u'TICKER', u'TYPE', u'URL']
MONTHS = {u'january':1, u'february':2, u'march':3, u'april':4, u'may':5, u'june':6, u'july':7, u'august':8, u'september':9, u'october':10, u'november':11, u'december':12}



# This function does the actual parsing into sections, by modifying doc in place
def parse_text(prefix, doc, labels, text):

    # Variables for error checking
    date_line_hash = {}
    line1_hash = {}
    post_date_hash = {}
    post_title_hash = {}


    if doc.has_key(u'CASE_ID'):
        case_id = doc[u'CASE_ID']

        
        # make a hash of where we find the date (for error checing)
        if u'DATE' in labels:
            date_line = labels.index(u'DATE')
            if date_line_hash.has_key(date_line):
                date_line_hash[date_line] += 1
            else:
                date_line_hash[date_line] = 1
        
        # assign the source and a possible disclaimer based on where we find the date
        if labels[0] != u'DATE':
            labels[0] = u'LN_SOURCE'
            
            if labels[1] != u'DATE':
                labels[1] = u'DISCLAIMER'
                if line1_hash.has_key(text[1]):
                    line1_hash[text[1]] += 1
                else:
                    line1_hash[text[1]] = 1

                                
        # if duplicate top tags, only keep the first
        for t in TOP_TAGS:
            count = labels.count(t)
            if count > 1:
                index = labels.index(t)
                for j in range(index+1, len(labels)):
                    if labels[j] == t:
                        labels[j] = u'UNKNOWN'

        # if duplicate end tags, only keep the last
        for t in END_TAGS:
            count = labels.count(t)
            while count > 1:
                index = labels.index(t)
                labels[index] = u'UNKNOWN'
                count = labels.count(t)

        # fill in unknown labels between top tags (treating byline specially)
        for t in range(len(labels)):                                       
            if labels[t] == u'UNKNOWN' and labels[t-1] in TOP_TAGS and labels[t+1] in TOP_TAGS:
                if labels[t-1] == u'BYLINE':
                    labels[t] = u'BYLINE_EXTRA'
                else:
                    labels[t] = u'TOP_MISC'
                    

        # after removing duplicate tags, search again for first and last top and end tags
        [first_top_tag, last_top_tag, first_end_tag, u_pre_top_tag, u_bw_top_tag, u_post_top_tag] = find_breakpoints(labels)

        # deal with artcles where the body starts with an end tag
        # if it starts with "SUBJECT", "CHART", or "NAME", assume it's actually
        # the first paragraph of the article, and update the labels
        if u_bw_top_tag == 0 and u_post_top_tag == 0:
            if first_end_tag < len(labels):
                if labels[first_end_tag] == u'SUBJECT' or labels[first_end_tag] == u'CHART' or labels[first_end_tag] == u'NAME':
                    labels[first_end_tag] = u'UNKNOWN'

        # after doing the above correction, find these breakpoints again
        [first_top_tag, last_top_tag, first_end_tag, u_pre_top_tag, u_bw_top_tag, u_post_top_tag] = find_breakpoints(labels)

        # assign lines as part of the title or body, based on the breakpoints
        # Three cases:
        if u_bw_top_tag == 0:
        	# First case:
            if u_post_top_tag == 0:
                # body above top tags
                for t in range(first_top_tag):
                    if labels[t] == u'UNKNOWN':
                        labels[t] = u'BODY'
            # Second case:
            else:
                # title above first top tag
                for t in range(first_top_tag):
                    if labels[t] == u'UNKNOWN':
                        labels[t] = u'TITLE'
                # body after last top tag
                for t in range(last_top_tag, first_end_tag):
                    if labels[t] == u'UNKNOWN':
                        labels[t] = u'BODY'
        # Third case:
        else:
            # title before first top tag
            for t in range(first_top_tag):
                if labels[t] == u'UNKNOWN':
                    labels[t] = u'TITLE'         
            # body b/w top tags
            for t in range(first_top_tag, last_top_tag):
                if labels[t] == u'UNKNOWN':
                    labels[t] = u'BODY'
            # misc after last top tag
            for t in range(last_top_tag, first_end_tag):
                if labels[t] == u'UNKNOWN':
                    labels[t] = u'END_MISC'
                         
        # deal with breakpoints in end tags
        current_label = u''
        for t in range(len(labels)):
            if labels[t] == u'UNKNOWN':
                labels[t] = current_label
            else:
                current_label = labels[t]


        # now build the document from the lines
        top_tags = {}       # a list of top tags
        paragraphs = []     # a list of body paragraphs
        end_tags = {}       # a list of end tags
        top_misc = u''      # things we can't parse from the top of the article
        end_misc = u''      # things we can't parse from the bottom of the article
        current = u''
        current_label = labels[0]
        
        for t in range(len(labels)):
            if labels[t] == u'LN_SOURCE':
                source = text[t]
                source = source.lower()
                source = re.sub('^the', '', source, 1)
                source   = source.lstrip()
                doc[u'SOURCE'] = source
            elif labels[t] == u'DISCLAIMER':
                doc[u'DISCLAIMER'] = text[t]
            elif labels[t] == u'TITLE':
                if labels[t-1] != u'TITLE':
                    doc[u'TITLE'] = text[t]
                else:
                    if doc.has_key(u'TITLE_EXTRA'):
                        doc[u'TITLE_EXTRA'] += u' ** ' + text[t]
                    else:
                        doc[u'TITLE_EXTRA'] = text[t]
            elif labels[t] in TOP_TAGS:
                tag_text = text[t]
                index = tag_text.find(':')
                tag_text = tag_text[index+1:]
                tag_text = tag_text.lstrip()
                top_tags[labels[t]] = tag_text
            elif labels[t] == u'BYLINE_EXTRA':
                top_tags[labels[t]] = text[t]
            elif labels[t] == u'TOP_MISC':
                if top_tags.has_key(u'TOP_MISC'):
                    top_tags[labels[t]] += u' ** ' + text[t]
                else:
                    top_tags[labels[t]] = text[t]
            elif labels[t] == u'BODY':
                if labels[t-1] != u'BODY':
                    paragraphs.append(text[t])
                else:                   
                    # Check to see if we should append this line to the last
                    append = True
                    # First, try to join hyperlinks, email addresses and
                    # hyphenated words that have been split
                    if re.search(u'[/@-]$', paragraphs[-1]):
                        if re.search(u'^[a-z]', text[t]):
                            paragraphs[-1] = paragraphs[-1] + u'' + text[t]
                            append = False

                    # Also search for the symbols at the start of the next line
                    elif re.search(u'^[/@]', current):
                        paragraphs[-1] = paragraphs[-1] + 'u' + text[t]
                        append = False

                    # Finally, try to join sentences that have been split
                    # i.e. the last paagraph doesn't end with an end character
                    elif not re.search(u'[\.\"\'?!:_]$', paragraphs[-1]):
                        # and the next paragraph doesn't start with a start symbol.
                        if not re.search(u'^[A-Z"\'>*-\.\(0-9=\$%_]|(http)|(www)', text[t]):
                            paragraphs[-1] = paragraphs[-1] + u' ' + text[t]
                            append = False

                    # in all other cases, just add the input as a new paragraph
                    if (append == True):
                        paragraphs.append(text[t]) 

            elif labels[t] in END_TAGS:
                if labels[t] != labels[t-1]:
                    tag_text = text[t]
                    index = tag_text.find(':')
                    tag_text = tag_text[index+1:]
                    tag_text = tag_text.lstrip()
                    end_tags[labels[t]] = tag_text
                else:
                    end_tags[labels[t]] += text[t]

            elif labels[t] == u'END_MISC':
                if end_tags.has_key(u'BOTTOM_MISC'):
                    end_tags[u'BOTTOM_MISC'] += u' ** ' + text[t]
                else:
                    end_tags[u'BOTTOM_MISC'] = text[t]

            elif labels[t] == u'COPYRIGHT':
                doc[u'COPYRIGHT'] = text[t]
                
            doc[u'TOP'] = top_tags
            doc[u'BODY'] = paragraphs
            doc[u'BOTTOM'] = end_tags

            

# Remove tags, and shorten the body of the article to a certain length, rounded up
def create_shortened_version(doc, prefix, max_length=225):
    # write our header to match the annotated versions
    text = ''
    text += prefix[0:3].upper() + u'-' + doc[u'CASE_ID']
    text += u'\n\n'
    text += "PRIMARY"
    text += u'\n\n'

    # look for the title in the json file, and write it to the output file
    if doc.has_key(u'TITLE'):
        text += doc[u'TITLE']
        text += u'\n\n'

    # then get the text of the article
    if doc.has_key(u'BODY'):
        body = doc[u'BODY']
        word_count = 0      # count of words found in the document
        p = 0               # paragarph number
        # go through each paragraph in the body and add it to the output
        # stop when we reach the end of the body, or we have enough words
        while (word_count < max_length) and (p < len(body)):
            # grab the next paragraph
            paragraph = body[p]
            # split it into words and count them, nothing fancy
            words = paragraph.split()
            word_count += len(words)

            # add the paragraph to the text to be written to the output
            text += paragraph
            # add newlines to separate pargraphs 
            text += u'\n\n'

            # go onto the next paragraph
            p += 1

    return text



# This function finds the division between sections in an article
def find_breakpoints(labels):

	# Search for the first and last top and end tags
    first_top_tag = len(labels)
    last_top_tag = 0
    first_end_tag = len(labels)
    for t in range(len(labels)):
        if labels[t] in TOP_TAGS:
            last_top_tag = t
            if t < first_top_tag:
                first_top_tag = t
        if labels[t] in END_TAGS and t < first_end_tag:
            first_end_tag = t
            

    u_pre_top_tag = 0
    u_bw_top_tag = 0
    u_post_top_tag = 0
    
    # If we found any top tags, generate breakpoints
    if last_top_tag > 0:
        for t in range(0,first_top_tag):
            if labels[t] == u'UNKNOWN':
                u_pre_top_tag += 1
        for t in range(first_top_tag, last_top_tag):
            if labels[t] == u'UNKNOWN':
                u_bw_top_tag += 1
        for t in range(last_top_tag,first_end_tag):
            if labels[t] == u'UNKNOWN':
                u_post_top_tag += 1
    else:
        for t in range(0, first_end_tag):
            if labels[t] == u'UNKNOWN':
                u_post_top_tag += 1
        first_top_tag = 0
    
    return [first_top_tag, last_top_tag, first_end_tag, u_pre_top_tag, u_bw_top_tag, u_post_top_tag] 

 

# Search a multi-article file from Lexis-Nexis for a particular article
# and write a shortened version of it to a file
def search_LN_file_for_articles(input_filename, filename_index, output_dir, article_directory, prefix, max_length=225):

    # split the Lexis-Nexis file into multiple articles
    docs = split_LN_file_into_articles(input_filename)

    # now properly parse all of the documents
    if len(docs.keys()) > 0:
        for d in docs.keys():
            parse_text('TEMP', docs[d], docs[d]['labels'], docs[d]['text'])            
            source = docs[d].get('SOURCE')
            year = str(docs[d].get('YEAR'))
            top = docs[d].get('TOP')
            length_string = top.get('LENGTH')
            # find the article based on source, year, length, and title
            if length_string is not None:
                parts = length_string.split()
                if len(parts) > 0:                    
                    length = parts[0]
                    title = docs[d].get('TITLE')
                    if source in sources.SOURCES:
                        csi = int(sources.SOURCES[source])
                        if csi in article_directory:
                            if year in article_directory[csi]:
                                if length in article_directory[csi][year]:
                                    if title in article_directory[csi][year][length].keys():
                                        caseid = article_directory[csi][year][length][title]
                                        if caseid in filename_index:
                                            output_filename = os.path.join(output_dir, filename_index[caseid])
                                            write_text_file(docs[d], output_filename)


# Write an individual article to a text file, unchanged
def write_text_file(doc, output_filename=None):
    with codecs.open(output_filename, mode='w', encoding='utf-8') as output_file:
        for line in doc['output_text']:
            output_file.writelines(line)        


# split a multi-article Lexis-Nexis file into individual articles
def split_LN_file_into_articles(input_filename):

    # open with utf-8-sig encoding to eat the unicode label
    with codecs.open(input_filename, encoding='utf-8-sig') as input_file:
        input_text = input_file.read()

    # split the text into individual lines
    lines = input_text.split('\r\n')

    expected_docs = 0

    tag_counts = {}             # counts of how many times we see each tag
    first_tag_counts = {}       # counts of how any times we see each tag as the first tag

    docs = {}            # store the article we are working on as a dictionary
    doc = None
    doc_count = 0       # count of how many articles we have found
    doc_num = 0         # document number in the original L-N file
    expected_docs = 0   # the number of articles we expect to find in this L-N file

    # process each line, one at a time
    for line in lines:
        # first, normalize the unicode
        orig_line = line
        line = normalize('NFKD', line)

        # start off looking for new document (each of which is marked as below)
        # also, store the numbers from this pattern as groups for use below
        match = re.search(u'([0-9]+) of ([0-9]+) DOCUMENT', line)

        # if we find a new article
        if match:
        
            # now move on to the new article
            # check to see if the document numbering within the L-N file is consisent
            # (i.e. the next document should be numbered one higher than the last)
            if int(match.group(1)) != doc_num + 1:
                message = u'Missed document after ' + input_filename + u' ' + str(doc_num)
                print message
                #error_file.writelines(message + u'\n\n')

            # if this is the first article in the L-N file, get the expected number of docs
            if expected_docs == 0:
                expected_docs = int(match.group(2))
            elif (expected_docs != int(match.group(2))):
                message = u'Discrepant document counts after ' + input_file_name + u' ' + str(doc_num-1)
                print message
                #error_file.writelines(message + u'\n\n')

            # store the document we've been working on
            if doc is not None:
                doc['text'] = text
                doc['labels'] = labels
                doc['orig_id'] = doc_num
                doc['output_text'] = output_text
                docs[doc_num] = doc

            # get the document number from the original L-N file
            doc_num = int(match.group(1))
            #doc_num += 1
            # add one to the number of documents we've seen
            doc_count += 1

            # start a new document as a dictionary
            doc = {}
            # store what we know so far
            doc[u'CASE_ID'] = doc_num               # temporary identifier

            text = []
            labels = []
            parts = line.split()

            # re-write the 1 of X documents line, since we'll be writing articles seperately
            renumbered = '\t1 ' + ' '.join(parts[1:])
            output_text = ['\n', renumbered, '\n']    # a list of lines to write to the text file

            current = u''       # current stores the block we are currently working on
            label = u'UNKNOWN'

        # if we didn't find a new article, label each line with our best guess
        elif doc_count > 0:

            match = False

            # check if thee's anything on this line
            if (line != u''):
                # if so, strip the whitespace and add the current line to our working line
                temp = line.lstrip()
                temp = temp.rstrip()
                current += temp + ' '

            # if not, label the line(s) we've been working on...
            elif (current != u''):
                current = current.rstrip()

                # first check to see if this looks like a tag
                tag_match = re.search(u'^([A-Z]+[-]?[A-Z]+):', current)
                if tag_match:
                    tag = tag_match.group(1)
                    if (tag in TOP_TAGS):
                        label = tag
                    elif (tag in END_TAGS):
                        label = tag

                # then check to see if it could be the copyright line
                copyright_match = re.search(u'^Copyright ', current)
                if label == u'UNKNOWN' and copyright_match:
                    label = u'COPYRIGHT'

                # check if it could be a date (if we don't already have one)
                if label == u'UNKNOWN' and not doc.has_key(u'DATE'):
                    # Dates appear in two different patterns (with and without day)
                    date_match = re.search('([a-zA-Z]*).?\s*(\d\d?).*\s*(\d\d\d\d).*', current)
                    month_yyyy_match = re.search('([a-zA-Z]*).?\s*(\d\d\d\d).*', current)

                    # if we find a pattern, parse it and assign details to the doc
                    if date_match:
                        month_name = date_match.group(1)
                        month_name = month_name.lower()
                        day = date_match.group(2)
                        year = date_match.group(3)
                        if MONTHS.has_key(month_name):
                            month = MONTHS[month_name]
                            doc[u'DATE'] = current
                            doc[u'MONTH'] = int(month)
                            doc[u'DAY'] = int(day)
                            doc[u'YEAR'] = int(year)
                            # also store the date in the format YYYYMMDD
                            fulldate = year + str(month).zfill(2) + day.zfill(2)
                            doc[u'FULLDATE'] = fulldate
                            label = u'DATE'

                    elif month_yyyy_match:
                        month_name = month_yyyy_match.group(1)
                        month_name = month_name.lower()
                        year = month_yyyy_match.group(2)
                        if MONTHS.has_key(month_name):
                            doc[u'DATE'] = current
                            month = MONTHS[month_name]
                            doc[u'MONTH'] = int(month)
                            doc[u'DAY'] = 0
                            doc[u'YEAR'] = int(year)
                            doc[u'FULLDATE'] = fulldate
                            label = u'DATE'

                # append this line to text for this doc
                text.append(current)
                # provide the best guess for its label
                labels.append(label)

                # start a new working line
                current = u''
                label = u'UNKNOWN'

            # append the line, unchanged, to another copy of the document
            output_text.append(orig_line + u'\r\n')

    # save the article we've been working on
    if doc is not None:
        doc['text'] = text
        doc['labels'] = labels
        doc['orig_id'] = doc_num
        doc['output_text'] = output_text        
        docs[doc_num] = doc

    return docs


# convert a specific article within a multi-article Lexis-Nexis file to a dictionary
def parse_LN_to_JSON(input_file_name, output_dir, prefix, case_id, target_num=0, max_length=225, directory=None):

    tag_counts = {}             # counts of how many times we see each tag
    first_tag_counts = {}       # counts of how any times we see each tag as the first tag

    # open the file we've been given
    name_parts = input_file_name.split('/')
    # open with utf-8-sig encoding to eat the unicode label
    with codecs.open(input_file_name, encoding='utf-8-sig') as input_file:
        input_text = input_file.read()

    # split the text into individual lines
    lines = input_text.split('\r\n')

    doc = {}            # store the article we are working on as a dictionary
    doc_count = 0       # count of how many articles we have found
    doc_num = 0         # document number in the original L-N file
    expected_docs = 0   # the number of articles we expect to find in this L-N file

    # process each line, one at a time
    for line in lines:
        # first, normalize the unicode (to get rid of things like \xa0)
        orig_line = line
        line = normalize('NFKD', line)

        # start off looking for new document (each of which is marked as below)
        # also, store the numbers from this pattern as groups for use below
        match = re.search(u'([0-9]+) of ([0-9]+) DOCUMENT', line)

        # if we find a new article
        if match:
        
            # now move on to the new artcle
            # check to see if the document numbering within the L-N file is consisent
            # (i.e. the next document should be numbered one higher than the last)
            if int(match.group(1)) != doc_num + 1:
                message = u'Missed document after ' + input_file_name + u' ' + str(doc_num)
                print message

            # if this is the first article in the L-N file, get the expected number of docs
            if expected_docs == 0:
                expected_docs = int(match.group(2))
            elif (expected_docs != int(match.group(2))):
                message = u'Discrepant document counts after ' + input_file_name + u' ' + str(doc_num-1)
                print message

            # get the document number from the original L-N file
            doc_num = int(match.group(1))
            # add one to the number of documents we've seen
            doc_count += 1

            # look for a particular article within this file
            if doc_num == target_num:
                # start a new document as a dictionary
                doc = {}
                # store what we know so far
                doc[u'CASE_ID'] = case_id               # unique identifier we've been given to use
                #doc[u'ORIG_FILE'] = orig_file_name      # filename of the original L-N file
                #doc[u'ORIG_ID'] = doc_num               # document number in the L-N file

                text = []
                labels = []
                output_text = []    # a list of lines to write to the text file

                current = u''       # current stores the block we are currently working on
                label = u'UNKNOWN'

        # process the lines in the article we want
        elif (doc_num == target_num):

            match = False

            # check if thee's anything on this line
            if (line != u''):
                # if so, strip the whitespace and add the current line to our working line
                temp = line.lstrip()
                temp = temp.rstrip()
                current += temp + ' '

            # if not, label the line(s) we've been working on...
            elif (current != u''):
                current = current.rstrip()

                # first check to see if this looks like a tag
                tag_match = re.search(u'^([A-Z]+[-]?[A-Z]+):', current)
                if tag_match:
                    tag = tag_match.group(1)
                    if (tag in TOP_TAGS):
                        label = tag
                    elif (tag in END_TAGS):
                        label = tag

                # then check to see if it could be the copyright line
                copyright_match = re.search(u'^Copyright ', current)
                if label == u'UNKNOWN' and copyright_match:
                    label = u'COPYRIGHT'

                # check if it could be a date (if we don't already have one)
                if label == u'UNKNOWN' and not doc.has_key(u'DATE'):
                    # Dates appear in two different patterns (with and without day)
                    date_match = re.search('([a-zA-Z]*).?\s*(\d\d?).*\s*(\d\d\d\d).*', current)
                    month_yyyy_match = re.search('([a-zA-Z]*).?\s*(\d\d\d\d).*', current)

                    # if we find a pattern, parse it and assign details to the doc
                    if date_match:
                        month_name = date_match.group(1)
                        month_name = month_name.lower()
                        day = date_match.group(2)
                        year = date_match.group(3)
                        if MONTHS.has_key(month_name):
                            month = MONTHS[month_name]
                            doc[u'DATE'] = current
                            doc[u'MONTH'] = int(month)
                            doc[u'DAY'] = int(day)
                            doc[u'YEAR'] = int(year)
                            # also store the date in the format YYYYMMDD
                            fulldate = year + str(month).zfill(2) + day.zfill(2)
                            doc[u'FULLDATE'] = fulldate
                            label = u'DATE'

                    elif month_yyyy_match:
                        month_name = month_yyyy_match.group(1)
                        month_name = month_name.lower()
                        year = month_yyyy_match.group(2)
                        if MONTHS.has_key(month_name):
                            doc[u'DATE'] = current
                            month = MONTHS[month_name]
                            doc[u'MONTH'] = int(month)
                            doc[u'DAY'] = 0
                            doc[u'YEAR'] = int(year)
                            doc[u'FULLDATE'] = fulldate
                            label = u'DATE'

                # append this line to text for this doc
                text.append(current)
                # provide the best guess for its label
                labels.append(label)

                # start a new working line
                current = u''
                label = u'UNKNOWN'

            # append the line, unchanged, to another copy of the document
            output_text.append(orig_line + u'\r\n')

    # parse the document of interest
    if u'CASE_ID' in doc.keys():
        parse_text(prefix, doc, labels, text)
        doc[u'ANNOTATION_TEXT'] = create_shortened_version(doc, prefix, max_length)

    if doc.has_key(u'ANNOTATION_TEXT'):
        return doc[u'ANNOTATION_TEXT'], doc_count
    else:
        return '', doc_count


