import math
import argparse, json, os
import utils.constants as constants

"""
    Each type has process_path as its source except the scriptload
    since it does not have a child but only parent and process
"""
def get_src(atlas_record):
    if atlas_record['type'] == 'endpoint.event.scriptload':
        return atlas_record['parent_path']
    
    return atlas_record['process_path']

""" 
    Each 'type' has a different dst and dst_type.
    The destination is collected from different attributes in the jsonl file.
    The destionation type is a single letter:
        'process': 'a'
        'file': 'c'
        'NA': 'e'
"""
def get_destionation(atlas_record):
    match atlas_record['type']:
        case 'endpoint.event.filemod':
            return {
                'dst': atlas_record['filemod_name'],
                'dst_type': 'c'
                }
        case 'endpoint.event.regmod':
            return {
                'dst': atlas_record['regmod_name'],
                'dst_type': 'c'
            }           
        case 'endpoint.event.moduleload':
            return {
                'dst': atlas_record['modload_name'],
                'dst_type': 'c'
            }   
        case 'endpoint.event.procend' | 'endpoint.event.procstart':
            return {
                'dst': atlas_record['childproc_name'],
                'dst_type': 'a'
            }   
        case 'endpoint.event.crossproc':
            return {
                'dst': atlas_record['crossproc_name'],
                'dst_type': 'a'
            } 
        case 'endpoint.event.scriptload':
            return {
                'dst': atlas_record['process_path'],
                'dst_type': 'a'
            } 
        case 'endpoint.event.netconn': 
            return {
                'dst': atlas_record['remote_ip'],
                'dst_type': 'e'
            }   

# Converts the src/dst path to a number, for easier handling.
def get_path_id(path, seen_paths, no_paths):
    new_path = 0
    if path not in seen_paths:
        seen_paths[path] = no_paths
        no_paths += 1
        new_path = 1

    return seen_paths[path], no_paths, new_path

""" 
    An action in the jsonl file can contain several action in one,
    e.g., "action":"ACTION_FILE_CREATE | ACTION_FILE_MOD_OPEN | ACTION_FILE_OPEN_WRITE"
    These need to be split into 3 different records to better group the data.
"""
def split_actions_and_add_to_records(value_dict, records):
        actions = value_dict['edge_type'].split('|')
        above_second = False

        for action in actions:
            action = constants.actionDict[action.strip()]

            # It cannot be a new new src/dst since the first action has seen the path before.
            if above_second:
                value_dict['new_src'] = 0               
                value_dict['new_dst'] = 0

            value_dict['edge_type'] = action
            records.append(value_dict)
            above_second = True

        return records

# Writes to the output files, depending on the base length (--length input). 
"""
    Writes to the output files, depending on the base length (--length input). 
"""
def write_to_file(base_outfile, stream_outfile, records, base_length):
    count = 0
    for value_dict in records:
        if count < base_length:
            base_outfile.write(f"{value_dict['src']} {value_dict['dst']} {value_dict['src_type']}"+ 
                    f":{value_dict['dst_type']}:{value_dict['edge_type']}:{count}\n")
        else: 
            stream_outfile.write(f"{value_dict['src']} {value_dict['dst']} {value_dict['src_type']}"+ 
                    f":{value_dict['dst_type']}:{value_dict['edge_type']}:{value_dict['new_src']}"+
                    f":{value_dict['new_dst']}:{count}\n")
        count += 1

        if count % 50000 == 0:
            print("Lines written: ", count)

# Main method that converts the atlas jsonl file to the parsed txt StreamSpot format.
def convert_file_to_streamspot(file, base_output, stream_output, base_graph_size):
 
    input_file = open(file, 'r')
    base_outfile = open(base_output, 'w+')
    stream_outfile = open(stream_output, 'w+')

    seen_paths = dict()
    no_paths = 0
    records = []
    print('Begin reading and parsing file.')

    for line in input_file:
        atlas_record = json.loads(line.strip())
        destination = get_destionation(atlas_record)
        src = get_src(atlas_record)

        src_id, no_paths, new_src = get_path_id(src, seen_paths, no_paths)
        dst_id, no_paths, new_dst = get_path_id(destination['dst'], seen_paths, no_paths)

        value_dict = {
            'src': src_id,
            'src_type': 'a',
            'dst': dst_id,
            'dst_type': destination['dst_type'],
            'edge_type': atlas_record['action'],
            'device_timestamp': atlas_record['device_timestamp'],
            'unknown': '?',
            'graph_id': atlas_record['schema'],
            'new_src': new_src,
            'new_dst': new_dst
        }

        records = split_actions_and_add_to_records(value_dict, records)

    print('Begin sorting records.')
    records_sorted = sorted(records, key=lambda record: record['device_timestamp'])
    print('Begin writing to files.')
    write_to_file(base_outfile, stream_outfile, records_sorted, base_graph_size)

    input_file.close()
    base_outfile.close()
    stream_outfile.close()

# Read the number of rows in a file to calculate the base graph size.
def get_file_length(input_file):
    with open(input_file, 'r') as fp:
        return len(fp.readlines())

# Creates the stream and base directory.
def create_directories(directory):
    directories = ['stream', 'base']
    print(directory)
    for dir in directories:
        output_dir = os.path.dirname(f'{directory}/{dir}')
        print(output_dir + "/" + dir)

        if not os.path.exists(f"{directory}/{dir}"):
            os.makedirs(f"{directory}/{dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Included methods')
    parser.add_argument('-d', '--directory', help='Input and output \'root\' directory e.g. xx/yy/zz. For easier input', type=str)
    parser.add_argument('-i', '--input', help='Input file path and name, e.g. [--directory]name.jsonl', type=str)
    parser.add_argument('-b', '--base', help='Output base file path and name, e.g. [--directory]name.txt', type=str)
    parser.add_argument('-s', '--stream', help='Output stream file path and name, e.g. [--directory]name.txt', type=str)
    parser.add_argument('-l', '--length', help='the length of the base graph in absolute value (default is 10%% of the entire graph)', type=int)
    parser.add_argument('-t', '--test', help='Preset values for testing', type=bool)
    global args
    args = parser.parse_args()

    if args.test:
        base_dir = "../../../data/atlasv2/data/benign/h1/cbc-edr"
        input_file = f"{base_dir}/edr-h1-benign.jsonl"
        base_output = f"{base_dir}/base/base_test.txt"
        stream_output = f"{base_dir}/stream/stream_test.txt"
        create_directories(f'{base_dir}')
    else:
        input_file = args.directory + args.input
        base_output = args.directory + args.base
        stream_output = args.directory + args.stream
        create_directories(args.directory)

    file_length = get_file_length(input_file)
    if not args.length:
        base_graph_size = int(math.ceil(file_length * 0.1))
    else:
        base_graph_size = args.length

    
    convert_file_to_streamspot(input_file, base_output, stream_output, base_graph_size)