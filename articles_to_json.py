import os
import json
import glob
import codecs
from optparse import OptionParser


def main():
	""" Read in all the text files in the given directory, and put them all in a big json directory"""
    
	usage = "%prog input_dir output_file"
	parser = OptionParser(usage=usage)

	(options, args) = parser.parse_args()

	input_dir = args[0]
	output_filename = args[1]

	articles = {}

	files = glob.glob(os.path.join(input_dir, '*.txt'))
	for f in files:
		basename = os.path.basename(f)
		case_id = os.path.splitext(basename)[0]

		with codecs.open(f, 'r', encoding='utf-8') as input_file:
			text = input_file.read()
			parts = text.split('\n\n')
			text = '\n\n'.join(parts[2:])
			articles[case_id] = text

	with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
		json.dump(articles, output_file, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
