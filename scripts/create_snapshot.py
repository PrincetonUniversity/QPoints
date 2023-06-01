import argparse
import sys
import os
from telnetlib import Telnet
import subprocess
import time

import parse_reg_info
import gen_mem_file

def parse_args():
    parser = argparse.ArgumentParser(description='Script to generate Full System Snapshot to be used with gem5 simulator')

    parser.add_argument('--m1',  default=False,
            action='store_true',
            help='Set this flag if snapshot is collected on m1 mac')

    parser.add_argument('--multi',  default=False,
            action='store_true',
            help='Set this flag to collect multi core snapshot')

    parser.add_argument('--skip-dump',  default=False,
            action='store_true',
            help='Flag to skip the first part of snapshot collection process')

    parser.add_argument('--disk-image',type=str, required=True,
            help='Disk image file name')

    parser.add_argument('--dest-dir',type=str, required=True,
            help='Destination directory to save snapshot files')

    parser.add_argument('--copy-disk-img', default=False,
            action='store_true',
            help='Flag to enable disk image copy')

    args = parser.parse_args()
    return args

def extract_addr(inp_byte_str):
  inp_str = inp_byte_str.decode('utf-8')
  toks=inp_str.split('\n')
  addr = toks[1].split()[-1]
  addr = int(addr,base=16)
  addr = addr << 12
  return addr

def extract_value(inp_byte_str):
  #Decode the input byte string
  inp_str = inp_byte_str.decode('utf-8')
  lines=inp_str.split('\n')
  toks = lines[1].split()
  last_tok = toks[-1]
  addr = int(last_tok,base=16)
  return addr

def run_gdb_on_docker(args):

  script_file = 'gdb.script'

  if args.multi:
    script_file = 'gdb.script.multi'

  #cmd = '''docker run \
  #             --rm -v$(pwd)/gdb_scripts:/tools \
  #             -v$(pwd)/{}:/tools/ckpt_dir \
  #             --privileged  --net host ubuntu-gdb \
  #             sh -c "cd /tools/ckpt_dir; gdb-multiarch -x /tools/{}"
  #       '''.format(args.dest_dir, script_file)
  #print(cmd)
  
  cwd = os.getcwd()
  cmd = 'cd {}; gdb-multiarch -x /qpoints/scripts/gdb_scripts/{}; cd {}'.format(args.dest_dir, script_file, cwd)


  proc = subprocess.Popen(
          [cmd],
          stdout=subprocess.PIPE,
          stdin=subprocess.PIPE,
          stderr=subprocess.PIPE,
          shell=True
          )
  proc.stdin.write(b"quit\n")
  proc.stdin.write(b"y\n")
  proc.stdin.flush()
  proc.wait()



def run_gdb_process_test():
  proc = subprocess.Popen(
          ['gdb-multiarch -x gdb.script'],
          stdout=subprocess.PIPE,
          stdin=subprocess.PIPE,
          stderr=subprocess.PIPE,
          shell=True
          )
  proc.stdin.write(b"quit\n")
  proc.stdin.write(b"y\n")
  proc.stdin.flush()
  proc.wait()

def run_gdb_process():
  proc = subprocess.Popen(
          ['gdb-multiarch'],
          stdout=subprocess.PIPE,
          stdin=subprocess.PIPE,
          stderr=subprocess.PIPE,
          shell=True
          )
  proc.stdin.write(b"help\n")
  proc.stdin.flush()
  proc.stdin.write(b"target remote localhost:1234\n")
  proc.stdin.flush()
  proc.stdin.write(b"set pagination off\n")
  proc.stdin.flush()
  proc.stdin.write(b"set logging file reg_info_test.virtio\n")
  proc.stdin.flush()
  proc.stdin.write(b"set logging on\n")
  proc.stdin.flush()
  proc.stdin.write(b"info registers all\n")
  proc.stdin.flush()
  proc.stdin.write(b"set logging off\n")
  proc.stdin.flush()
  proc.stdin.write(b"quit\n")
  proc.stdin.write(b"y\n")
  proc.stdin.flush()
  proc.wait()
  #print(proc.communicate(timeout=5))
  return proc

def copy_disk_image(dest_dir, disk_image):
  proc = subprocess.Popen(
          ['cp',disk_image,dest_dir],
          stdout=subprocess.PIPE)
  proc.wait()

def move_file_dest_dir(dest_dir, fname):
  if not os.path.exists(fname):
      print("{} doesnot exist".format(fname))
      return
  proc = subprocess.Popen(
          ['mv',fname,dest_dir],
          stdout=subprocess.PIPE)
  proc.wait()


