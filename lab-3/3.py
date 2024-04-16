import sys

def syntaxAnalyze(lines):
    lexicalInfo = {}  # A dictionary to store lexical unit, its definition row, and block depth
    currentBlockDepth = 0
    prevLine = ""

    for input in lines:
        input = input.strip()

        if input == "":
            break

        splitInput = input.split(" ")
        firstWord = splitInput[0]

        # Check the number of elements in splitInput before unpacking
        if len(splitInput) > 1:
            rowNumber = splitInput[1]
        else:
            rowNumber = None

        if len(splitInput) > 2:
            idnName = splitInput[2]
        else:
            idnName = None

        if firstWord == "KR_ZA":
            currentBlockDepth += 1
        elif firstWord == "KR_AZ":
            # Remove entries with the current block depth
            lexicalInfo = {k: v for k, v in lexicalInfo.items() if v[1] != currentBlockDepth}
            currentBlockDepth -= 1

        if firstWord == "IDN" and rowNumber is not None and idnName is not None:
            isUnitDefined = idnName in lexicalInfo

            if prevLine != "<P>" and (not isUnitDefined or prevLine.split(" ")[0] == "KR_ZA"):
                lexicalInfo[idnName] = (int(rowNumber), currentBlockDepth)
            elif prevLine != "<naredba_pridruzivanja>" and (prevLine == "<P>" or isUnitDefined or prevLine.split(" ")[0] != "KR_ZA"):
                if idnName in lexicalInfo and lexicalInfo[idnName][0] != int(rowNumber):
                    print(f"{rowNumber} {lexicalInfo[idnName][0]} {idnName}")
                else:
                    print(f"err {rowNumber} {idnName}")
                    break

        prevLine = input

def main():
    lines = [line.strip() for line in sys.stdin if line.strip()]
    syntaxAnalyze(lines)

if __name__ == "__main__":
    main()
