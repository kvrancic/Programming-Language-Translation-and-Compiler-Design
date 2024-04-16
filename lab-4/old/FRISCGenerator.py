input_data = []

while True:
    try:
        line = input().split()
    except EOFError:
        break
    input_data.append(line)

idx = 0
var_count = 0
loop_count = 0
var_declarations = []
op_stack = []
var_addresses = ""
output_file = open("a.frisc", "w+")


def next_var_address():
    global var_count
    var_count += 1
    return "V" + str(var_count - 1)


def assign_variable(var_name, is_loop_var):
    global var_declarations
    for decl in reversed(var_declarations):
        if decl[0] == var_name and not is_loop_var:
            output_file.write("\t\tPOP R0\n")
            output_file.write("\t\tSTORE R0, (" + decl[1] + ")\n")
            return ""
    output_file.write("\t\tPOP R0\n")
    addr = next_var_address()
    output_file.write("\t\tSTORE R0, (" + addr + ")\n")
    return addr


def load_number(num):
    output_file.write("\t\tMOVE %D " + num + ", R0\n")
    output_file.write("\t\tPUSH R0\n")


def handle_operator(op):
    op_cmds = {
        'PLUS': ("\t\tPOP R0\n\t\tPOP R1\n\t\tADD R1, R0, R2\n\t\tPUSH R2\n"),
        'MINUS': ("\t\tPOP R0\n\t\tPOP R1\n\t\tSUB R1, R0, R2\n\t\tPUSH R2\n"),
        'PUTA': "\t\tCALL MUL\n",
        'DIJELI': "\t\tCALL DIV\n"
    }
    output_file.write(op_cmds[op])


def increment_loop_counter(var_name):
    global var_declarations
    for decl in reversed(var_declarations):
        if decl[0] == var_name:
            output_file.write("\t\tLOAD R0, (" + decl[1] + ")\n")
            output_file.write("\t\tADD R0, 1, R0\n")
            output_file.write("\t\tSTORE R0, (" + decl[1] + ")\n")
            break


def compare_loop_counter(var_name, loop_label):
    global var_declarations
    output_file.write("\t\tPOP R0\n")
    for decl in reversed(var_declarations):
        if decl[0] == var_name:
            output_file.write("\t\tLOAD R1, (" + decl[1] + ")\n")
            output_file.write("\t\tCMP R1, R0\n")
            output_file.write("\t\tJP_SLE " + loop_label + "\n")
            break


def check_matching(symbol):
    global idx
    if input_data[idx][0] == symbol:
        idx += 1
        return True
    else:
        return False


def handle_loading_variable(var_name):
    global var_declarations
    for decl in reversed(var_declarations):
        if decl[0] == var_name:
            output_file.write("\t\tLOAD R0, (" + decl[1] + ")\n")
            output_file.write("\t\tPUSH R0\n")
            break


def return_result_to_R6():
    global var_declarations
    for decl in reversed(var_declarations):
        if decl[0] == "rez":
            output_file.write("\t\tLOAD R6, (" + decl[1] + ")\n")
            output_file.write("\t\tHALT\n")
            break


def parse_expression():
    global idx, op_stack

    def P():
        if check_matching("OP_PLUS"):
            op_stack.append("OP_PLUS")
            check_matching("<P>")
            P()
        elif check_matching("OP_MINUS"):
            op_stack.append("OP_MINUS")
            check_matching("<P>")
            P()
        elif check_matching("L_ZAGRADA"):
            check_matching("<E>")
            E()
            check_matching("D_ZAGRADA")
        elif check_matching("IDN"):
            handle_loading_variable(input_data[idx - 1][2])
        elif check_matching("BROJ"):
            load_number(input_data[idx - 1][2])

    def T():
        check_matching("<P>")
        P()
        check_matching("<T_lista>")
        while check_matching("OP_PUTA") or check_matching("OP_DIJELI"):
            op = "PUTA" if input_data[idx - 1][0] == "OP_PUTA" else "DIJELI"
            op_stack.append(op)
            check_matching("<T>")
            T()
            handle_operator(op_stack.pop())

    def E():
        check_matching("<T>")
        T()
        check_matching("<E_lista>")
        while check_matching("OP_PLUS") or check_matching("OP_MINUS"):
            op = "PLUS" if input_data[idx - 1][0] == "OP_PLUS" else "MINUS"
            op_stack.append(op)
            check_matching("<E>")
            E()
            handle_operator(op_stack.pop())

    E()


