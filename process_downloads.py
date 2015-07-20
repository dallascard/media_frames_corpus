## STILL A WORK IN PROGRESS

import os
import re
import sys
import json
import codecs
import datetime
from optparse import OptionParser

import parse_LN_to_JSON



def main():
    # Handle input options and arguments
    usage = "%prog <subject>"
    parser = OptionParser(usage=usage)
    parser.add_option('-d', dest='download_dir', default="./downloads",
              help='Download directory; default=%default')
    parser.add_option('-o', dest='output_dir', default='./articles',
                  help='Output directory (to write article files); default=%default')
    (options, args) = parser.parse_args()

    (options, args) = parser.parse_args()
    if len(args) < 1:
        sys.exit("Please provide a subject (e.g. immigration)")
    else:
        subject = args[0]

    if subject == 'immigration':
        prefix = 'IMM'
    elif subject == 'smoking':
        prefix = 'TOB'
    elif subject == 'samesex':
        prefix = 'SSM'
    else:
        sys.exit("Please specify 'immigration', 'smoking', or 'samesex'")


    # create download directory
    if options.download_dir == './downloads':
        download_directory = os.path.join(os.getcwd(), 'downloads', subject)
    else:
        download_directory = os.path.join(options.download_dir, subject)
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    if options.output_dir == './articles':
        output_dir = os.path.join(os.getcwd(), 'articles', subject)
    else:
        output_dir = os.path.join(options.output_dir, subject)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    index_dir = os.path.join(os.getcwd(), 'indices')
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    
    
    annotation_filename = os.path.join(os.getcwd(), 'annotations', subject + '.json')
    index_filename = os.path.join(index_dir, subject + '_index.json')

    with codecs.open(annotation_filename, 'r') as input_file:
        annotations = json.load(input_file, encoding='utf-8')

    print "Processing articles"
    process_text_files(download_directory, annotations, index_filename, output_dir, prefix)


def process_text_files(download_directory, annotations, index_filename, output_dir, prefix):

    with codecs.open(index_filename, 'r') as input_file:
        filename_index = json.load(input_file)

    delete_list = get_del_list()
    insert_list = get_insert_list()
    replace_list = get_replace_list()
    sublist = get_sublist()
    target_nums = get_target_numbers()
    max_lengths = get_max_lengths()

    keys = annotations.keys()
    keys.sort()
    for ki, k in enumerate(keys):

        parts = k.split('-')
        caseid = parts[-1]

        if k not in filename_index:
            print k, "not found in filename index"
            raw_input("Press enter to continue...")
        else:
            filename = os.path.join(download_directory, filename_index[k])
            if not os.path.exists(filename):
                print filename, " not found!"
                raw_input("Press enter to continue...")
            else:
                if k in target_nums:
                    target_num = target_nums[k]
                else:
                    target_num = 1
                if k in max_lengths:
                    max_length = max_lengths[k]
                else:
                    max_length=225
                
                text, total_docs = parse_LN_to_JSON.parse_LN_to_JSON(filename, '', prefix, caseid, target_num, max_length)                
                
                if k in sublist:
                    text = re.sub(sublist[k][0], sublist[k][1], text)
                if k in delete_list:
                    for c in delete_list[k]:
                        text = text[:c[0]] + text[c[1]:]
                if k in insert_list:
                    for c in insert_list[k]:
                        text = text[:c[0]] + c[1] + text[c[0]:]
                if k in replace_list:
                    for r in replace_list[k]:
                        text = text[:r[0]] + r[1] + text[r[0]+1:]
                
                anns = annotations[k]['annotations']
                lastEnd = -1
                offendingCoder = ''
                for a in anns:
                    start = a['start']
                    end = int(a['end'])
                    coder = a['coder']
                    if end > lastEnd:
                        lastEnd = end
                        offendingCoder = coder
                    if end < start:
                        print "Error: Bad annotation", k, coder
                        print start, end
                        raw_input("Press enter to continue...")

                if lastEnd > len(text):
                    print "Error: mismatched article length", k, offendingCoder
                    print lastEnd, len(text)
                    print text[start:end]
                    raw_input("Press enter to continue...")
                else:                    
                    output_filename = os.path.join(output_dir, k + '.txt')
                    with codecs.open(output_filename, 'w', encoding='utf-8') as output_file:
                        output_file.write(text)               


    print "Processed", len(keys), "articles"


def get_del_list():
    del_list = {}
    del_list['Immigration1.0-12353'] = [(66, 88), (618, 646)]
    del_list['Immigration1.0-14383'] = [(56, 62), (371, 382)]
    del_list['Immigration1.0-15763'] = [(63, 72), (687, 697)]
    del_list['Immigration1.0-11666'] = [(52, 58), (631, 638), (1443, 1445)]
    del_list['Tobacco1.0-19874'] = [(65, 75), (861, 874)]
    del_list['same-sex_marriage1.0-1241'] = [(53, 57), (896, 906)]
    del_list['same-sex_marriage1.0-1622'] = [(64, 74), (406, 419)]
    del_list['same-sex_marriage1.0-1790'] = [(88, 94), (713, 724)]
    del_list['same-sex_marriage1.0-2173'] = [(56, 63), (637, 651)]
    del_list['same-sex_marriage1.0-362'] = [(60, 65), (681, 688)]
    del_list['same-sex_marriage1.0-4547'] = [(1663, 1664)]
    del_list['same-sex_marriage1.0-568'] = [(73, 75), (648, 659)]
    del_list['same-sex_marriage1.0-7603'] = [(1031, 1032)]
    del_list['same-sex_marriage1.0-8361'] = [(1499, 1500)]
    del_list['same-sex_marriage1.0-946'] = [(51, 60), (705, 714)]
    del_list['same-sex_marriage1.0-963'] = [(80, 82), (601, 606)]

    return del_list

