import argparse
import os
import sys
import jinja2
from jinja2 import Template
from reg_mappings import miscreg_map
from reg_mappings import intreg_list


def parse_args(inp_args):
    parser = argparse.ArgumentParser(description='Script to generate register info in m5 checkpoint form')

    parser.add_argument('--gdb-reg-info',type=str, required=True,
            help='Output dump file of info registers all command from gdb')

    parser.add_argument('--dev-info',type=str, required=True,
            help='Output dump file of info registers all command from gdb')

    parser.add_argument('--m5-miscreg-info',type=str, required=True,
            help='List of registers in gem5 in each line as appears in misreg header file')

    parser.add_argument('--out-reg-info',type=str, required=True,
            help='Output file')

    parser.add_argument('--m5-template',type=str, required=True,
            help='m5ckpt template file')

    parser.add_argument('--num-cpus',type=int, required=True,
            help='Number of cpu cores')

    args = parser.parse_args(inp_args)
    return args

def parse_reg_info(fname):
    reg_info_file = open(fname, 'r')
    reg_map = dict()

    for line in reg_info_file:
        toks = line.split()

        #Int and Misc registers
        if len(toks) == 3:
            reg_name = toks[0].lower()

            reg_val = int(toks[1],16)
            reg_map[reg_name] = reg_val

        #Else FP registers
        elif line.startswith('q'):
            reg_name = toks[0].lower()
            reg_val_toks = toks[3].split(',')
            reg_val = int(reg_val_toks[0],16)
            reg_map[reg_name] = reg_val

    return reg_map

def parse_dev_info(fname, reg_map):
    dev_info = open(fname, 'r')

    for line in dev_info:
        print(line)
        toks = line.split()

        name = toks[0]
        reg_map[name] = toks[1]

def reverse_byte_order(hex_str):
    assert (len(hex_str) == 512)

    rev_str = ''
    for i in range(255,0,-1):
        rev_str += hex_str[2*i : 2*i + 2]

    return rev_str


def get_fpreg_string(reg_map):

    #Total 43 Vec registers in gem5
    #Length of each register is 256 bytes
    TOTAL_REGS = 43
    NUM_FPREGS = 32

    fp_regs = list()
    #q0-q31 2048 bit registers or 256 bytes registers
    for i in range (NUM_FPREGS):
        reg = f'q{i}'
        reg_val = reg_map[reg]
        fp_regs.append(reg_val)

    FILLER_LEN = TOTAL_REGS -  NUM_FPREGS

    filler = [0 for i in range(FILLER_LEN)]

    fp_regs = fp_regs + filler

    fp_regs_hex_list = [ reverse_byte_order('{:0512x}'.format(v))  for v in fp_regs ]

    return ' '.join(fp_regs_hex_list)


def get_intreg_string(reg_map):

    #Total 43 registers in gem5
    TOTAL_REGS = 43
    SP_REGS = 4
    NUM_XREGS = len(intreg_list)

    int_regs = list()
    #x0-x30 31 64bit
    for reg in intreg_list:
        reg_val = 0
        if reg != '0':
          reg_val = reg_map[reg]
        int_regs.append(reg_val)

    FILLER_LEN = TOTAL_REGS - SP_REGS - NUM_XREGS

    filler = [0 for i in range(FILLER_LEN)]

    int_regs = int_regs + filler

    # SP_EL0 : 39
    # SP_EL1 : 40
    # SP_EL2 : 41
    # SP_EL3 : 42
    for el_level in range(SP_REGS):
        reg = f'sp_el{el_level}'

        if reg in reg_map.keys():
            reg_val = reg_map[reg]
        else:
            reg_val = 0

        int_regs.append(reg_val)

    return " ".join(map(str,int_regs))

def get_cc_reg_string(cpsr):
    NZCV = cpsr >> 28
    NZ = NZCV >> 2
    C = (NZCV >> 1 ) & 0x01
    V = (NZCV) & 0x01
    cc_reg_string = '{} {} {} 0 0 0'.format(NZ,C,V)
    print("cc_reg_string is "+cc_reg_string)
    return cc_reg_string

