from enum import Enum, EnumType, auto
from dataclasses import dataclass


class TokenType(Enum):

    """ Defines all valid token types for the Java lexer. """

    # Key words
    CLASS = auto()
    INTERFACE = auto()
    EXTENDS = auto()
    IMPLEMENTS = auto()
    NEW = auto()
    THIS = auto()
    SUPER = auto()
    RETURN = auto()
    IMPORT = auto()
    PACKAGE = auto()

    # Modifiers
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()
    STATIC = auto()
    FINAL = auto()
    ABSTRACT = auto()

    # Control flow
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    DO = auto()
    BREAK = auto()
    CONTINUE = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()

    # Base types
    INT = auto()
    DOUBLE = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    CHAR = auto()
    LONG = auto()
    SHORT = auto()
    BYTE = auto()
    VOID = auto()

    # Literals
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()
    BOOLEAN_LITERAL = auto()   # true / false
    NULL_LITERAL = auto()   # null

    # Arithmetic operators
    PLUS = auto()   # +
    MINUS = auto()   # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()   # /
    MODULO = auto()   # %

    # Comparison operators
    EQUALS = auto()   # ==
    NOT_EQUALS = auto()   # !=
    LESS_THAN = auto()   # 
    GREATER_THAN = auto()   # >
    LESS_OR_EQUAL = auto()   # <=
    GREATER_OR_EQUAL= auto()   # >=

    # Logical operators
    AND = auto()   # &&
    OR = auto()   # ||
    NOT = auto()   # !

    # Assignment
    ASSIGN = auto()   # =
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN = auto()   # -=
    MULTIPLY_ASSIGN = auto()   # *=
    DIVIDE_ASSIGN = auto()   # /=

    # Increment / Decrement
    INCREMENT = auto()   # ++
    DECREMENT = auto()   # --

    # Delimiters
    LPAREN = auto()   # (
    RPAREN = auto()   # )
    LBRACE = auto()   # {
    RBRACE = auto()   # }
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    SEMICOLON = auto()   # ;
    COMMA = auto()   # ,
    DOT = auto()   # .
    COLON = auto()   # :

    # Special
    IDENTIFIER = auto()   # variable names, class names, method names
    COMMENT = auto() # coment signs (// and /* */)
    EOF = auto()   # end of file



# The lexer will use this to distinguish keywords from identifiers
KEYWORDS: dict[str, TokenType] = {
    "class":        TokenType.CLASS,
    "interface":    TokenType.INTERFACE,
    "extends":      TokenType.EXTENDS,
    "implements":   TokenType.IMPLEMENTS,
    "new":          TokenType.NEW,
    "this":         TokenType.THIS,
    "super":        TokenType.SUPER,
    "return":       TokenType.RETURN,
    "import":       TokenType.IMPORT,
    "package":      TokenType.PACKAGE,
    "public":       TokenType.PUBLIC,
    "private":      TokenType.PRIVATE,
    "protected":    TokenType.PROTECTED,
    "static":       TokenType.STATIC,
    "final":        TokenType.FINAL,
    "abstract":     TokenType.ABSTRACT,
    "if":           TokenType.IF,
    "else":         TokenType.ELSE,
    "for":          TokenType.FOR,
    "while":        TokenType.WHILE,
    "do":           TokenType.DO,
    "break":        TokenType.BREAK,
    "continue":     TokenType.CONTINUE,
    "switch":       TokenType.SWITCH,
    "case":         TokenType.CASE,
    "default":      TokenType.DEFAULT,
    "int":          TokenType.INT,
    "double":       TokenType.DOUBLE,
    "float":        TokenType.FLOAT,
    "boolean":      TokenType.BOOLEAN,
    "char":         TokenType.CHAR,
    "long":         TokenType.LONG,
    "short":        TokenType.SHORT,
    "byte":         TokenType.BYTE,
    "void":         TokenType.VOID,
    "true":         TokenType.BOOLEAN_LITERAL,
    "false":        TokenType.BOOLEAN_LITERAL,
    "null":         TokenType.NULL_LITERAL,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int      # на кой ред е токенът (за error съобщения)
    column: int    # на коя колона