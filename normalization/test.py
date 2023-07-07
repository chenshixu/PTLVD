code = '''
#include <stdio.h>

int main() {
    printf("Hello,\" world!", "sadasd//*");
    return 0;
}
'''
import re

def find_strings(code):
    pattern = re.compile(r'\".*?\"')
    return pattern.findall(code)

def line_find(line):
    if not '\\' in line:
        return find_strings(line)
    elif not '\"' in line:
        return find_strings(line)




strings = find_strings(code)
print(strings)