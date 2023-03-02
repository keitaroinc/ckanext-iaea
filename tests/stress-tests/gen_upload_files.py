from random import randint
from argparse import ArgumentParser


def rand_str(size):
    s = ''
    for _ in range(size):
        s += chr(randint(ord('A'), ord('Z')))
    return s


def gen_csv_file(filename, col_number, file_size):
    columns = [(lambda: rand_str(5)) if randint(0,1) else (lambda: str(randint(1000, 2000))) for _ in range(col_number)]
    content_size = 0
    row_count = 0
    with open(filename, mode='w+') as f:
        while content_size < file_size:
            row = ','.join([fn() for fn in columns]) + '\n'
            content_size += len(row)
            row_count += 1
            f.write(row)
    print '{}, size: {}, rows: {}'.format(filename, content_size, row_count)


def gen_files(file_prefix, num_files, col_number, file_size):
    for i in range(num_files):
        file_name = '{}_{}.csv'.format(file_prefix, i+1)
        gen_csv_file(file_name, col_number, file_size)

if __name__ == '__main__':
    parser = ArgumentParser(description='Generate random CSV files.')
    parser.add_argument('--file-prefix', type=str, dest='file_prefix', default='/tmp/csv_file', help='Files prefix.')
    parser.add_argument('--file-size', type=int, dest='file_size', default=10*1024*1024, help='Total size of the file.')
    parser.add_argument('--columns', type=int, dest='col_number', default=20, help='Number of columns')
    parser.add_argument('--files-count', type=int, dest='num_files', default=10, help='Number of files to generate')

    args = parser.parse_args()

    gen_files(args.file_prefix, args.num_files, args.col_number, args.file_size)


        