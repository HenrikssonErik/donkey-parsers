import os, argparse

def main():
    parser = argparse.ArgumentParser(description='Rename files in a directory')
    parser.add_argument('-s', '--source', help='Input data folder', required=True)
    parser.add_argument('-n', '--name', help='Base name', choices=['cadets', 'clearscope', 'fivedirections', 'theia', 'trace'], required=True)
    parser.add_argument('-o', '--output', help='Output data filename', required=True)
    parser.add_argument('-e,', '--ending', help='File ending .eg., .txt ')
    parser.add_argument('-l', '--length', help='Number of files in the directory')

    args = vars(parser.parse_args())

    input_source = args['source']
    name = args['name']
    output_locat = args['output']
    ending = args['ending']
    directory = os.fsencode(input_source)
    count = 0
    for file in os.listdir(directory):
        filename = f"{input_source}/{file.decode()}"
        if name in filename: # (file.endswith(f".{ending}") or file.endswith(ending)): 
            os.rename(filename, f'{output_locat}.{count}')
            count += 1   
        else:
            continue

if __name__ == "__main__":
    main()