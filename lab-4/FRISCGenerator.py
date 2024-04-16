import sys

class FRISCGenerator:
    def __init__(self):
        self.test = Grmilica()


class Grmilica:
    def __init__(self):
        self.reader = sys.stdin
        self.writer = open("a.frisc", "w")
        self.variable_list = [{}]
        self.line_curr = ""
        self.line_num = 0
        self.depth = 0
        self.issue = None
        self.vars = {}
        self.counter = 0
        self.var_sign = ""
        self.write_increment = False
        self.label_not_added = True
        self.var_petlja = ""
        self.mul_div = False
        self.add_op = False
        self.sub_op = False
        self.mul_op = False
        self.div_op = False

        self.writer.write("    MOVE %D 40000, r7\n")

        pass_var = True
        if not self.read_next_line():
            pass_var = False

        while self.get_next_line() is not None and pass_var:
            if self.line_curr == "<naredba_pridruzivanja>":
                if not self.pridruzivanje():
                    pass_var = False
            elif self.line_curr == "<za_petlja>":
                if not self.za_loop():
                    pass_var = False

        if not pass_var and self.issue is not None:
            # Handle error
            pass

        self.writer.write("    POP r0\n")
        self.writer.write("    STORE r0, (" + self.vars.get("rez") + ")\n")
        self.writer.write("    LOAD r6, (" + self.vars.get("rez") + ")\n")
        self.writer.write("    HALT\n\n")

        for value in self.vars.values():
            self.writer.write(value + "  DW 0\n")
        self.writer.write("DO  DW 0\n\n")

        if self.mul_div:
            self.write_mul_div()

        self.writer.flush()
        self.writer.close()

    def za_loop(self):
        # Implementation of za_petlja
        self.variable_list.insert(self.depth + 1, {})
        if not self.read_next_lines(2):
            return False

        k = self.read_var_name() + "PETLJA"
        self.var_petlja = k
        v = str(self.line_num)
        self.vars.setdefault(k, "V" + str(self.counter))
        self.counter += 1
        self.write_increment = True

        line_no_comp = self.line_num
        job_not_done = True

        od = False
        do = False
        while True:
            if not self.read_next_line():
                return False

            if line_no_comp == self.line_num and "KR_OD" in self.line_curr:
                od = True
            if line_no_comp == self.line_num and "KR_DO" in self.line_curr:
                do = True

            if line_no_comp == self.line_num and "IDN" in self.line_curr:
                var = self.read_var_name()
                self.writer.write("    LOAD r0, (" + self.vars.get(var) + ")\n")
                if od:
                    self.writer.write("    STORE r0, (" + self.vars.get(k) + ")\n")
                    od = False
                if do:
                    self.writer.write("    STORE r0, (DO)\n")
                    do = False
                if var == k:
                    self.issue = var
                    return False

            if "OP_MINUS" in self.line_curr:
                self.var_sign = "-"

            if line_no_comp == self.line_num and "BROJ" in self.line_curr:
                var = self.read_var_name()
                self.writer.write("    MOVE %D " + self.var_sign + var + ", r0\n")
                self.var_sign = ""
                if od:
                    self.writer.write("    STORE r0, (" + self.vars.get(k) + ")\n")
                    od = False
                if do:
                    self.writer.write("    STORE r0, (DO)\n")
                    do = False

            if self.line_num != line_no_comp and job_not_done:
                self.variable_list[self.depth][k] = v
                job_not_done = False

            if self.line_curr.startswith("KR_AZ"):
                break

            if self.line_curr == "<naredba_pridruzivanja>":
                if not self.pridruzivanje():
                    return False
            elif self.line_curr == "<za_petlja>":
                if not self.za_loop():
                    return False
            else:
                if "IDN" in self.line_curr:
                    if not self.var_check():
                        return False

        self.depth -= 1
        return True

    def pridruzivanje(self):
        # Implementation of naredba_pridruzivanja
        if not self.read_next_line():
            return False
        k = self.read_var_name()
        v = str(self.line_num)
        self.vars.setdefault(k, "V" + str(self.counter))
        self.counter += 1

        if not self.read_next_line():
            return False
        row_no = self.line_num
        while row_no == self.line_num:
            if not self.read_next_line():
                return False

            if "<P>" in self.line_curr:
                self.read_next_line()
                if "OP_MINUS" in self.line_curr:
                    self.var_sign = "-"

            if "BROJ" in self.line_curr or "IDN" in self.line_curr:
                if "BROJ" in self.line_curr:
                    self.writer.write("    MOVE %D " + self.var_sign + self.read_var_name() + ", r0\n")
                    self.writer.write("    STORE r0, (" + self.vars.get(k) + ")\n")
                    self.var_sign = ""
                else:
                    var_name = self.read_var_name()
                    var = self.var_petlja if self.var_petlja and var_name.startswith(self.var_petlja[0]) else var_name
                    if self.write_increment and self.label_not_added:
                        self.writer.write("L0")
                        self.label_not_added = False
                    self.writer.write("    LOAD r0, (" + self.vars.get(var) + ")\n")
                self.writer.write("    PUSH r0\n")
                if self.add_op or self.sub_op:
                    # Specific logic related to add and sub operations
                    self.read_next_lines(2)
                    if not "$" in self.line_curr:
                        if "OP_PUTA" in self.line_curr:
                            self.mul_op = True
                        if "OP_DIJELI" in self.line_curr:
                            self.div_op = True
                        while not "<P>" in self.line_curr:
                            self.read_next_line()
                        self.read_next_line()
                        if "BROJ" in self.line_curr:
                            self.writer.write("    MOVE %D " + self.read_var_name() + ", r0\n")
                        else:
                            if not self.var_check() or not self.read_var_name():
                                return False
                            self.writer.write("    LOAD r0, (" + self.vars.get(self.read_var_name()) + ")\n")
                        self.writer.write("    PUSH r0\n")
                        self.mul_div_op()
                    self.add_sub_op(k)
                    if self.write_increment:
                        self.test_increm()

                if self.mul_op or self.div_op:
                    self.mul_div_op()

            if "<E_lista>" in self.line_curr:
                self.read_next_line()
                if "OP_PLUS" in self.line_curr:
                    self.add_op = True
                if "OP_MINUS" in self.line_curr:
                    self.sub_op = True

            if "<T_lista" in self.line_curr:
                self.read_next_line()
                if "OP_PUTA" in self.line_curr:
                    self.mul_op = True
                if "OP_DIJELI" in self.line_curr:
                    self.div_op = True

        no_key = all(not d.get(k) for d in self.variable_list[:self.depth + 1])
        if no_key:
            self.variable_list[self.depth][k] = v

        return True

    def test_increm(self):
        self.writer.write("    LOAD R0, (" + self.vars.get(self.var_petlja) + ")\n")
        self.writer.write("    ADD R0, 1, R0\n")
        self.writer.write("    STORE R0, (" + self.vars.get(self.var_petlja) + ")\n")
        self.writer.write("    LOAD R0, (" + self.vars.get(self.var_petlja) + ")\n")
        self.writer.write("    LOAD R1, (DO)\n")
        self.writer.write("    CMP R0, R1\n")
        self.writer.write("    JP_SLE L0\n")
        self.write_increment = False

    def var_check(self):
        variable_name = self.read_var_name()
        return self.check_variable_in_scopes(variable_name)

    def check_variable_in_scopes(self, variable_name):
        # Check if the variable exists in the current scope or any parent scope
        for depth_level in range(self.depth, -1, -1):
            if variable_name in self.variable_list[depth_level]:
                return True  # Variable found in the current or a parent scope
        # Variable not found, set the issue to the variable name
        self.issue = variable_name
        return False

    def add_sub_op(self, k):
        self.writer.write("    POP r1\n")
        self.writer.write("    POP r0\n")
        operation = "ADD" if self.add_op else "SUB"
        self.writer.write(f"    {operation} r0, r1, r2\n")
        self.writer.write("    PUSH r2\n")
        self.writer.write("    STORE r2, (" + self.vars.get(k) + ")\n")
        self.add_op = self.sub_op = False

    def mul_div_op(self):
        self.writer.write("    CALL " + ("MUL" if self.mul_op else "DIV") + "\n")
        self.mul_op = self.div_op = False
        self.mul_div = True

    def write_mul_div(self):
        self.writer.write("MD_SGN MOVE 0, R6\n")
        self.writer.write("   XOR R0, 0, R0\n")
        self.writer.write("   JP_P MD_TST1\n")
        self.writer.write("   XOR R0, -1, R0\n")
        self.writer.write("   ADD R0, 1, R0\n")
        self.writer.write("   MOVE 1, R6\n")
        self.writer.write("MD_TST1 XOR R1, 0, R1\n")
        self.writer.write("   JP_P MD_SGNR\n")
        self.writer.write("   XOR R1, -1, R1\n")
        self.writer.write("   ADD R1, 1, R1\n")
        self.writer.write("   XOR R6, 1, R6\n")
        self.writer.write("MD_SGNR RET\n")
        self.writer.write("MD_INIT POP R4\n")
        self.writer.write("   POP R3\n")
        self.writer.write("   POP R1\n")
        self.writer.write("   POP R0\n")
        self.writer.write("   CALL MD_SGN\n")
        self.writer.write("   MOVE 0, R2\n")
        self.writer.write("   PUSH R4\n")
        self.writer.write("   RET\n")
        self.writer.write("MD_RET XOR R6, 0, R6\n")
        self.writer.write("   JP_Z MD_RET1\n")
        self.writer.write("   XOR R2, -1, R2\n")
        self.writer.write("   ADD R2, 1, R2\n")
        self.writer.write("MD_RET1 POP R4\n")
        self.writer.write("   PUSH R2\n")
        self.writer.write("   PUSH R3\n")
        self.writer.write("   PUSH R4\n")
        self.writer.write("   RET\n")
        self.writer.write("MUL CALL MD_INIT\n")
        self.writer.write("   XOR R1, 0, R1\n")
        self.writer.write("   JP_Z MUL_RET\n")
        self.writer.write("   SUB R1, 1, R1\n")
        self.writer.write("MUL_1  ADD R2, R0, R2\n")
        self.writer.write("   SUB R1, 1, R1\n")
        self.writer.write("   JP_NN MUL_1\n")
        self.writer.write("MUL_RET CALL MD_RET\n")
        self.writer.write("   RET\n")
        self.writer.write("DIV CALL MD_INIT\n")
        self.writer.write("   XOR R1, 0, R1\n")
        self.writer.write("   JP_Z DIV_RET\n")
        self.writer.write("DIV_1  ADD R2, 1, R2\n")
        self.writer.write("   SUB R0, R1, R0\n")
        self.writer.write("   JP_NN DIV_1\n")
        self.writer.write("   SUB R2, 1, R2\n")
        self.writer.write("DIV_RET CALL MD_RET\n")
        self.writer.write("   RET\n")


    def read_next_lines(self, n):
        for _ in range(n):
            if not self.read_next_line():
                return False
        return True

    def read_var_name(self):
        return self.line_curr.split(" ")[2]

    def read_next_line(self):
        try:
            self.line_curr = next(self.reader).strip()
            if self.line_curr == "<lista_naredbi>":
                self.line_num += 1
                self.read_next_line()
            return True
        except StopIteration:
            return False

    def get_next_line(self):
        self.line_curr = None
        if not self.read_next_line():
            return None
        return self.line_curr


if __name__ == "__main__":
    frisc_generator = FRISCGenerator()