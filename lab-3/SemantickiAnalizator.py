import sys

def syntaxAnalyze(lines):
    definitionsRows = []
    lexicalUnits = []
    blockDepthUnits = []

    currentBlockDepth = 0
    prevLine = ""

    for input in lines:
        input = input.strip()

        if input == "":
            break

        splitInput = input.split(" ")
        firstWord = splitInput[0]

        if firstWord == "KR_ZA":
            currentBlockDepth += 1
        elif firstWord == "KR_AZ":
            indicesToRemove = [i for i, depth in enumerate(blockDepthUnits) if depth == currentBlockDepth]
            for i in sorted(indicesToRemove, reverse=True):
                definitionsRows.pop(i)
                lexicalUnits.pop(i)
                blockDepthUnits.pop(i)

            currentBlockDepth -= 1

        if firstWord == "IDN":
            idnName = splitInput[2]
            isUnitDefined = idnName in lexicalUnits

            if prevLine != "<P>" and (not isUnitDefined or prevLine.split(" ")[0] == "KR_ZA"):
                definitionsRows.append(int(splitInput[1]))
                lexicalUnits.append(idnName)
                blockDepthUnits.append(currentBlockDepth)
            elif prevLine != "<naredba_pridruzivanja>" and (prevLine == "<P>" or isUnitDefined or prevLine.split(" ")[0] != "KR_ZA"):
                leksJedinka, redakDefinicije = None, None

                if not (lexicalUnits[-1] == idnName and definitionsRows[-1] == int(splitInput[1])):
                    for unit, row in zip(lexicalUnits, definitionsRows):
                        if unit == idnName:
                            leksJedinka, redakDefinicije = unit, row

                if leksJedinka is not None:
                    print(f"{splitInput[1]} {redakDefinicije} {leksJedinka}")
                else:
                    print(f"err {splitInput[1]} {idnName}")
                    break

        prevLine = input

def main():
    lines = [line for line in sys.stdin]
    syntaxAnalyze(lines)

if __name__ == "__main__":
    main()
