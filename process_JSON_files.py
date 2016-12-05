import os
import glob
import json
import codecs

from collections import defaultdict
from optparse import OptionParser


def main():
    usage = "%prog config_file.json"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    parser.add_option('--shingle', action="store_true", dest="shingle", default=False,
                      help='Do shingling: default=%default')

    (options, args) = parser.parse_args()
    shingle = options.shingle

    config_file = args[0]
    with codecs.open(config_file, 'r', encoding='utf-8') as input_file:
        config = json.load(input_file)
    subject = config['name']

    with codecs.open('sources.json', 'r', encoding='utf-8') as input_file:
        sources = json.load(input_file)

    print "Processing JSON files"
    unknown_sources = set()
    download_index = defaultdict(list)
    shingled = defaultdict(list)

    parsed_dir = os.path.join('parsed', subject, 'json')
    files = glob.glob(os.path.join(parsed_dir, '*.json'))

    for f_i, f in enumerate(files):
        if (f_i % 1000) == 0 and f_i > 0:
            print f_i
        with codecs.open(f, 'r', encoding='utf-8') as input_file:
            data = json.load(input_file, encoding='utf-8')

        year = int(data['YEAR'])
        month = int(data['MONTH'])
        day = int(data['DAY'])

        source = data['SOURCE']
        if 'BYLINE' in data['TOP']:
            byline = data['TOP']['BYLINE'].encode('ascii', 'ignore')
        elif 'TITLE_EXTRA' in data:
            byline = data['TITLE_EXTRA'].encode('ascii', 'ignore')
        else:
            byline = ""

        if 'TITLE' in data:
            title = data['TITLE'].encode('ascii', 'ignore')
        elif 'TITLE' in data['TOP']:
            title = data['TOP']['TITLE'].encode('ascii', 'ignore')
        else:
            title = ""

        if 'SECTION' in data['TOP']:
            section = data['TOP']['SECTION'].encode('ascii', 'ignore')
        else:
            section = ""

        if 'LENGTH' in data:
            length = data['LENGTH'].split()[0]
        elif 'LENGTH' in data['TOP']:
            length = data['TOP']['LENGTH'].split()[0]
        else:
            length = ""

        body_parts = data['BODY']
        body = ""
        body_words = []
        for body_part in body_parts:
            if len(body) > 0:
                body = '\n\n'.join([body, body_part])
            else:
                body = body_part
            body_words.extend(body_part.split())
            if len(body_words) >= 225:
                break

        body = body.rstrip()
        if title != "":
            body = title + '\n\n' + body

        if source in sources:
            csi = int(sources[source])
            key = str(csi) + ',' + str(year) + ',' + str(month) + ',' + str(day)
            download_index[key].append({'title': title, 'byline': byline, 'length': length, 'section': section,
                                        'body_length': len(body), 'body': body, 'file': f})
            if shingle:
                shingles = list(set([body[i:i+4] for i in range(len(body)-4)]))
                shingled[key].append({'title': title, 'byline': byline, 'length': length, 'section': section,
                                      'body_length': len(body), 'shingles': shingles, 'file': f})

        else:
            unknown_sources.add(source)

    output_dir = os.path.join('parsed', subject)

    output_filename = os.path.join(output_dir, subject + '.json')
    with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
        json.dump(download_index, output_file, encoding='utf-8', indent=2, sort_keys=False)

    if shingle:
        output_filename = os.path.join(output_dir, 'shingles.json')
        with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
            json.dump(shingled, output_file, encoding='utf-8', indent=2, sort_keys=False)


if __name__ == '__main__':
    main()
