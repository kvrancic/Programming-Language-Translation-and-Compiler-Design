import sys

def syntaxAnalyze(lines):
    retciDefinicije = []
    leksJedinke = []
    dubinaBlokaJedinki = []

    trenutnaDubinaBloka = 0
    prevLine = ""

    for input in lines:
        input = input.strip()

        if input == "":
            break

        if input.split(" ")[0] == "KR_ZA":
            trenutnaDubinaBloka += 1
        elif input.split(" ")[0] == "KR_AZ":
            i = 0
            while i < len(leksJedinke):
                if trenutnaDubinaBloka == dubinaBlokaJedinki[i]:
                    del retciDefinicije[i]
                    del leksJedinke[i]
                    del dubinaBlokaJedinki[i]
                    i -= 1
                i += 1

            trenutnaDubinaBloka -= 1

        if input.split(" ")[0] == "IDN":
            jedinkaDefinirana = False
            for jedinka in leksJedinke:
                if input.split(" ")[2] == jedinka:
                    jedinkaDefinirana = True

            if prevLine != "<P>" and (not jedinkaDefinirana or prevLine.split(" ")[0] == "KR_ZA"):
                retciDefinicije.append(int(input.split(" ")[1]))
                leksJedinke.append(input.split(" ")[2])
                dubinaBlokaJedinki.append(trenutnaDubinaBloka)
            elif not prevLine == "<naredba_pridruzivanja>" and not (prevLine != "<P>" and (not jedinkaDefinirana or prevLine.split(" ")[0] == "KR_ZA")):
                leksJedinka = None
                redakDefinicije = None

                if not (leksJedinke[-1] == input.split(" ")[2] and retciDefinicije[-1] == int(input.split(" ")[1])):
                    for i in range(len(leksJedinke)):
                        if input.split(" ")[2] == leksJedinke[i]:
                            leksJedinka = leksJedinke[i]
                            redakDefinicije = retciDefinicije[i]

                if leksJedinka is not None:
                    print(f"{input.split(' ')[1]} {redakDefinicije} {leksJedinka}")
                else:
                    print(f"err {input.split(' ')[1]} {input.split(' ')[2]}")
                    break

        prevLine = input

def main():
    lines = []
    for line in sys.stdin:
        lines.append(line)
    syntaxAnalyze(lines)

if __name__ == "__main__":
    main()
