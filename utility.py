import pprint

# Prints the nicely formatted dictionary
def PrintDict(dictionary):
    pprint.pprint(dictionary)

# for debugging, sometime is if hard to figure out if, variable is string or tuple in buildbot
def DetectType(var):
    if isinstance(var, tuple):
        print("Variable is a tuple, please convert to string before sending it by a http reporter")
    if isinstance(var, str):
        print("Variable is a string")

# Get nth element from tuple
# It is sometime hard to figure out if value is a string
def ExtractValueFromTuple(tuple, element):
    size = len(tuple)
    if element > size:
        raise Exception("Error : Choose smaller element, out of bounds")
    return tuple[element]

# all build properties are tuples 
def GetBuildPropertyValue(build_properties, propertyName):
    if build_properties is None:
        raise Exception("build_properties is none")
    
    propertyTuple = build_properties.get(propertyName)
    if propertyTuple is None:
        # return None
        return propertyTuple
    return str(propertyTuple[0])
