import os
import re

from src.function import Function
from src.dataFile import DataFile

def extractData(file_path: str) -> DataFile:
    datafile = DataFile()

    # Get the filename without extension
    file = os.path.splitext(os.path.basename(file_path))
    namename = file[0]
    extension = file[1]

    datafile.setFilename(namename)
    datafile.setExtension(extension)

    with open(file_path, 'r') as file:
        format_function = False
        inside_comment = False
        check_function = False
        inside_function = False
        current_comment = ""
        current_function = ""

        # Read line by line
        for line in file:
            if line.lstrip().startswith('/**') and not re.search('[a-zA-Z]', line):
                inside_comment = True
                current_comment = ""
            
            elif inside_comment and line.lstrip().startswith('*/'):
                inside_comment = False
                check_function = True

            elif inside_comment:
                current_comment += line

            elif check_function:
                # in one line
                if re.search(r'\bfun\b', line) and (re.search(r'[\s]*{', line) or re.search(r'{', line)): #and line.strip().endswith('{'):
                    current_function = line.strip()
                    format_function = True

                elif re.search(r'\bfun\b', line):
                    current_function = line.strip()
                    inside_function = True
                
                elif inside_function and (re.search(r'[\s]*{', line) or re.search(r'{', line)):
                    current_function += line.strip()
                    inside_function = False
                    format_function = True

                elif inside_function:
                    current_function += line.strip()
            
            if format_function:
                #print(f"Extract Comment:\n{current_comment}")
                #print(f"Generate Function:\n{current_function}")
                #data.append([current_comment, current_function])
                datafile.addRawData(current_comment, current_function)
                format_function = False
                current_function = ""
                current_comment = ""

    return datafile

def extractParam(line: str) -> tuple[str, str]:
    parts = line.split()
    if len(parts) > 1:
        param_name = parts[1]
        description = ' '.join(parts[2:])
        return param_name, description
    else:
        return "", ""
    

def extractReturn(line: str) -> str:
    return ' '.join(line.split()[1:])

def extractComment(comment: str) -> Function:
    function = Function()
    extracted_comment = ""

    lines = comment.split('\n')
    for line in lines:
        
        line = re.sub(r'^\s*\*\s*', '', line)  # Remove leading spaces, tabs, and asterisks
        line = re.sub(r'\s+', ' ', line)       # Replace multiple spaces with a single space
        
        if re.match(r'\s*@param', line):
            function.addParameter(extractParam(line.strip()))
        elif re.match(r'\s*@interruption', line):
            function.addInterruption(extractParam(line.strip()))
        elif re.match(r'\s*@return', line):
            function.addReturn(extractReturn(line.strip()))
        elif re.match(r'\s*@note', line):
            function.addNote(extractReturn(line.strip()))
        elif re.match(r'\s*\*', line):
            continue
        else:
            extracted_comment += line.strip() + ' '
    function.addDescription(extracted_comment)
    return function

def extractFunction(functionDeclaration: str, function: Function) -> None:
    # Extract the function name
    functionName = getFunctionName(functionDeclaration)

    # Extract and format parameters
    parameters = getParameters(functionDeclaration)

    # print(f"\nfunction: {functionDeclaration}")
    # print(f"--{functionName}({parameters})\n")

    # Format the result
    function.addFunctionName(functionName)
    function.addFunctionParameters(parameters)

def getFunctionName(functionDeclaration: str) -> str:
    functionNameMatch = re.search(r'\bfun\s+([\w.]+)\s*\(', functionDeclaration)
    if functionNameMatch:
        return functionNameMatch.group(1)
    else:
        return "Invalid function declaration"

def getParameters(functionDeclaration: str) -> list[str]:
    formatFun = functionDeclaration.replace(" ", "")
    temp = ""
    parameters = []
    save_parameters = False
    in_parameter = False

    for char in formatFun:
        # Enter in '(...)'
        if char == '(' and not save_parameters:
            save_parameters = True
            in_parameter = True
        # End of the function "fun .. (...) : ... {"
        elif char == '{' and save_parameters:
            break
        # Inside '(...)'
        elif save_parameters:
            #print(f"inside param: {char}")
            if char == ':':
                in_parameter = False
            elif char == ',' and not in_parameter:
                in_parameter = True
            
            if in_parameter:
                if char == ' ' or char == ',':
                    parameters.append(temp)
                    #temp += ', '
                    temp = ""
                else:
                    temp += char
    # Append last parameter
    parameters.append(temp)
    return parameters

