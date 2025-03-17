import argparse
import json, os, subprocess, sys
from collections import defaultdict
from datetime import datetime

# Pretty prints each X jsonl objects. Unrefined code.
def pretty_print_object():
    filename =    "../../../../data/atlasv2/data/benign/h1/cbc-edr-alerts/test.jsonl"
    filename = "../../../../data/atlasv2/data/attack/h2/cbc-edr/edr-h2-m1.jsonl"
    output_file = "../../../../data/atlasv2/data/benign/h1/cbc-edr-alerts/output.txt"
    output_file = "../../../../data/atlasv2/data/attack/h2/cbc-edr/output_test1024.txt"

    f = open(filename, 'r')

    objects = 3
    for line in f:
        if objects <= 0:
            break
        objects -= 1

        atlas_record = json.loads(line.strip())
        subprocess.run(f'touch {output_file}', shell=True, executable='/bin/bash')
        for key, value in atlas_record.items():
            subprocess.run(f'echo {key} : {value} >> {output_file}', shell=True, executable='/bin/bash')
            print(f'{key} : {value}')

        subprocess.run(f'echo "" >> {output_file}', shell=True, executable='/bin/bash')

        print("\n")
    f.close()

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
    parser.add_argument('-p', '--pretty', help='pretty print jsonl object', type=bool)
    parser.add_argument('-g', '--guid', help='get guid', type=bool)
    parser.add_argument('-a', '--action', help='get action', type=bool)
    parser.add_argument('-f', '--found', help='see if action has been found', type=bool)
    global args
    args = parser.parse_args()

    date = datetime.now()
    base_dir = "../../../../data/atlasv2/data/benign/h1/cbc-edr"
    output_dir = f"{base_dir}/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"New dir: {output_dir}")

    if args.guid:
        get_guid()
    if args.pretty:
        pretty_print_object()

    # In case there are multiple files as in *atlasv2/*/attack/h1/cbc-edr/edr-h1-m*.jsonl
    count = 1
    while(count > 0):
        file = f'edr-h1-benign' # f'edr-h1-m{count}'
        if args.action:
            get_actions(date, file, base_dir)
        if args.found:
            action_prev_found(date, file, base_dir)
        print(f"File: {file} done")
        count -= 1