import argparse
import sys
import os

def parse_args(inp_args):
    parser = argparse.ArgumentParser(description='Script to generate register info in m5 checkpoint form')

    parser.add_argument('--skip-bytes',type=str, required=True, default="0x470",
            help='Output dump file of info registers all command from gdb')

    parser.add_argument('--input-elf',type=str, required=True,
            help='List of registers in gem5 in each line as appears in misreg header file')

    parser.add_argument('--out-file',type=str, required=True,
            help='Output file')

    args = parser.parse_args(inp_args)
    return args

def gen_file(args):
    input_elf_file = args.input_elf
    output_file = args.out_file

    skip = int(args.skip_bytes,16)

    input_fd = open(input_elf_file, 'rb')
    output_fd = open(output_file, 'wb')

    #Skip from input file
    input_fd.read(skip)

    while True:
        chunk = input_fd.read(4096)
        if not chunk:
            break
        output_fd.write(chunk)

    output_fd.close()
    input_fd.close()


def gen_physmem(cli_args):
    args = parse_args(cli_args)
    gen_file(args)


if __name__ == '__main__':
    #Parse Command line argunments first
    gen_physmem(sys.argv[1:])

