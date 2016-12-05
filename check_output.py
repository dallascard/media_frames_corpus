import os
import json
import codecs

import numpy as np

from optparse import OptionParser


def main():
    usage = "%prog config.json"
    parser = OptionParser(usage=usage)
    parser.add_option('--examples', action="store_true", dest="examples", default=False,
                      help='Print example annotations: default=%default')
    parser.add_option('--ex_freq', dest='ex_freq', default=0.001,
                      help='Proportion of examples to print: default=%default')

    (options, args) = parser.parse_args()
    config_file = args[0]
    with codecs.open(config_file, 'r', encoding='utf-8') as input_file:
        config= json.load(input_file)

    name = config['name']
    data_file = os.path.join('output', name + '.json')
    with codecs.open(data_file, 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)

    print_examples = options.examples
    ex_freq = float(options.ex_freq)

    for k_i, key in enumerate(data.keys()):
        f_annotations = data[key]['annotations']['framing']
        text = data[key]['text']
        if len(f_annotations) > 0:
            for coder in f_annotations.keys():
                for a in f_annotations[coder]:
                    start = a['start']
                    end = a['end']
                    code = a['code']
                    if print_examples and np.random.rand() < ex_freq:
                        print key, coder, start, end, code
                        print text[start:end]
                    if end > len(text)+2:
                        print "** Size mismatch **", key, end, len(text)
                        print text[start:end]


if __name__ == '__main__':
    main()
