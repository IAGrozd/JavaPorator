"""
src/rules.py — Regex правила за конверсия от Java към Python.
"""

import re
from dataclasses import dataclass


@dataclass
class Rule:
    pattern: str
    replacement: str
    description: str = ""


RULES: list[Rule] = [
    # Comments
    Rule(
        pattern=r'//(.*)$',
        replacement=r'#\1',
        description='Едноредов коментар'
    ),
    Rule(
        pattern=r'/\*.*?\*/',
        replacement='',
        description='Многоредов коментар'
    ),

    # 2. PACKAGE И IMPORTS
    Rule(
        pattern=r'^\s*package\s+[\w.]+\s*;',
        replacement='',
        description='Премахване на package'
    ),
    Rule(
        pattern=r'^\s*import\s+[\w.]*\.(\w+)\s*;',
        replacement=r'# import \1',
        description='Закоментиране на import'
    ),

    # 3. КЛАСОВЕ
    Rule(
        pattern=r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+(\w+)\s+extends\s+(\w+)\s+implements\s+([\w,\s]+)',
        replacement=r'class \1(\2, \3)',
        description='Клас с наследство и интерфейси'
    ),
    Rule(
        pattern=r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+(\w+)\s+extends\s+(\w+)',
        replacement=r'class \1(\2)',
        description='Клас с наследство'
    ),
    Rule(
        pattern=r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+(\w+)\s+implements\s+([\w,\s]+)',
        replacement=r'class \1(\2)',
        description='Клас с интерфейс'
    ),
    Rule(
        pattern=r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+(\w+)',
        replacement=r'class \1',
        description='Прост клас'
    ),

    # 4. СТАНДАРТНА БИБЛИОТЕКА (Преди премахването на типовете)
    Rule(
        pattern=r'System\.out\.println\((.*?)\)\s*;?',
        replacement=r'print(\1)',
        description='System.out.println → print()'
    ),
    Rule(
        pattern=r'System\.out\.print\((.*?)\)\s*;?',
        replacement=r'print(\1, end="")',
        description='System.out.print → print(end="")'
    ),
    Rule(
        pattern=r'\.equals\((.*?)\)',
        replacement=r' == \1',
        description='.equals() → =='
    ),
    Rule(
        pattern=r'\b([\w.\[\]]+)\.length\(\)\b',
        replacement=r'len(\1)',
        description='obj.length() → len(obj)'
    ),
    Rule(
        pattern=r'\b([\w.\[\]]+)\.size\(\)\b',
        replacement=r'len(\1)',
        description='obj.size() → len(obj)'
    ),

    # 5. МЕТОДИ И КОНСТРУКТОРИ
    Rule(
        # public static int calculate( -> def calculate(
        pattern=r'(?:(?:public|private|protected|static|final|abstract|synchronized)\s+)*'
                r'(?:(?:void|int|double|float|long|short|byte|boolean|char|String|[\w<>\[\]]+)\s+)'
                r'(\w+)\s*\(',
        replacement=r'def \1(',
        description='Декларация на метод'
    ),
    Rule(
        pattern=r'(?:public|private|protected)\s+(\w+)\s*\(',
        replacement=r'def __init__(self, ',
        description='Конструктор → __init__'
    ),

    # 6. ПРЕМАХВАНЕ НА ТИПОВЕ ОТ ПРОМЕНЛИВИ
    Rule(pattern=r'\b(?:int|double|float|long|short|byte|boolean|char|String)\s+(\w+)', replacement=r'\1'),
    Rule(pattern=r'\b\w+<[\w<>, ]+>\s+(\w+)', replacement=r'\1'),  # Generics
    Rule(pattern=r'\b\w+(?:\[\])+\s+(\w+)', replacement=r'\1'),     # Масиви

    # 7. МОДИФИКАТОРИ И NEW
    Rule(pattern=r'\b(?:public|private|protected|static|final|abstract|synchronized|volatile)\b\s*', replacement=r''),
    Rule(pattern=r'\bvoid\b\s*', replacement=r''),
    Rule(pattern=r'\bnew\s+(\w+)', replacement=r'\1'),

    # 8. КОНТРОЛЕН ПОТОК
    Rule(
        pattern=r'for\s*\(\s*\w+\s+(\w+)\s*:\s*(.*?)\s*\)',
        replacement=r'for \1 in \2:',
        description='For-each цикъл'
    ),
    Rule(
        pattern=r'\belse\s+if\b',
        replacement=r'elif',
        description='else if'
    ),
    Rule(
        pattern=r'\belse\s+if\s*\((.*?)\)',
        replacement=r'elif \1:',
        description='else if (условие) → elif условие:'
    ),
    Rule(
        pattern=r'\belse\b',
        replacement=r'else:',
        description='else'
    ),
    Rule(
        pattern=r'\bwhile\s*\((.*?)\)',
        replacement=r'while \1:',
        description='while цикъл'
    ),

    # 9. ОПЕРАТОРИ И ЛИТЕРАЛИ
    Rule(pattern=r'&&', replacement=r' and '),
    Rule(pattern=r'\|\|', replacement=r' or '),
    Rule(pattern=r'!(?!=)', replacement=r'not '),
    Rule(pattern=r'\btrue\b', replacement=r'True'),
    Rule(pattern=r'\bfalse\b', replacement=r'False'),
    Rule(pattern=r'\bnull\b', replacement=r'None'),

    # 10. ТОЧКА И ЗАПЕТАЯ (Последна)
    Rule(pattern=r'\s*;', replacement=r''),
]