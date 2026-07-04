import re
from dataclasses import dataclass

ACCESS_MODIFIERS = "public|private|protected"
BASE_TYPES = "void|int|double|float|long|short|byte|boolean|char|String"

def multiline_to_oneline_comment(match):
    comment_content = match.group(1)
    lines = comment_content.split('\n')
    python_comment_lines = []
    
    for line in lines:
        clean_line = line.strip()
        if clean_line.startswith('*'):
            clean_line = clean_line[1:].strip()
        if clean_line:
            python_comment_lines.append(f"# {clean_line}")
        else:
            python_comment_lines.append("#")
            
    return '\n'.join(python_comment_lines)

def standard_for_to_range(match):
    var_name = match.group(1)
    start = match.group(2).strip()
    op = match.group(3).strip()
    end = match.group(4).strip()
    update = match.group(5).strip()
    
    if op == "<=":
        if end.isdigit():
            end = str(int(end) + 1)
        else:
            end = f"{end} + 1"
    elif op == ">=":
        if end.isdigit():
            end = str(int(end) - 1)
        else:
            end = f"{end} - 1"
            
    step = "1"
    if "++" in update:
        step = "1"
    elif "--" in update:
        step = "-1"
    elif "+=" in update:
        step = update.split("+=")[1].strip()
    elif "-=" in update:
        step = f"-{update.split('-=')[1].strip()}"
        
    if step == "1":
        if start == "0":
            return f"for {var_name} in range({end}):"
        return f"for {var_name} in range({start}, {end}):"
    else:
        return f"for {var_name} in range({start}, {end}, {step}):"

@dataclass
class Rule:
    pattern: str
    replacement: str
    description: str = ""


