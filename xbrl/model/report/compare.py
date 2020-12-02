
#def consistentFacts(a, b):

def completeDuplicates(a, b):
    return a.typedValue == b.typedValue and a.decimals == b.decimals

def consistentDuplicates(a, b):
    if completeDuplicates(a, b):
        return True

    if not a.isNumeric or not b.isNumeric:
        return False

    if a.isNil or b.isNil:
        return a.isNil == b.isNil

    aa = a.valueRange
    bb = b.valueRange

    return aa[0] < bb[1] and bb[0] < aa[1]


    
