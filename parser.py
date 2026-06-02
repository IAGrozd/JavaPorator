class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tokens = []
        self.current_token_index = 0

    def tokenize(self):
        with open(self.file_path, 'r') as file:
            code = file.read()
            # Simple tokenization logic (can be improved)
            self.tokens = code.split()

    def has_more_tokens(self):
        return self.current_token_index < len(self.tokens)

    def advance(self):
        if self.has_more_tokens():
            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token
        return None