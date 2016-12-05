import os
import glob
import json
import codecs

import numpy as np

from optparse import OptionParser

def main():
    usage = "%prog config_file.json"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    config_file = args[0]
    with codecs.open(config_file, 'r', encoding='utf-8') as input_file:
        config = json.load(input_file)
    subject = config['name']
    annotations_file = os.path.join('annotations', subject + '.json')
    skip_list = config['skip_list']
    n_expected = config['n_expected']

    with codecs.open(annotations_file, 'r', encoding='utf-8') as input_file:
        annotations = json.load(input_file, encoding='utf-8')

    with codecs.open('sources.json', 'r') as input_file:
        sources = json.load(input_file)

    download_index_file = os.path.join('parsed', subject, subject + '.json')
    with codecs.open(download_index_file, 'r', encoding='utf-8') as input_file:
        download_index = json.load(input_file)

    output = {}

    n_successes = 0
    n_unmatched = 0
    n_unfound = 0
    n_empty = 0

    for k_i, key in enumerate(annotations.keys()):
        if key not in skip_list:
            if (k_i % 1000) == 0 and k_i > 0:
                print k_i
            caseid = key.split('-')[-1]
            data = annotations[key]
            source = data['source']
            csi = str(sources[source])
            year = str(data['year'])
            month = str(data['month'])
            day = str(data['day'])
            title = str(data['title']).encode('ascii', 'ignore')
            byline = str(data['byline']).encode('ascii', 'ignore')
            section = str(data['section']).encode('ascii', 'ignore')
            f_annotations = data['annotations']['framing']
            t_annotations = data['annotations']['tone']
            i_annotations = data['annotations']['irrelevant']
            n_annotations = len(f_annotations) + len(t_annotations) + len(i_annotations)
            if n_annotations == 0:
                n_empty += 1
            length = data['length']
            if length != '':
                length = str(int(length))
            page = str(data['page'])

            index_key = ','.join([csi, year, month, day])
            if index_key in download_index:
                csi_matches = download_index[index_key]
            else:
                csi_matches = []

            if year >= 1980 and n_annotations > 0:
                found = False
                for match in csi_matches:
                    if title == match['title'] and byline == match['byline'] and length == match['length']:
                        if key not in output:
                            n_successes += 1
                            found = True
                        text = key[:3] + '-' + caseid + '\n\nPRIMARY\n\n' + match['body']
                        output[key] = {}
                        output[key]['source'] = source
                        output[key]['csi'] = csi
                        output[key]['year'] = year
                        output[key]['month'] = month
                        output[key]['day'] = day
                        output[key]['title'] = title
                        output[key]['byline'] = byline
                        output[key]['section'] = section
                        output[key]['page'] = page
                        output[key]['text'] = text
                        output[key]['annotations'] = {'framing': {}, 'tone': {}, 'irrelevant': {}}
                        # anonymize the coder names and copy over the annotations
                        for coder in f_annotations.keys():
                            output[key]['annotations']['framing'][coder] = f_annotations[coder]

                        for coder in t_annotations.keys():
                            output[key]['annotations']['tone'][coder] = t_annotations[coder]
                if len(csi_matches) == 0:
                    n_unmatched += 1
                elif not found:
                    n_unfound += 1

    #print n_unmatched
    #print n_unfound
    #print n_empty

    output_dir = os.path.join('output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with codecs.open(os.path.join(output_dir, subject + '.json'), 'w', encoding='utf-8') as output_file:
        json.dump(output, output_file, indent=2)

    print "Number of articles expected:", n_expected
    print "Number of articles matched:", n_successes

if __name__ == '__main__':
    main()