def get_insert_list():
    insert_list = {}
    insert_list['Immigration1.0-40400'] = [(64, 'THOMAS SOWELL COLUMN\n\nDATELINE: PALO ALTO, CALIF.\n\n')]
    insert_list['Immigration1.0-41121'] = [(54, 'WILLIAM SAFIRE COLUMN\n\nDATELINE: WASHINGTON\n\n')]
    insert_list['Immigration1.0-41294'] = [(91, 'MONA CHAREN COLUMN\n\nDATELINE: WASHINGTON\n\n')]
    insert_list['Immigration1.0-592'] = [(84, 'THOMAS SOWELL COLUMN\n\nDATELINE: PALO ALTO, CALIF.\n\n')]
    insert_list['same-sex_marriage1.0-10039'] = [(717, " ")]
    insert_list['same-sex_marriage1.0-10121'] = [(222, " ")]
    insert_list['same-sex_marriage1.0-10965'] = [(1036, " ")]
    insert_list['same-sex_marriage1.0-1153'] = [(499, " ")]
    insert_list['same-sex_marriage1.0-1360'] = [(486, " ")]
    insert_list['same-sex_marriage1.0-1408'] = [(313, " ")]
    insert_list['same-sex_marriage1.0-1489'] = [(254, " ")]
    insert_list['same-sex_marriage1.0-1741'] = [(464, " ")]
    insert_list['same-sex_marriage1.0-2101'] = [(566, " ")]
    insert_list['same-sex_marriage1.0-2392'] = [(642, " ")]
    insert_list['same-sex_marriage1.0-2885'] = [(1047, " ")]
    insert_list['same-sex_marriage1.0-3143'] = [(329, " ")]
    insert_list['same-sex_marriage1.0-3223'] = [(184, " ")]
    insert_list['same-sex_marriage1.0-3736'] = [(316, " ")]
    insert_list['same-sex_marriage1.0-3801'] = [(652, " ")]
    insert_list['same-sex_marriage1.0-4009'] = [(1445, " ")]
    insert_list['same-sex_marriage1.0-4033'] = [(1302, " ")]
    insert_list['same-sex_marriage1.0-4169'] = [(1515, " ")]
    insert_list['same-sex_marriage1.0-421'] = [(611, " ")]
    insert_list['same-sex_marriage1.0-4374'] = [(1227, " ")]
    insert_list['same-sex_marriage1.0-5075'] = [(886, " ")]
    insert_list['same-sex_marriage1.0-5449'] = [(724, " ")]
    insert_list['same-sex_marriage1.0-5627'] = [(709, " ")]
    insert_list['same-sex_marriage1.0-6055'] = [(1254, " ")]
    insert_list['same-sex_marriage1.0-6705'] = [(716, " ")]
    insert_list['same-sex_marriage1.0-7085'] = [(623, " ")]
    insert_list['same-sex_marriage1.0-7326'] = [(711, " ")]
    insert_list['same-sex_marriage1.0-7992'] = [(1004, " ")]
    insert_list['same-sex_marriage1.0-8111'] = [(127, " ")]
    insert_list['same-sex_marriage1.0-8170'] = [(226, " ")]
    insert_list['same-sex_marriage1.0-8183'] = [(500, " ")]
    insert_list['same-sex_marriage1.0-8277'] = [(326, " ")]
    insert_list['same-sex_marriage1.0-8547'] = [(865, " ")]
    insert_list['same-sex_marriage1.0-8741'] = [(817, " ")]
    insert_list['same-sex_marriage1.0-8911'] = [(237, " ")]
    insert_list['same-sex_marriage1.0-896'] = [(642, " ")]
    insert_list['same-sex_marriage1.0-9681'] = [(304, " ")]
    return insert_list

def get_replace_list():
    replace_list = {}
    return replace_list

def get_sublist():
    sublist = {}
    sublist['Immigration1.0-32282'] = ('In your community', 'community news roundup')
    sublist['Immigration1.0-31889'] = ('In your community', 'Community news roundup')
    return sublist

def get_target_numbers():
    target_nums = {}
    target_nums['Immigration1.0-31375'] = 2
    target_nums['Immigration1.0-31625'] = 2
    target_nums['Immigration1.0-32815'] = 2
    target_nums['Immigration1.0-33984'] = 2
    target_nums['Immigration1.0-34469'] = 3
    target_nums['Immigration1.0-34591'] = 3
    target_nums['Immigration1.0-34607'] = 4
    target_nums['Immigration1.0-34670'] = 2
    target_nums['Immigration1.0-34688'] = 2
    target_nums['Immigration1.0-37357'] = 2
    target_nums['Tobacco1.0-6442'] = 2
    target_nums['same-sex_marriage1.0-1004'] = 3
    target_nums['same-sex_marriage1.0-2374'] = 3
    target_nums['same-sex_marriage1.0-4768'] = 2
    target_nums['same-sex_marriage1.0-6115'] = 2
    target_nums['same-sex_marriage1.0-7430'] = 2
    target_nums['same-sex_marriage1.0-8486'] = 2

    return target_nums

def get_max_lengths():
    lengths = {}
    return lengths

if __name__ == '__main__':
    main()

