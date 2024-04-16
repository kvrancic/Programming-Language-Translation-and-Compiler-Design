import sys

KEYWORDS = ["za", "od", "do", "az"]
OPERATORS = ['+', '-', '*', '/', '(', ')', '=']

# Function definitions
def obrada(lines):
    i = 1

    for i in range (1, len(lines)+1):
        line = lines[i - 1]
        
        #preskoci komentar
        if line.startswith("//"):
            continue

        #ukloni komentar
        if "//" in line: 
            line = line.split("//")[0]

        
        parts = line.split()
        for part in parts: 
            if part == "za":
                    print(f"KR_ZA {i} {part}")
            elif part == "od":
                print(f"KR_OD {i} {part}")
            elif part == "do":
                print(f"KR_DO {i} {part}")
            elif part == "az":
                print(f"KR_AZ {i} {part}")
            elif part.startswith("-") and part[1:].isdigit():
                print(f"OP_MINUS {i} -")
                print(f"BROJ {i} {part[1:]}")
            else:
                curr_number = ""
                curr_variable = ""
                for c in part: 
                    if c.isalpha() or (c.isdigit() and curr_variable):
                        #imamo ime varijable 

                        # vidi je li do sad bio neki broj 
                        if curr_number:
                            print(f"BROJ {i} {curr_number}")
                            curr_number = ""
                        
                        curr_variable += c
                    
                    elif c.isdigit() and not curr_variable: 
                        # imamo broj 
                        curr_number += c
                    
                    elif c in OPERATORS: 
                        if curr_number:
                            print(f"BROJ {i} {curr_number}")
                            curr_number = ""
                        if curr_variable: 
                            print(f"IDN {i} {curr_variable}")
                            curr_variable = ""
                        if c=="=":
                            print(f"OP_PRIDRUZI {i} {c}")
                        if c=="+":
                            print(f"OP_PLUS {i} {c}")
                        elif c=="-":
                            print(f"OP_MINUS {i} {c}")
                        elif c=="*":
                            print(f"OP_PUTA {i} {c}")
                        elif c=="/":
                            print(f"OP_DIJELI {i} {c}")
                        elif c=="(":
                            print(f"L_ZAGRADA {i} {c}")
                        elif c==")":
                            print(f"D_ZAGRADA {i} {c}")
                    
                if curr_number:
                    print(f"BROJ {i} {curr_number}")
                    curr_number = ""
                if curr_variable: 
                    print(f"IDN {i} {curr_variable}")
                    curr_variable = ""




def main():
    lines = []
    for line in sys.stdin:
        lines.append(line)

    obrada(lines)


if __name__ == "__main__":
    main()
