
def completeDuplicates(a, b):
    if a.concept.isLanguageType:
        return a.typedValue.lower() == b.typedValue.lower()
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

    # Ranges must overlap, but if precision is the same then the values must be the same
    return aa[0] <= bb[1] and bb[0] <= aa[1] and (a.decimals != b.decimals or a.numericValue == b.numericValue)


    
