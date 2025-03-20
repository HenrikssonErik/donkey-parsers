import argparse, json, os
import utils.constants as constants

# These are 100% wrong at the moment.
def print_parser_columns(key, value, columns):
    match key:
        case 'parent_pid':
            if type(value) is float:
                columns[0] = int(value)
            else:
                columns[0] = value
        case 'process_pid':
            columns[1] = value
        case 'parent_cmdline':
            columns[2] = value
        case 'process_cmdline': 
            columns[3] = value
        case 'action':
            if '|' in value:
                columns[4] = value
            else:
                columns[4] = constants.actionDict[value]

# Pretty prints each X jsonl objects.
def convert_file_to_streamspot(file, base_dir):
    filename = f"{base_dir}/{file}.jsonl"
    output_file = f"{base_dir}/converted/ConvertedTest.txt"

    if not os.path.exists(f"{base_dir}/converted"):
        os.makedirs(f"{base_dir}/converted")

    f = open(filename, 'r')
    outFile = open(output_file, 'w+')
    count = 0

    for line in f:
        atlas_record = json.loads(line.strip())
        columns = ["", "", "", "", ""]

        for key, value in atlas_record.items():
            print_parser_columns(key, value, columns)

        if '|' in columns[4]:
            actions = columns[4].split('|')
            for action in actions:

                columns[4] = constants.actionDict[action.strip()]
                count += 1
                # Src, src_type, dst, dst_type, edge_type, count
                outFile.write(f"{columns[0]} {columns[1]} {columns[2]}:{columns[3]}:{columns[4]}:{count}\n")
        else:
            count += 1
            # Src, src_type, dst, dst_type, edge_type, 
            outFile.write(f"{columns[0]} {columns[1]} {columns[2]}:{columns[3]}:{columns[4]}:{count}\n")

        if count % 50000 == 0:
            print("Lines written: ", count)
    f.close()
    outFile.close

if __name__ == "__main__":
 #   parser = argparse.ArgumentParser(description='Included methods')
 #   parser.add_argument('-f', '--filepath', help='File path and name, e.g. xx/yy/name.txt')
 #   parser.add_argument('-g', '--guid', help='get guid', type=bool)
 #   parser.add_argument('-a', '--action', help='get action', type=bool)
 #   parser.add_argument('-f', '--found', help='see if action has been found', type=bool)
 #   global args
 #   args = parser.parse_args()

    base_dir = "../../../data/atlasv2/data/benign/h1/cbc-edr"
    output_dir = f"{base_dir}/output"
    file = f'edr-h1-benign'

    convert_file_to_streamspot(file, base_dir)