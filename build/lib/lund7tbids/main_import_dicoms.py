import argparse

def parse_inputs():
    parser = argparse.ArgumentParser(description='Import DICOMS')
    parser.add_argument('--dicom_dir', help='DICOM directory', type=str)
    parser.add_argument('--id', help='Subject ID', type=str)
    parser.add_argument('--key', help='Study key', type=str)
    parser.add_argument('-v', help='Verbose output')
    args = parser.parse_args()

    return args

def main():
    args = parse_inputs()
    dicom_dir = args.dicom_dir
    subj_id = args.id
    study_key = args.key
    verbose = args.v

    print(args)

if __name__ == '__main__':
    main()