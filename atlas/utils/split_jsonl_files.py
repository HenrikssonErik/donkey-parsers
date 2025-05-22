import json
import numpy as np

input_file = '../../../../data/atlasv2/data/benign/h2/cbc-edr/edr-h2-benign.jsonl'
output_file = '../../../../data/atlasv2/data/benign/h2/cbc-edr/split/edr-h2-benign'

number_of_files = 8
if __name__ == "__main__":
    records = [] 
    with open(input_file, 'r') as inf:
        for line in inf:
            atlas_record = json.loads(line)
            records.append(atlas_record)
    print("appended")
    
    sorted_records = sorted(records, key=lambda record: record['device_timestamp'])
    sorted_records_list = np.array_split(sorted_records, number_of_files)
    print("sorted")
    
    r_count = 0
    for record_list in sorted_records_list:
        tmp_out = f'{output_file}-{r_count}.jsonl'

        with open(tmp_out, 'w+') as of:
            for record in record_list:
                jout = json.dumps(record) + '\n'
                of.write(jout)
        r_count += 1     
    print("written")


