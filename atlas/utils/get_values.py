import argparse
import json, os, subprocess, sys
from collections import defaultdict
from datetime import datetime

def print_all(key, value, of):
    of.writelines(f"{key} : {value}\n")
    print(f'{key}')# : {value}')

def print_parser_columns(key, value, of):
    match key:
        case "parent_cmdline" | 'process_cmdline' | 'device_timestamp' | 'process_path' | 'parent_path' | 'scriptload_publisher' | 'scriptload_effective_reputation' | 'scriptload_reputation' | 'scriptload_count' :
        #case 'process_guid' | 'parent_guid' | 'action' | 'device_timestamp' | \
            #'process_cmdline' | 'parent_cmdline' | 'parent_pid' | 'process_pid':

            of.writelines(f"{key} : {value}\n")

def get_types(file, base_dir, output_dir):
    filename = f"{base_dir}/{file}.jsonl"
    output_file = f"{output_dir}/types_{file}__{date}.txt"
    f = open(filename, 'r')
    of = open(output_file, 'w')
    edge_types = list()
    for line in f:
        atlas_record = json.loads(line.strip())
        for key, value in atlas_record.items():
            if key == 'type':
                if value not in edge_types:
                    edge_types.append(value)

    for edge in edge_types:
        of.write(f"{edge}\n")

def timestamp_in_order(file, base_dir, file_type):
    filename = f"{base_dir}/{file}.{file_type}"
    old_time = "1900-07-19 07:24:57.2328953 +0000 UTC"
    
    f = open(filename, 'r')
    for line in f:
        if file_type == 'jsonl':
            atlas_record = json.loads(line.strip())
            record_time = atlas_record['device_timestamp'] 
        else: 
            record_time = line.split('&')[1]

        if record_time < old_time:
            print (f"Record time: {record_time} and old: {old_time}" )
        old_time = record_time

    f.close

# Pretty prints each X jsonl objects.
def pretty_print_object(date, file, base_dir, objects, print_all_cols, print_parser_cols):
    type = ''
    if print_all_cols:
        type = 'all'
    else:
        type = 'parser'
    filename = f"{base_dir}/{file}.jsonl"
    output_file = f"{base_dir}/output/pretty_print_{type}_{file}__{date}_c{count}.txt"

    f = open(filename, 'r')
    of = open(output_file, 'w')
    paths = []
    parent_paths= []
    for line in f:  
        
        if objects <= 0:
            break

        atlas_record = json.loads(line.strip())
        if atlas_record['type'] != 'endpoint.event.scriptload':
            continue
        if atlas_record['process_path'] not in paths:
            print(f"process: {atlas_record["process_path"]} || parent: {atlas_record['parent_path']}")

            paths.append(atlas_record['process_path'])

        if atlas_record['parent_path'] not in parent_paths:
            print(f"parent: {atlas_record["parent_path"]}")

            parent_paths.append(atlas_record['parent_path'])

        for key, value in atlas_record.items():
            if print_all_cols:
                print_all(key, value, of)
            if print_parser_cols:
                print_parser_columns(key, value, of)
        #    of.writelines(f"{key} : {value}\n")
        #    print(f'{key}')# : {value}')
        objects -= 1

        of.write('\n')
        #print("\n")

    f.close()
    of.close

# Find all process_guids in a file and no of occurences. Unrefined code.
def get_guid():
    filename =    "../../../../data/atlasv2/data/attack/h1/cbc-edr-alerts/edr-alerts-h1-m2.jsonl"
    output_file = "../../../../data/atlasv2/data/attack/h1/cbc-edr-alerts/output/guids2.txt"

    f = open(filename, 'r')

    p_guid = defaultdict(int)
    for line in f:
        atlas_record = json.loads(line.strip())
        subprocess.run(f'touch {output_file}', shell=True, executable='/bin/bash')
        
        for key, val in atlas_record.items():
            if(key == "process_guid"):
                p_guid[val] += 1
    
    f.close()
    with open(output_file, 'w') as fp:
        for key, val in p_guid.items():
            subprocess.run(f'echo {key} : {val} >> {output_file}', shell=True, executable='/bin/bash')
    print(p_guid)

# Matches all actions found in a file against our found actions in parser-info.txt
def action_prev_found(date, file, base_dir):
    actions = f"{base_dir}/output/actions_{file}_{date}.txt"
    found = "../parser-info.txt"

    with open(found, 'r') as f:
        found_actions = {line.strip().split(':')[0] for line in f} 

    with open(actions, 'r') as fa:
        for line in fa:
            action = line.split(':')[0].strip()
            if action not in found_actions: 
                print(f"New action: {action}")
    print("actionPrevFound: Done")

# Gets all actions in a file and no of occurences. 
def get_actions(date, file, base_dir):
    filename = f"{base_dir}/{file}.jsonl"
    output_file = f"{base_dir}/output/actions_{file}_{date}.txt"

    f = open(filename, 'r')
    
    p_guid = defaultdict(int)
    for line in f:
        atlas_record = json.loads(line.strip())
        print("här:\n", atlas_record)
        for key, val in atlas_record.items():
            if(key == "action"):
                p_guid[val] += 1

    for k in p_guid.copy():
        if '|' in k:
            p_guid.pop(k)
            valueKeys = k.split('|')
            for vk in valueKeys:
                p_guid[vk.strip()] += 1

    f.close()
    sorted_pguid = dict(sorted(p_guid.items()))
    
    with open(output_file, "w") as fp:
        fp.writelines(f"{key}: {value}\n" for key, value in sorted_pguid.items()) 

    print("getActions: Done")    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Included methods')
    parser.add_argument('-pa', '--prettyAll', help='Pretty print whole jsonl object', type=bool)
    parser.add_argument('-pp', '--prettyParser', help='Pretty print parser args jsonl object', type=bool)
    parser.add_argument('-g', '--guid', help='Get guid', type=bool)
    parser.add_argument('-a', '--action', help='Get action', type=bool)
    parser.add_argument('-f', '--found', help='See if action has been found', type=bool)
    parser.add_argument('-c', '--count', help='Number of times/files to run', type=int, default=1)
    parser.add_argument('-t', '--types', help='Get all types', type=bool)
    parser.add_argument('-ts', '--timestamp', help='Types: txt | jsonl See if records are in order by timestamp', type=str)
    global args
    args = parser.parse_args()

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base_dir = "../../../../data/atlasv2/data/benign/h1/cbc-edr"
    output_dir = f"{base_dir}/output"
    file = f'edr-h1-m1'
    file = f'edr-h1-benign'

    count = args.count
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"New dir: {output_dir}")

    if args.guid:
        get_guid()
    
    if args.timestamp != "":
        timestamp_in_order(file, base_dir, args.timestamp)
    if args.prettyAll or args.prettyParser:
        pretty_print_object(date, file, base_dir, count, args.prettyAll, args.prettyParser)
        print(f"File: {file} done")

    if args.types:
        get_types(file, base_dir, output_dir)
    # In case there are multiple files as in *atlasv2/*/attack/h1/cbc-edr/edr-h1-m*.jsonl
    while(count > 0 and (args.action or args.found)):
       # file = f'{file}-{count}'
        if args.action:
            get_actions(date, file, base_dir)
        if args.found:
            action_prev_found(date, file, base_dir)

        print(f"File: {file} done")
        count -= 1