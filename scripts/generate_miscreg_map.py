import sys


def get_reg(cstr):
    toks = cstr.split('MISCREG_')
    reg = toks[-1].split(')')[0]
    #print(reg.lower())
    return reg.lower()

miscreg_cfile = open(sys.argv[1],'r')

reg_str=''
mapsto_str=''
miscreg_map = dict()
for line in miscreg_cfile:
    if 'InitReg' in line:
        #print(line.strip())
        temp_reg_str = line.strip()
        reg_str = get_reg(temp_reg_str)
    if 'mapsTo' in line:
        #print(line.strip())
        temp_mapsto_str = line.strip()
        mapsto_str = get_reg(temp_mapsto_str)
        #print(f'{reg_str}:{mapsto_str}')
        if not (reg_str.endswith('12')) :
            if mapsto_str in miscreg_map.keys():
                print(f"KEY already present {mapsto_str}:{miscreg_map[mapsto_str]}")
            miscreg_map[mapsto_str] = reg_str
        else:
            print(f'{reg_str}:{mapsto_str}')

print(miscreg_map)
for reg in miscreg_map:
    reg_dst = miscreg_map[reg]

    if reg_dst in miscreg_map.keys():
        print(f'{reg}:{reg_dst}:{miscreg_map[reg_dst]}')
