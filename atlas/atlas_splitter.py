import math
import argparse, json, os
import utils.constants as constants
import numpy as np
import hashlib

def get_src(src_atlas_record):
    """
        Each type has process_path as its source except the scriptload
        since it does not have a child but only parent and process
    """
    if src_atlas_record['type'] == 'endpoint.event.scriptload':
        return src_atlas_record['parent_path']
    
    return src_atlas_record['process_path']

def get_destionation(dst_atlas_record):
    """ 
        Each 'type' has a different dst and dst_type.
        The destination is collected from different attributes in the jsonl file.
        The destionation type is a single letter:
            'process': 'a'
            'file': 'c'
            'NA': 'e'
    """
    match dst_atlas_record['type']:
        case 'endpoint.event.filemod':
            return {
                'dst': dst_atlas_record['filemod_name'],
                'dst_type': 'c'
                }
        case 'endpoint.event.regmod':
            return {
                'dst': dst_atlas_record['regmod_name'],
                'dst_type': 'c'
            }           
        case 'endpoint.event.moduleload':
            return {
                'dst': dst_atlas_record['modload_name'],
                'dst_type': 'c'
            }   
        case 'endpoint.event.procend' | 'endpoint.event.procstart':
            return {
                'dst': dst_atlas_record['childproc_name'],
                'dst_type': 'a'
            }   
        case 'endpoint.event.crossproc':
            return {
                'dst': dst_atlas_record['crossproc_name'],
                'dst_type': 'a'
            } 
        case 'endpoint.event.scriptload':
            return {
                'dst': dst_atlas_record['process_path'],
                'dst_type': 'a'
            } 
        case 'endpoint.event.netconn': 
            return {
                'dst': dst_atlas_record['remote_ip'],
                'dst_type': 'e'
            }   

def hash_src(src):
    src_hash = hashlib.blake2b(src.encode(), digest_size=3) #3 bytes = 6 digits ABCDEF
    return src_hash.hexdigest()

def create_records(in_file):
    """
        Reads each line/object in the input file and converts the object to
        a record containing the necessary information. Returns the complete
        list of individual records. 
    """
    input_file = open(f'{in_file}.jsonl', 'r')
    records = []

    for line in input_file:
        atlas_record = json.loads(line.strip())
        destination = get_destionation(atlas_record)
        src = get_src(atlas_record)
        src_hash = hash_src(src)
        record_dict = {
            'src': src,
            'src_type': 'a',
            'dst': destination['dst'],
            'dst_type': destination['dst_type'],
            'edge_type': atlas_record['action'],
            'device_timestamp': atlas_record['device_timestamp'],
            'graph_id': atlas_record['schema'],
            'new_src': 0, #Placeholder
            'new_dst': 0, # Placeholder
            'src_hash': src_hash
        }

        records.extend(split_actions_and_add_to_records(record_dict))
    input_file.close()

    return records

def split_actions_and_add_to_records(single_record_dict):
    """ 
        An action in the jsonl file can contain several action in one,
        e.g., "action":"ACTION_FILE_CREATE | ACTION_FILE_MOD_OPEN | ACTION_FILE_OPEN_WRITE"
        These need to be split into 3 different records to better group the data.
    """
    actions = single_record_dict['edge_type'].split('|')
    split_single_records = []

    for action in actions:
        translated_action = constants.actionDict[action.strip()]

        new_record = single_record_dict.copy()
        new_record['edge_type'] = translated_action
        split_single_records.append(new_record)

    return split_single_records

def get_path_id(path, seen_paths, path_id):
    """
        Converts the src/dst path to a number, for easier handling and to comply with
        the Unicorn format.
    """
    new_path = 0

    if path not in seen_paths:
        seen_paths[path] = path_id
        path_id += 1
        new_path = 1
    
    return seen_paths[path], path_id, new_path