RULES: list[Rule] = [
    # COMMENTS
    Rule(
        pattern=r'//(.*)$',
        replacement=r'#\1',
        description='Oneline comment'
    ),
    Rule(
        pattern=r'/\*([\s\S]*?)\*/',
        replacement=multiline_to_oneline_comment,
        description='Multiline comment'
    ),

    # PACKAGE AND IMPORTS
    Rule(
        pattern=r'^\s*package\s+[\w.]+\s*;',
        replacement='',
        description='Remove package declaration'
    ),
    Rule(
        pattern=r'^\s*import\s+[\w.]*\.(\w+)\s*;',
        replacement=r'import \1',
        description='Import declaration'
    ),

    # CONTROL FLOW
    Rule(
        pattern=r'\belse\s+if\s*\((.*?)\)',
        replacement=r'elif \1:',
        description='elif'
    ),
    Rule(
        pattern=r'\bif\s*\((.*?)\)',
        replacement=r'if \1:',
        description='if'
    ),
    Rule(
        pattern=r'\belse\b',
        replacement=r'else:',
        description='else'
    ),
    Rule(
        pattern=rf'\bfor\s*\(\s*(?:(?:{BASE_TYPES})\s+)?(\w+)\s*=\s*([^;]+)\s*;\s*\1\s*(<|<=|>|>=)\s*([^;]+)\s*;\s*([^)]+)\)',
        replacement=standard_for_to_range,
        description='For'
    ),
    Rule(
        pattern=r'\bfor\s*\(\s*(?:final\s+)?(?:[\w<>\[\]\.]+)\s+(\w+)\s*:\s*(.*?)\s*\)',
        replacement=r'for \1 in \2:',
        description='For-each'
    ),
    Rule(
        pattern=r'\bwhile\s*\((.*?)\)',
        replacement=r'while \1:',
        description='while'
    ),

    # CLASSES
    Rule(
        pattern=rf'(?:\b(?:{ACCESS_MODIFIERS})\s+)?(?:abstract\s+)?class\s+(\w+)\s+extends\s+(\w+)',
        replacement=r'class \1(\2):',
        description='Inheritance class'
    ),
    Rule(
        pattern=rf'(?:\b(?:{ACCESS_MODIFIERS})\s+)?(?:abstract\s+)?class\s+(\w+)\s+implements\s+([\w,\s]+)',
        replacement=r'class \1(\2):',
        description='Class with interface'
    ),
    Rule(
        pattern=rf'(?:\b(?:{ACCESS_MODIFIERS})\s+)?(?:abstract\s+)?class\s+(\w+)\b(?!\s*\()',
        replacement=r'class \1:',
        description='Simple class'
    ),

    # METHODS AND INITIALIZERS
    Rule(
        pattern=rf'(?:\b(?:{ACCESS_MODIFIERS})\s+)(\w+)\s*\((.*?)\)',
        replacement=r'def __init__(self, \2):',
        description='__init__()'
    ),
    Rule(
        pattern=rf'(?:\b(?!(?:class|new|return|in|for|if|else|elif|while|def)\b)(?:{BASE_TYPES}|[\w<>\[\]]+)\s+)(\w+)\s*\((.*?)\)',
        replacement=r'def \1(self, \2):',
        description='Method declaration'
    ),

    # STANDARD LIBRARY
    Rule(
        pattern=r'System\.out\.println\(([^"]*"[^"]*")\s*\+\s*([a-zA-Z0-9_]+)\);',
        replacement=r'print(\1, \2)'
    ),
    Rule(
        pattern=r'System\.out\.print\((.*?)\s*\+\s*"(.*?)"\)\s*;?',
        replacement=r'print(\1, "\2", end="")',
    ),
    Rule(
        pattern=r'System\.out\.println\((.*?)\)\s*;?',
        replacement=r'print(\1)',
        description='print()'
    ),
    Rule(
        pattern=r'System\.out\.print\((.*?)\)\s*;?',
        replacement=r'print(\1, end="")',
        description='print(end="")'
    ),
    Rule(
        pattern=r'\.equals\((.*?)\)',
        replacement=r' == \1',
        description='=='
    ),
    Rule(
        pattern=r'\b([\w.\[\]]+)\.length\(\)',
        replacement=r'len(\1)',
        description='len(obj)'
    ),
    Rule(
        pattern=r'\b([\w.\[\]]+)\.size\(\)',
        replacement=r'len(\1)',
        description='len(obj)'
    ),
    Rule(
        pattern=rf'({BASE_TYPES})\[\]\s+(\w+)\s*=\s*{{([^}}]+)}};',
        replacement=r'\2 = [\3]',
        description='Arrays to lists'
    ),

    # DETYPIFICATION
    Rule(
        pattern=rf'\b(?:{BASE_TYPES})\s+(\w+)',
        replacement=r'\1', 
        description='Base types'
    ),
    Rule(
        pattern=r'\b\w+<[\w<>, ]+>\s+(\w+)',
        replacement=r'\1',
        description='Generics'
    ),
    Rule(
        pattern=r'\b\w+(?:\[\])+\s+(\w+)',
        replacement=r'\1',
        description='Lists'
    ),

    # MODIFICATORS
    Rule(
        pattern=rf'\b(?:{ACCESS_MODIFIERS}|static|final|abstract|synchronized|volatile)\b\s*',
        replacement=r''
    ),
    Rule(
        pattern=r'\bvoid\b\s*',
        replacement=r''
    ),
    Rule(
        pattern=r'\bnew\s+(\w+)',
        replacement=r'\1'
    ),

    # 9. BOOL OPERATORS
    Rule(
        pattern=r'&&',
        replacement=r'and'
    ),
    Rule(
        pattern=r'\|\|',
        replacement=r'or'
    ),
    Rule(
        pattern=r'!(?!=)',
        replacement=r'not '
    ),
    Rule(
        pattern=r'\btrue\b',
        replacement=r'True'
    ),
    Rule(
        pattern=r'\bfalse\b',
        replacement=r'False'
    ),
    Rule(
        pattern=r'\bnull\b',
        replacement=r'None'
    ),
    Rule(
        pattern=r'\s*;',
        replacement=r''
    ),
]

def apply_rules(code: str) -> str:
    for rule in RULES:
        code = re.sub(rule.pattern, rule.replacement, code, flags=re.MULTILINE)
    return code