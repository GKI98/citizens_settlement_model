import argparse
from scripts import main_file


def main():
    parser = argparse.ArgumentParser(prog='CLI-parser', description='')

    # Group_1 "Reading/Saving data"
    parser_saver = parser.add_argument_group(title='Reading options')
    parser_saver.add_argument('--folder-path', '--p', dest='path', nargs='?', const=0, default='./outputs', help='Path to read files')

    args = parser.parse_args()
    main_file.main(args)


if __name__ == '__main__':
    main()
