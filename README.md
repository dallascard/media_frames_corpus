    Media Frames Corpus (version 1)
    Copyright (C) 2015
    Dallas Card (Machine Learning Department, Carnegie Mellon University),
    Amber E. Boydstun (Department of Political Science, University of California, Davis),
    Justin H. Gross (Department of Political Science, University of Massachusetts, Amherst)
    Philip Resnik (UMIACS, University of Maryland)
    Noah A. Smith (Computer Science and Engineering, University of Washington)


This is a README for a repository containing annotations for the Media Frames Corpus
====================================================================================



1. Requirements
===============
- Python 2.7
- python modules: codecs, csv, datetime, glob, json, optparse, os, numpy, random, re, selenium, string, sys, time, unicodedata 
- Firefox
- access to Lexis-Nexis academic

2. Contents
===========


- download_articles.py
    The main script to run to download the articles
- process_downloads.py
    The second script to run; once all articles have been downloaded, this will convert them to their proper form
- bulk_downloads.py
    A secondary script to assemble queries to download articles in bulk
- parse_LN_to_JSON.py
    A secondary script to pull the relevant information out of files downloaded from Lexis-Nexis
- sources.py
    A dictionary of the id numbers of various newspapers
- annotations/
    A directory containing one file for each issue, with all annotations and metadata
- indices/
    A directory containing two files for each issue, with the relevant information about filenames
- temp/
    A temporary directory which will be created to hold the bulk files to be downloaded from Lexis Nexis
- downloads/
    A directory which will be created that will contain all of the articles to downloaded from Lexis-Nexis
- articles/
    A directory which will be created where the final copies of each article will end up
- README.md
    This file


3. Obtaining the data
=====================

This repository contains the metadata for all articles in the Media Frames Corpus (version 1), along with the beginning and end (and associated framing dimension) of all annotated spans of text. All of this information is in a single JSON file in the annotations/ directory, with one file for each issue (immigraiton, smoking, and same-sex marriage). To obtain the actual articles, however, it is necessary to have access to Lexis-Nexis acadmic.

Assuming you have access, download this repository and unzip it anywhere. Then, in the media_frames_corpus directory, run:

> python download_articles.py <issue>

where <issue> must be 'immigration', 'smoking', or 'samesex'.

This script will open a Firefox browser and begin downloading all the relevant articles for the corresponding issue, first in large batches (which will be parsed into individual articles), and then individually (to get the ones missing from the batch downloads). **NOTE THAT THIS WILL TAKE SEVERAL HOURS**.

The script will then perform a few minor manipulations (adding spaces, etc) to ensure that the downloaded text matches the text that was annotated.

Firefox will occassionally crash or hang. If this happens (if the last timestamp is more than a few minutes old), simply cancel the excecution and re-run the script. It will pick up from wherever it left off. Once all articles have been downloaded, the last line printed should be "All files downloaded".

Once all files have been downloaded, the second step is to run:

> python process_downloads.py <issue>

again replacing <issue> with the appropriate issue name, as above.

This second script will do some validation of the downloaded files, and write the text to indiviudal files in the articles/ directory, with names that match the dictionary keys in the json files in the annotations/ directory.

The annotations are specified with a coder name (anonymized), a code (corresponding to a framing dimension), a coding round, and a start and end for the annotated span (see reference below for additional details). The codes are mapped to names of framing dimensions in the codes.json file in the annotations/ directory. "start" is the first character using 0-based indexing, and "end" is the last plus one. In python, for example, if the text of the article were loaded into a variable called "text", the annotated span could be extracted using text[start:end]. 

Some users may need to modify the website address needed to access Lexis-Nexis. The default is http://www.lexisnexis.com 

To specify a replacement for this address (upon which all URLs will be built), use the -u option in download_articles.py. For example,

> python download_articles.py immigration -u http://www.lexisnexis.com.libproxy.lib.unc.edu



4. Further Reading
==================
If you use this corpus, please cite the following paper:

Card D, Boydstun AE, Gross JH, Resnik P, Smith NA. The Media Frames Corpus: Annotations of Frames Across Issues. In Proceedings of the Annual Meeting of the Association for Computational Linguistics (ACL 2015), Beijing, China, July 2015. 
http://www.cs.cmu.edu/~dcard/resources/card.acl2015.pdf


5. Contact
==========
If you find any bugs or have questions, please email Dallas Card (dcard@cmu.edu).