def dump_to_file(fname, value_map):
    fh = open(fname,'a')
    for key in value_map.keys():
        fh.write('{} {} {}\n'.format(key, hex(value_map[key]), value_map[key]))

def dump_disk_dev_info(tn, dest_dir, fname):
  out_file = os.path.join(dest_dir, fname)
  fh= open(out_file, 'w')

  tn.write(b"xp /xw 0xa003e40\n")
  inp=tn.read_until(b"(qemu)")
  print(inp.decode('utf-8'))
  addr = extract_addr(inp)
  vio_base = hex(addr)
  addr = addr + 0x4002
  addr = hex(addr)
  type(addr)
  tn.write(b"xp /xw "+ addr.encode('ascii') + b"\n")
  inp=tn.read_until(b"(qemu)")

  OFFSET_MASK = ( 1 << 16) - 1
  print("offset",inp.decode('utf-8'))
  offset_val = extract_addr(inp)
  print("offse_val", offset_val)
  offset = offset_val & OFFSET_MASK

  print(offset)
  fh.write("vio_base {}\n".format(vio_base))
  fh.write("queue0_offset {}\n".format(offset))

  fh.close()

def collect_snapshot(args):
  host="localhost"
  
  # Hack for M1 Mac
  if args.m1:
    host="host.docker.internal"

  port="45454"
  tn = Telnet(host, port)

  inp=tn.read_until(b"(qemu)")
  tn.write(b"stop\n")
  inp=tn.read_until(b"(qemu)")
  tn.write(b"commit all\n")
  inp=tn.read_until(b"(qemu)")

  tn.write(b"commit all\n")
  inp=tn.read_until(b"(qemu)")

  if args.copy_disk_img:
    copy_disk_image(dest_dir = args.dest_dir,
            disk_image = args.disk_image)

  #tn.write(bytes("dump-guest-memory {}/physmem.elf\n".format(os.path.abspath(args.dest_dir)), 'ascii'))
  tn.write(bytes("dump-guest-memory physmem.elf\n", 'ascii'))
  inp=tn.read_until(b"(qemu)")

  dump_disk_dev_info(tn, args.dest_dir, "dev.info")

  move_file_dest_dir(dest_dir = args.dest_dir,
          fname = '/qpoints/physmem.elf')
  #Start gdb server
  tn.write(b"gdbserver\n")
  inp=tn.read_until(b"(qemu)")

  #run_gdb_process_test()
  run_gdb_on_docker(args)
  time.sleep(2)
  #move_file_dest_dir(dest_dir = args.dest_dir,
  #        fname = 'reg_info.virtio')

def process_snapshot(args):
    reg_info_fname = "{}/reg_info.virtio".format(args.dest_dir)
    reg_info_args = []

    reg_info_args.append('--gdb-reg-info')
    reg_info_args.append(reg_info_fname)

    reg_info_args.append('--num-cpus')
    reg_info_args.append('1')

    reg_info_args.append('--m5-miscreg-info')
    reg_info_args.append('gem5_misc_regs')

    reg_info_args.append('--out-reg-info')
    reg_info_args.append('{}/m5.cpt'.format(args.dest_dir))

    reg_info_args.append('--m5-template')
    if args.m1:
        reg_info_args.append('m5.cpt.gicv2.template')
    else:
        reg_info_args.append('m5.cpt.template')

    parse_reg_info.gen_m5cpt(reg_info_args)

    #--skip-bytes=0x470 --input-elf=/scratch/bgodala/qemu_workspace/qemu_local_kernel_build/finagle-http/physmem.elf --out-file=/scratch/bgodala/qemu_workspace/qemu_local_kernel_build/finagle-http/physmem
    #mem_conv_args = ['--skip-bytes=0x830', '--input-elf={}/physmem.elf'.format(args.dest_dir),
    mem_conv_args = ['--skip-bytes=0x470', '--input-elf={}/physmem.elf'.format(args.dest_dir),
            '--out-file={}/physmem'.format(args.dest_dir)]

    gen_mem_file.gen_physmem(mem_conv_args)



if __name__ == "__main__":
    args = parse_args()


    if not args.skip_dump:
        if os.path.exists(args.dest_dir):
            # Donot run the script if dest dir exists
            print("Dest direscoty  {} already exists.\n"
                    "Please delete it and try again.".format(args.dest_dir))
            sys.exit()

        #Create the directory
        os.mkdir(args.dest_dir)

        collect_snapshot(args)

    process_snapshot(args)
