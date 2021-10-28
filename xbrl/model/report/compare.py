
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

    # if value is INF or NaN, valueRange returns that value for both ends of
    # the range, ignoring decimals.
    if aa[0].is_nan() or bb[0].is_nan():
        return False

    if aa[0].is_infinite() or bb[0].is_infinite():
        return a == b

    # Ranges must overlap, but if precision is the same then the values must be the same
    return aa[0] <= bb[1] and bb[0] <= aa[1] and (a.decimals != b.decimals or a.numericValue == b.numericValue)


    
