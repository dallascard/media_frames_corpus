## NOTE: This repo has been deprecated, due to changes to the Lexis-Nexis interface.



Media Frames Corpus v2.0
====================================================================================


1. Requirements
===============
- Python 2.7 with selenium module installed (via pip)
- Chrome browser
- [Chrome Driver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
- access to Lexis-Nexis academic


2. Obtaining the articles
=====================

This repository contains the metadata for all articles in the Media Frames Corpus (version 2), along with the beginning and end (and associated framing dimension) of all annotated spans of text. All of this information is in a single JSON file in the annotations/ directory, with one file for each issue (immigration, smoking, and same-sex marriage). To obtain the actual articles, however, it is necessary to have access to Lexis-Nexis academic.

To begin, download a copy of the chrome driver, and place it in a subdirectory of this repo called `chrome`.

Second, if you do not already have it, install `selenium` using pip:

	> pip install selenium

Then, in the repo directory, run:

	> python get_news_articles.py config_file.json
	
where `config_file.json` is one of the provided configuration files (e.g. `immigration_config.json`, etc.)

If your chrome driver is located elsewhere, you can specify it with the -c option, i.e.:

	> python get_news_articles.py config_file.json -c /path/to/chromedriver

This script will open a Chrome browser window and begin downloading all the relevant articles for the corresponding issue. This requires that you have access to Lexis-Nexis, and it may take a few hours per issue.

Once all files have been downloaded, the second step is to run:

	> python parse_LN_to_JSON.py config_file.json

which splits the downloads up into individual articles, and extracts the structured information (author, title, etc.)

Third, run:

	> python process_JSON_files.py config_file.json

This script recombines the information from each article in such a way so as to match the articles as they were annotated, and then recombines all the articles into a single JSON file. 

Finally, run:

	> python combine_text_and_annotations.py config_file.json
	
This will produce a single file in the output directory which contains the annotations and text for each article.

The annotations are specified with a coder name (anonymized), a code (corresponding to a framing dimension), and a start and end for the annotated span (see reference below for additional details). The codes are mapped to names of framing dimensions and tones in the `codes.json` file in the `annotations` directory. "start" is the first character using 0-based indexing, and "end" is the last plus one. In python, for example, if the text of the article were loaded into a variable called "text", the annotated span could be extracted using `text[start:end]`. 

Some users may need to modify the website address needed to access Lexis-Nexis. The default is http://www.lexisnexis.com 

To specify a replacement for this address (upon which all URLs will be built), use the -u option in download_articles.py. For example,

	> python get_news_articles.py immigration_config.json -u http://www.lexisnexis.com.libproxy.lib.unc.edu


3. Revision History
=======

5/Dec/2016:

- v2.0 of the MFC provides a new set of annotations which entirely replaces those from v1.0.
- The annotations scheme remains the same, except that the overall Tone of the article (pro, neutral, anti) has been added. Also, for these annotations, the annotators resolved all conflicts on the primary frame and tone of each article. (Note that some articles only have annotations for framing or tone, but not both).
- Finally, the browser was switched from Firefox to Chrome, and the download process sped up.
- data format has changed slightly
- Note that annotator IDs are NOT the same across issues



4. References
==================
If you make use of this corpus, please cite the following paper:

Card D, Boydstun AE, Gross JH, Resnik P, Smith NA. The Media Frames Corpus: Annotations of Frames Across Issues. In Proceedings of the Annual Meeting of the Association for Computational Linguistics (ACL 2015), Beijing, China, July 2015. [http://www.cs.cmu.edu/~dcard/resources/card.acl2015.pdf](http://www.cs.cmu.edu/~dcard/resources/card.acl2015.pdf)



5. Contact
==========
If you find any bugs or have questions, please email Dallas Card (dcard at cmu dot edu).