def get_miscreg_output(miscreg_ref_fname, out_fname, reg_map):
    miscreg_fd = open(miscreg_ref_fname, 'r')
    out_fg = open(out_fname, 'w')

    miscreg_string = ''
    for line in miscreg_fd:
        toks = line.split('=')
        reg_name = toks[0]
        reg_val = toks[1].strip()

        #Use the value from reg_map if present
        if reg_name in reg_map.keys():
            reg_val = reg_map[reg_name]

        elif reg_name in miscreg_map.keys() and \
             miscreg_map[reg_name] in reg_map.keys():
            reg_val = reg_map[miscreg_map[reg_name]]

        else:
            print(f'{reg_name} not in reg_map')
            pass

        #out_fg.write(f'{reg_name}={reg_val}\n')
        miscreg_string += f'{reg_name}={reg_val}\n'

    return miscreg_string

def fix_sp_regs(reg_map):
    #Add any register correction code here

    #Since the Execption Level we are in is
    #EL1 SP_EL1 corresponds to SP so replace
    #it here
    #TODO: Add Exception Level Check before
    #actually making the change
    if (int(reg_map['cpsr'])%2 == 0):
        reg_map['sp_el0'] = reg_map['sp']
    else:
        reg_map['sp_el1'] = reg_map['sp']

    #Fixing MAIR register which is saved
    #as two 32bit registers mair_el1 and
    #nmrr_ns registers in gem5

    mair_reg = int(reg_map['mair_el1'])
    reg_map['nmrr_ns'] = mair_reg >> 32


def gen_m5cpt(cli_args):
    args = parse_args(cli_args)
    print(os.path.abspath(__file__))
    cur_file_abspath = os.path.abspath(__file__)
    parent_dir_name = os.path.dirname(cur_file_abspath)
    args.m5_template = os.path.join(parent_dir_name, "templates",  args.m5_template)
    args.m5_miscreg_info = os.path.join(parent_dir_name, args.m5_miscreg_info)
    print(args.m5_template)
    if args.num_cpus == 1:
        reg_map = parse_reg_info(args.gdb_reg_info)
        parse_dev_info(args.dev_info, reg_map)
        fix_sp_regs(reg_map)

        miscreg_str = get_miscreg_output(args.m5_miscreg_info, args.out_reg_info, reg_map)
        intreg_str =  get_intreg_string(reg_map)
        fpreg_str = get_fpreg_string(reg_map)
        ccreg_str = get_cc_reg_string(reg_map['cpsr'])

        pc = reg_map['pc']
        npc = pc + 4

        #Generate the checkpoint file using jinja2 template file
        print(reg_map)
        subs = jinja2.Environment(
                      loader=jinja2.FileSystemLoader('/')
                      ).get_template(args.m5_template).render(
                          pc = pc,
                          npc = npc,
                          miscreg_string = miscreg_str,
                          intreg_string = intreg_str,
                          fpreg_string = fpreg_str,
                          ccreg_string = ccreg_str,
                          reg_map = reg_map
                      )
        # lets write the substitution to a file
        with open(args.out_reg_info,'w') as f: f.write(subs)
    else:
        reg_map = [None for i in range(0,args.num_cpus)]
        miscreg_str = [None for i in range(0,args.num_cpus)]
        intreg_str = [None for i in range(0,args.num_cpus)]
        fpreg_str = [None for i in range(0,args.num_cpus)]
        ccreg_str = [None for i in range(0,args.num_cpus)]
        pc = [None for i in range(0,args.num_cpus)]
        npc = [None for i in range(0,args.num_cpus)]


        for i in range(0, args.num_cpus):
            reg_map[i] = parse_reg_info(args.gdb_reg_info + "." + str(i+1))
            fix_sp_regs(reg_map[i])

            miscreg_str[i] = get_miscreg_output(args.m5_miscreg_info, args.out_reg_info, reg_map[i])
            intreg_str[i] =  get_intreg_string(reg_map[i])
            fpreg_str[i] = get_fpreg_string(reg_map[i])
            ccreg_str[i] = get_cc_reg_string(reg_map[i]['cpsr'])

            pc[i] = reg_map[i]['pc']
            npc[i] = pc[i] + 4

        #Generate the checkpoint file using jinja2 template file
        print(reg_map)
        subs = jinja2.Environment(
                      loader=jinja2.FileSystemLoader('/')
                      ).get_template(args.m5_template).render(
                          pc = pc,
                          npc = npc,
                          miscreg_string = miscreg_str,
                          intreg_string = intreg_str,
                          fpreg_string = fpreg_str,
                          ccreg_string = ccreg_str,
                          reg_map = reg_map,
                          num_cpus = args.num_cpus
                      )
        # lets write the substitution to a file
        with open(args.out_reg_info,'w') as f: f.write(subs)

if __name__ == '__main__':
    #Parse Command line argunments first
    print(sys.argv)
    gen_m5cpt(sys.argv[1:])