def parse_loop():
    global idx, loop_count, var_addresses, var_declarations

    check_matching("KR_ZA")
    loop_var_name = input_data[idx][2] if check_matching("IDN") else None
    check_matching("KR_OD")

    check_matching("<E>")
    parse_expression()
    loop_var_addr = assign_variable(loop_var_name, True)
    var_declarations.append([loop_var_name, loop_var_addr])
    var_addresses += loop_var_addr + " DW 0 ; " + loop_var_name + "\n"
    
    loop_label = "L" + str(loop_count)
    loop_count += 1
    output_file.write(loop_label + ":\n")

    check_matching("KR_DO")
    check_matching("<E>")
    parse_expression()

    # Loop body
    if check_matching("<lista_naredbi>"):
        parse_statement_list()

    check_matching("KR_AZ")
    increment_loop_counter(loop_var_name)
    compare_loop_counter(loop_var_name, loop_label)

def parse_assignment():
    global idx, var_addresses, var_declarations
    if check_matching("IDN"):
        var_name = input_data[idx - 1][2]

    check_matching("OP_PRIDRUZI")

    check_matching("<E>")
    parse_expression()

    var_addr = assign_variable(var_name, False)
    if var_addr != "":
        var_declarations.append([var_name, var_addr])
        var_addresses += var_addr + " DW 0 ; " + var_name + "\n"


def parse_statement():
    global idx
    if check_matching("<naredba_pridruzivanja>"):
        parse_assignment()
    elif check_matching("<za_petlja>"):
        parse_loop()


def parse_statement_list():
    if check_matching("$"):
        return
    elif check_matching("<naredba>"):
        parse_statement()
        check_matching("<lista_naredbi>")
        parse_statement_list()


def main_program():
    if check_matching("<program>"):
        if check_matching("<lista_naredbi>"):
            parse_statement_list()


output_file.write("\t\tMOVE 40000, R7 ; init stog\n")
main_program()
return_result_to_R6()
output_file.write(""" 
MD_SGN  MOVE 0, R6
        XOR R0, 0, R0
        JP_P MD_TST1
        XOR R0, -1, R0
        ADD R0, 1, R0
        MOVE 1, R6
MD_TST1 XOR R1, 0, R1
        JP_P MD_SGNR
        XOR R1, -1, R1
        ADD R1, 1, R1
        XOR R6, 1, R6
MD_SGNR RET

MD_INIT POP R4 ; MD_INIT ret addr
        POP R3 ; M/D ret addr
        POP R1 ; op2
        POP R0 ; op1
        CALL MD_SGN
        MOVE 0, R2 ; init rezultata
        PUSH R4 ; MD_INIT ret addr
        RET
        
MD_RET  XOR R6, 0, R6 ; predznak?
        JP_Z MD_RET1
        XOR R2, -1, R2 ; promijeni predznak
        ADD R2, 1, R2
        
MD_RET1 POP R4 ; MD_RET ret addr
        PUSH R2 ; rezultat
        PUSH R3 ; M/D ret addr
        PUSH R4 ; MD_RET ret addr
        RET
        
MUL     CALL MD_INIT
        XOR R1, 0, R1
        JP_Z MUL_RET ; op2 == 0
        SUB R1, 1, R1
        
MUL_1   ADD R2, R0, R2
        SUB R1, 1, R1
        JP_NN MUL_1 ; >= 0?
        
MUL_RET CALL MD_RET
        RET
        
DIV     CALL MD_INIT
        XOR R1, 0, R1
        JP_Z DIV_RET ; op2 == 0
        
DIV_1   ADD R2, 1, R2
        SUB R0, R1, R0
        JP_NN DIV_1
        SUB R2, 1, R2
        
DIV_RET CALL MD_RET
        RET
""")
output_file.write(var_addresses)
output_file.close()
