from collections import deque
import sys

# Definicija gramatike
non_terminal_symbols = ["<program>", "<lista_naredbi>", "<lista_naredbi>", "<naredba>", "<naredba>",
                        "<naredba_pridruzivanja>", "<za_petlja>", "<E>", "<E_lista>", "<E_lista>",
                        "<E_lista>", "<T>", "<T_lista>", "<T_lista>", "<T_lista>", "<P>", "<P>", "<P>",
                        "<P>", "<P>"]
productions = ["<lista_naredbi>", "<naredba> <lista_naredbi>", "$", "<naredba_pridruzivanja>",
                "<za_petlja>", "IDN OP_PRIDRUZI <E>", "KR_ZA IDN KR_OD <E> KR_DO <E> <lista_naredbi> KR_AZ",
                "<T> <E_lista>", "OP_PLUS <E>", "OP_MINUS <E>", "$", "<P> <T_lista>", "OP_PUTA <T>",
                "OP_DIJELI <T>", "$", "OP_PLUS <P>", "OP_MINUS <P>", "L_ZAGRADA <E> D_ZAGRADA", "IDN", "BROJ"]
apply_list = ["IDN KR_ZA XYZ_KRAJ", "IDN KR_ZA", "KR_AZ XYZ_KRAJ", "IDN", "KR_ZA", "IDN",
                "KR_ZA", "IDN BROJ OP_PLUS OP_MINUS L_ZAGRADA", "OP_PLUS", "OP_MINUS",
                "IDN KR_ZA KR_DO KR_AZ D_ZAGRADA XYZ_KRAJ", "IDN BROJ OP_PLUS OP_MINUS L_ZAGRADA",
                "OP_PUTA", "OP_DIJELI", "IDN KR_ZA KR_DO KR_AZ OP_PLUS OP_MINUS D_ZAGRADA XYZ_KRAJ",
                "OP_PLUS", "OP_MINUS", "L_ZAGRADA", "IDN", "BROJ"]

def parse():
    stack = deque(["<program>"])
    indent_stack = deque([0])
    output_lines = []
    indentations = []

    current_input = None
    try:
        current_input = input()
    except EOFError:
        current_input = "XYZ_KRAJ"

    while current_input or stack:
        identifier = current_input.split()[0] if current_input else "XYZ_KRAJ"
        if identifier == "XYZ_KRAJ" and not stack:
            break

        if stack[0] == "$":
            output_lines.append(stack.popleft())
            indentations.append(indent_stack.popleft())
            continue
        elif stack[0] == identifier:
            output_lines.append(current_input)
            stack.popleft()
            indentations.append(indent_stack.popleft())
            try:
                current_input = input() if stack else "XYZ_KRAJ"
            except EOFError:
                current_input = "XYZ_KRAJ"
            continue

        found = False
        for i, symbol in enumerate(non_terminal_symbols):
            if symbol == stack[0] and identifier in apply_list[i].split():
                found = True
                current_indent = indent_stack.popleft()
                indentations.append(current_indent)
                production_parts = productions[i].split()
                indent_stack.extendleft([current_indent + 1] * len(production_parts))
                output_lines.append(stack.popleft())
                stack.extendleft(production_parts[::-1])
                break

        if not found:
            print("err", current_input if (current_input != "XYZ_KRAJ" and stack[0] != "KR_AZ") else "kraj")
            return

    for line, indent in zip(output_lines, indentations):
        print(" " * indent + line)

# Pokretanje parsiranja
parse()
