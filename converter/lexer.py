from tokens import Token, TokenType, KEYWORDS


class Lexer:
    """
    Lexical analyzer for Java source code.
    
    Reads the source code character by character and produces
    a flat list of Token objects for the parser to consume.
    
    Usage:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
    """

    def __init__(self, source_code: str):
        self.source = source_code
        self.pos = 0           # текуща позиция в source
        self.line = 1          # текущ ред
        self.column = 0        # текуща колона
        self.tokens: list[Token] = []

    # ------------------------------------------------------------------ #
    #  Главен метод                                                        #
    # ------------------------------------------------------------------ #

    def tokenize(self) -> list[Token]:
        """Scan the entire source and return all tokens."""
        while not self._is_at_end():
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    # ------------------------------------------------------------------ #
    #  Core scan                                                           #
    # ------------------------------------------------------------------ #

    def _scan_token(self):
        """Read one token starting at the current position."""
        char = self._advance()

        # --- Whitespace ---
        if char in (' ', '\t', '\r'):
            return
        if char == '\n':
            self.line += 1
            self.column = 0
            return

        # --- Коментари и / ---
        if char == '/':
            if self._match('/'):
                self._convert_line_comment()
            elif self._match('*'):
                self._convert_block_comment()
            elif self._match('='):
                self._add_token(TokenType.DIVIDE_ASSIGN, '/=')
            else:
                self._add_token(TokenType.DIVIDE, '/')
            return

        # --- Стрингови и char литерали ---
        if char == '"':
            self._read_string()
            return
        if char == "'":
            self._read_char()
            return

        # --- Числа ---
        if char.isdigit():
            self._read_number(char)
            return

        # --- Идентификатори и ключови думи ---
        if char.isalpha() or char == '_':
            self._read_identifier(char)
            return

        # --- Оператори и разделители ---
        self._read_symbol(char)

    # ------------------------------------------------------------------ #
    #  Литерали                                                            #
    # ------------------------------------------------------------------ #

    def _read_string(self):
        """Read a string literal, handling escape sequences."""
        value = ''
        while not self._is_at_end() and self._peek() != '"':
            ch = self._advance()
            if ch == '\\':                        # escape sequence
                value += self._read_escape()
            elif ch == '\n':
                self.line += 1
                self.column = 0
                value += ch
            else:
                value += ch

        self._advance()                           # затваря "
        self._add_token(TokenType.STRING_LITERAL, value)

    def _read_char(self):
        """Read a char literal e.g. 'a' or '\\n'."""
        value = ''
        ch = self._advance()
        if ch == '\\':
            value = self._read_escape()
        else:
            value = ch
        self._advance()                           # затваря '
        self._add_token(TokenType.CHAR_LITERAL, value)

    def _read_escape(self) -> str:
        """Read one escape sequence after the backslash."""
        ESCAPES = {
            'n': '\n', 't': '\t', 'r': '\r',
            '"': '"',  "'": "'",  '\\': '\\'
        }
        ch = self._advance()
        return ESCAPES.get(ch, ch)

    def _read_number(self, first_char: str):
        """Read an integer or float literal."""
        value = first_char
        is_float = False

        while not self._is_at_end() and self._peek().isdigit():
            value += self._advance()

        # Десетична точка → float
        if self._peek() == '.' and self._peek_next().isdigit():
            is_float = True
            value += self._advance()             # '.'
            while not self._is_at_end() and self._peek().isdigit():
                value += self._advance()

        # Java суфикси: 1.0f, 1.0d, 100L
        if self._peek() in ('f', 'F', 'd', 'D', 'l', 'L'):
            self._advance()                      # консумираме суфикса, не го пазим

        token_type = TokenType.FLOAT_LITERAL if is_float else TokenType.INTEGER_LITERAL
        self._add_token(token_type, value)

    def _read_identifier(self, first_char: str):
        """Read an identifier or keyword."""
        value = first_char
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == '_'):
            value += self._advance()

        # Проверяваме дали е ключова дума
        token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)
        self._add_token(token_type, value)

    # ------------------------------------------------------------------ #
    #  Оператори и разделители                                            #
    # ------------------------------------------------------------------ #

    def _read_symbol(self, char: str):
        """Map a single character (or two-char sequence) to a token."""
        match char:
            # Скоби
            case '(': self._add_token(TokenType.LPAREN, char)
            case ')': self._add_token(TokenType.RPAREN, char)
            case '{': self._add_token(TokenType.LBRACE, char)
            case '}': self._add_token(TokenType.RBRACE, char)
            case '[': self._add_token(TokenType.LBRACKET, char)
            case ']': self._add_token(TokenType.RBRACKET, char)

            # Разделители
            case ';': self._add_token(TokenType.SEMICOLON, char)
            case ',': self._add_token(TokenType.COMMA, char)
            case '.': self._add_token(TokenType.DOT, char)
            case ':': self._add_token(TokenType.COLON, char)

            # Аритметика
            case '+':
                if self._match('+'):   self._add_token(TokenType.INCREMENT, '++')
                elif self._match('='): self._add_token(TokenType.PLUS_ASSIGN, '+=')
                else:                  self._add_token(TokenType.PLUS, '+')
            case '-':
                if self._match('-'):   self._add_token(TokenType.DECREMENT, '--')
                elif self._match('='): self._add_token(TokenType.MINUS_ASSIGN, '-=')
                else:                  self._add_token(TokenType.MINUS, '-')
            case '*':
                if self._match('='): self._add_token(TokenType.MULTIPLY_ASSIGN, '*=')
                else:                self._add_token(TokenType.MULTIPLY, '*')
            case '%':
                self._add_token(TokenType.MODULO, char)

            # Сравнение и присвояване
            case '=':
                if self._match('='): self._add_token(TokenType.EQUALS, '==')
                else:                self._add_token(TokenType.ASSIGN, '=')
            case '!':
                if self._match('='): self._add_token(TokenType.NOT_EQUALS, '!=')
                else:                self._add_token(TokenType.NOT, '!')
            case '<':
                if self._match('='): self._add_token(TokenType.LESS_OR_EQUAL, '<=')
                else:                self._add_token(TokenType.LESS_THAN, '<')
            case '>':
                if self._match('='): self._add_token(TokenType.GREATER_OR_EQUAL, '>=')
                else:                self._add_token(TokenType.GREATER_THAN, '>')

            # Логически
            case '&':
                if self._match('&'): self._add_token(TokenType.AND, '&&')
            case '|':
                if self._match('|'): self._add_token(TokenType.OR, '||')

            case _:
                raise LexerError(f"Unexpected character '{char}'", self.line, self.column)

    # ------------------------------------------------------------------ #
    #  Коментари                                                           #
    # ------------------------------------------------------------------ #

    def _convert_line_comment(self):
        """Convert // comment to # comment."""
        value = ''
        while not self._is_at_end() and self._peek() != '\n':
            value += self._advance()
        self._add_token(TokenType.COMMENT, f"#{value}")

    def _convert_block_comment(self):
        """Convert /* ... */ comment to # ... comment."""
        value = ''
        while not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
                self.column = 0
            ch = self._advance()
            if ch == '*' and self._match('/'):
                # Всеки ред на block comment става отделен # коментар
                for line in value.splitlines():
                    self._add_token(TokenType.COMMENT, f"# {line.strip()}")
                return
            value += ch

    # ------------------------------------------------------------------ #
    #  Помощни методи                                                      #
    # ------------------------------------------------------------------ #

    def _advance(self) -> str:
        """Consume and return the current character."""
        char = self.source[self.pos]
        self.pos += 1
        self.column += 1
        return char

    def _peek(self) -> str:
        """Return current character without consuming it."""
        if self._is_at_end():
            return '\0'
        return self.source[self.pos]

    def _peek_next(self) -> str:
        """Return the character after the current one without consuming."""
        if self.pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.pos + 1]

    def _match(self, expected: str) -> bool:
        """Consume current character only if it matches expected."""
        if self._is_at_end() or self.source[self.pos] != expected:
            return False
        self.pos += 1
        self.column += 1
        return True

    def _is_at_end(self) -> bool:
        return self.pos >= len(self.source)

    def _add_token(self, type: TokenType, value: str):
        self.tokens.append(Token(type, value, self.line, self.column))


# ------------------------------------------------------------------ #
#  Грешки                                                              #
# ------------------------------------------------------------------ #

class LexerError(Exception):
    """Raised when the lexer encounters an unexpected character."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"[Line {line}, Col {column}] LexerError: {message}")
        self.line = line
        self.column = column