def sort_records(sorted_records, number_of_files):
    """
        Sorts the records (each object) first by their device_timestamp and 
        sorts the src/dst ids according to the new list order so the first 
        id in the output starts at 0.
    """

    sorted_records = sorted(sorted_records, key=lambda record: record['device_timestamp'])
    sorted_records_list = np.array_split(sorted_records, number_of_files)
    print(f'Sorted length: {len(sorted_records_list)}')

    for record_list in sorted_records_list:
        seen_paths = dict()
        path_id = 0
        
        for record in record_list:
            src_id, path_id, new_src = get_path_id(record['src'], seen_paths, path_id)
            dst_id, path_id, new_dst = get_path_id(record['dst'], seen_paths, path_id)

            record['src'] = src_id
            record['dst'] = dst_id
            record['new_src'] = new_src
            record['new_dst'] = new_dst
    
    return sorted_records_list

def write_to_file(base_outfile, stream_outfile, records, base_length):
    """
        Writes to the output files, depending on the base length (--length input).
        The first -l records are written to the base file and the rest will be written
        to the stream file.  
    """
    print(f'Sorted length before write: {len(records)}')

    count = 0
    for record in records:
        if count < base_length:
            base_outfile.write(f"{record['src']} {record['dst']} {record['src_type']}"+ 
                    f":{record['dst_type']}:{record['edge_type']}:{count}:{record['src_hash']}\n")
        else: 
            stream_outfile.write(f"{record['src']} {record['dst']} {record['src_type']}"+ 
                    f":{record['dst_type']}:{record['edge_type']}:{record['new_src']}"+
                    f":{record['new_dst']}:{count}:{record['src_hash']}\n")
        
        count += 1
        if count % 50000 == 0:
            print("Lines written: ", count)

def write_to_files(sorted_records_list, base_output, stream_output, base_length):
    record_count = 0
    for sorted_records in sorted_records_list:
        tmp_base = base_output
        tmp_stream = stream_output

        if len(sorted_records_list) > 1:
            tmp_base = f'{base_output}-{record_count}'
            tmp_stream = f'{stream_output}-{record_count}'

        base_outfile = open(f'{tmp_base}.txt', 'w+')
        stream_outfile = open(f'{tmp_stream}.txt', 'w+')
        
        write_to_file(base_outfile, stream_outfile, sorted_records, base_length)
        
        base_outfile.close()
        stream_outfile.close()

        print(f"File {record_count} done.")
        record_count += 1

def convert_file_to_streamspot(input_file, base_output, stream_output, base_length, number_of_files):
    """ Main method that converts the atlas jsonl file to the parsed txt Unicorn format. """
    
    print('Begin reading and parsing file.')
    records = create_records(input_file)

    print('Begin sorting records.')
    sorted_records_list = sort_records(records, number_of_files)

    print(f'Sorted length after return: {len(sorted_records_list)}')

    print('Begin writing to files.')
    write_to_files(sorted_records_list, base_output, stream_output, base_length)


def get_file_length(input_file):
    """ Read the number of rows in a file to calculate the base graph size. """
    with open(f'{input_file}.jsonl', 'r') as fp:
        return len(fp.readlines())

def create_directories(directory):
    """ Creates the stream and base directory. """
    directories = ['stream', 'base']
    print(directory)
    for dir in directories:
        output_dir = f"{directory}/{dir}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Included methods')
    parser.add_argument('-d', '--directory', help='Input and output \'root\' directory e.g. xx/yy/zz. For easier input', type=str)
    parser.add_argument('-i', '--input', help='Input file path and name without file ending, e.g. [--directory]name', type=str)
    parser.add_argument('-b', '--base', help='Output base file path and name without file ending, e.g. [--directory]name', type=str)
    parser.add_argument('-s', '--stream', help='Output stream file path and name without file ending, e.g. [--directory]name', type=str)
    parser.add_argument('-l', '--length', help='The length of the base graph in number of percentages (default is 10%% of the entire graph)', type=int, default=10)
    parser.add_argument('-f', '--files', help='Number of files that the input file should be split into (default is 1 file)', type=int, default=1)

    global args
    args = parser.parse_args()

    print(args.directory+args.base)
    input_file = f"{args.directory}/{args.input}"
    base_output = f"{args.directory}/{args.base}"
    stream_output = f"{args.directory}/{args.stream}"
    create_directories(args.directory)

    file_length = get_file_length(input_file)
    number_of_files = args.files
    base_graph_size = int(math.ceil(file_length * (args.length / 100) / number_of_files))

    convert_file_to_streamspot(input_file, base_output, stream_output, base_graph_size, number_of_files)
