import re
class hackAssembler():

    def __init__(self):
        self.vardict = {'SP':0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4, 
                        'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, 'R5':5,
                        'R6':6, 'R7':7, 'R8':8, 'R9':9, 'R10':10, 'R11':11,
                        'R12':12, 'R13':13, 'R14':14, 'R15':15, 
                        'SCREEN':16384, 'KBD':24576}
    
        self.next_addr = 16

    def cmd_from_num(self, num):
        binnum = bin(num)[2:]
        # checking bounds!
        if (0 > num) or (num >= 2**15):
            raise Exception("Assembler: out-of-range assignment to A!:  " + line)
        numdigits = min(15, len(binnum))
        numzeros = 16-numdigits
        bincmd='0'*numzeros + binnum[-numdigits:]
        return bincmd

    def is_legal_var_name(self, str):
        if str[0].isdigit():
            return False
        for sym in ['-', '*', '+', '/', '&', '|', '!']:
            if sym in str:
                return False
        else:
            return True

    def handle_a_expr(self, line):
        if line[1:].isdigit():
            decnum = int(line[1:])
            bincmd = self.cmd_from_num(decnum)
        elif self.is_legal_var_name(line[1:]): 
            varname = line[1:]
            if varname in self.vardict.keys():
                addr = self.vardict[varname]
                bincmd = self.cmd_from_num(addr)
            else:
                bincmd = self.cmd_from_num(self.next_addr)
                self.vardict[varname] = self.next_addr;
                self.next_addr += 1;

        else:
            raise Exception("Assembler: illegal variable name:  " + line)

        return [bincmd]



    def segment_c_expr(self, line):
        if '=' in line:
            tokens = line.split('=')
            dest = tokens[0]
            line = tokens[1]
        else:
            dest = None
        if ';' in line:
            tokens = line.split(';')
            expr = tokens[0]
            jump = tokens[1]
        else:
            expr = line
            jump = None
        return (dest, expr, jump)

    def parse_dest(self, dest):
        if dest is None:
            destcmd = '000'
        else:
            destcmd = ''
            if 'A' in dest:
                destcmd = destcmd + '1'
            else:
                destcmd = destcmd + '0'
            if 'D' in dest:
                destcmd = destcmd + '1'
            else:
                destcmd = destcmd + '0'
            if 'M' in dest:
                destcmd = destcmd + '1'
            else:
                destcmd = destcmd + '0'
        return destcmd

    def parse_jump(self, jump):
        if jump is None:
            jumpcmd = '000'
        elif jump == 'JGT':
            jumpcmd = '001'
        elif jump == 'JEQ':
            jumpcmd = '010'
        elif jump == 'JGE':
            jumpcmd = '011'
        elif jump == 'JLT':
            jumpcmd = '100'
        elif jump == 'JNE':
            jumpcmd = '101'
        elif jump == 'JLE':
            jumpcmd = '110'
        elif jump == 'JMP':
            jumpcmd = '111'
        else:
            raise Exception("Assembler: Illegal jump command: " + jump)
        return jumpcmd
    

    def parse_calc(self, calc):
        if calc == '0':
            calccmd = '0101010'
        elif calc == '1':
            calccmd = '0111111'
        elif calc == '-1':
            calccmd = '0111010'
        elif calc == 'D':
            calccmd = '0001100'
        elif calc == 'A':
            calccmd = '0110000'
        elif calc == '!D':
            calccmd = '0001101'
        elif calc == '!A':
            calccmd = '0110001'
        elif calc == '-D':
            calccmd = '0001111'
        elif calc == '-A':
            calccmd = '0110011'
        elif calc == 'D+1' or calc == '1+D':
            calccmd = '0011111'
        elif calc == 'A+1' or calc == '1+A':
            calccmd = '0110111'
        elif calc == 'D-1':
            calccmd = '0001110'
        elif calc == 'A-1':
            calccmd = '0110010'
        elif calc == 'D+A' or calc == 'A+D':
            calccmd = '0000010'
        elif calc == 'D-A':
            calccmd = '0010011'
        elif calc == 'A-D':
            calccmd = '0000111'
        elif calc == 'D&A' or calc == 'A&D':
            calccmd = '0000000'
        elif calc == 'D|A' or calc == 'A|D':
            calccmd = '0010101'
        elif calc == 'M':
            calccmd = '1110000'
        elif calc == '!M':
            calccmd = '1110001'
        elif calc == '-M':
            calccmd = '1110011'
        elif calc == 'M+1' or calc == '1+M':
            calccmd = '1110111'
        elif calc == 'M-1':
            calccmd = '1110010'
        elif calc == 'D+M' or calc == 'M+D':
            calccmd = '1000010'
        elif calc == 'D-M':
            calccmd = '1010011'
        elif calc == 'M-D':
            calccmd = '1000111'
        elif calc == 'D&M' or calc == 'M&D':
            calccmd = '1000000'
        elif calc == 'D|M' or calc == 'M|D':
            calccmd = '1010101'
        else:
            raise Exception("Assembler: illegal calculation: " + calc)
        return calccmd

    def handle_c_expr(self, line):
        dest, calc, jump = self.segment_c_expr(line)
        if calc is None:
            raise Exception("Assembler: c-command must have command: " + line)
        if calc == line:
            raise Exception("Assembler: c-command line must contain '=' or ';' ... " + line)

        destcmd = self.parse_dest(dest)
        jumpcmd = self.parse_jump(jump)
        calccmd = self.parse_calc(calc)
    
        bincmd = '111' + calccmd + destcmd + jumpcmd
        return [bincmd]
    

    def handle_labels(self, inlines):
        outlines = []
        next_line = 0
        for line in inlines:
            if line[0] == '(' and line[-1] == ')':
                labelname = line[1:-1]
                if labelname in self.vardict.keys():
                    raise Exception("Assembler: attempted to add already-existing label: " + line)
                self.vardict[labelname] = next_line
            else:
                next_line += 1
                outlines.append(line)
        return outlines


def clean_file(filename):
    infile = open(filename, 'r')
    cleanlines = []
    for line in infile:
        tokens = re.split(r"//", line)
        cleaned = re.sub("\n|\r|\t| ", "", tokens[0])
        if cleaned != '':
            cleanlines.append(cleaned)
    infile.close()
    return cleanlines


if __name__== "__main__":

    infile = "infile.asm"
    outfile = "outfile.hack"
    cleanlines = clean_file(infile)
    myassembler = hackAssembler()
    codelines = myassembler.handle_labels(cleanlines)

    hackcode = []
    for line in codelines:
        if line[0] == '@':
            cmd = myassembler.handle_a_expr(line)
            hackcode.append(cmd)
        else:
            cmd = myassembler.handle_c_expr(line)
            hackcode.append(cmd)

    outfile = open(outfile, 'w');
    for cmd in hackcode:
        outfile.write(cmd[0] + '\n')
    outfile.close()

