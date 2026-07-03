import re

class JavaScanner:
    def __init__(self):
        self.class_vars = set()

    def _extract_class_variables(self, lines: list[str]):
        """Scan the code and extract all member-variables of the class."""
        self.class_vars.clear()
        identation_level = 0
        
        for line in lines:
            line = line.strip()
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            if identation_level == 1 and not line.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'elif ', 'else ', '{', '}')):
                if '=' in line:
                    var_name = line.split('=')[0].strip()
                else:
                    var_name = line.strip()
                
                if var_name and var_name.isidentifier():
                    self.class_vars.add(var_name)
                elif not var_name.isidentifier():
                    raise ValueError(f"Invalid variable name detected: '{var_name}' in line: '{line}'")
            
            identation_level += open_braces - close_braces

    def _replace_field_callback(self, match, processed_line: str, current_locals: set, new_locals: set) -> str:
        """Checks if a given word should receive the 'self.' prefix."""
        word = match.group(0)
        start, _ = match.span()
        
        if start >= 5 and processed_line[start-5:start] == 'self.':
            return word
            
        if start >= 1 and processed_line[start-1] == '.':
            return word
            
        if word in self.class_vars and word not in current_locals and word not in new_locals:
            return f"self.{word}"
            
        return word

    def _manage_scope_closing(self, close_count: int, local_scopes: list[set]):
        """Take care for closing a scope"""
        for _ in range(close_count):
            if local_scopes:
                local_scopes.pop()
            else:
                raise ValueError("Unmatched closing brace '}' detected in the code.")

    def _collect_current_locals(self, local_scopes: list[set]) -> set:
        """Make a set from all variables that are seen in the current scope"""
        current_locals = set()
        for scope in local_scopes:
            current_locals.update(scope)
        return current_locals

    def _extract_new_locals(self, clean_line: str, inside_method: bool, original_line: str) -> set:
        """Finds new local variables at the current line"""
        new_locals = set()
        
        if clean_line.startswith('def '):
            match = re.search(r'def \w+\((.*?)\):', clean_line)
            if match:
                params = match.group(1).split(',')
                for p in params:
                    p = p.strip()
                    if p and p != 'self':
                        new_locals.add(p)
        elif '=' in clean_line and not clean_line.startswith(('if ', 'for ', 'while ', 'elif ')):
            if inside_method:
                if any(op + '=' in clean_line for op in ['+', '-', '*', '/', '%', '&', '|', '^', '<', '>', '!', '=']):
                    return new_locals
                var_name = clean_line.split('=')[0].strip()
                if '.' in var_name:
                    return new_locals
                if var_name.isidentifier():
                    new_locals.add(var_name)
                else:
                    raise ValueError(f"Invalid variable name detected: '{var_name}' in line: '{original_line}'")            
        return new_locals

    def _transform_variables(self, clean_line: str, inside_method: bool, current_locals: set, new_locals: set) -> str:
        """Change this. -> self. and puts self. in front of class variables"""
        processed = re.sub(r'\bthis\.', 'self.', clean_line)

        if inside_method and not clean_line.startswith(('def ', 'class ')):
            processed = re.sub(
                r'\b\w+\b', 
                lambda m: self._replace_field_callback(m, processed, current_locals, new_locals), 
                processed
            )
        return processed

    def _manage_scope_opening(self, open_count: int, local_scopes: list[set], new_locals: set):
        """Take care for opening a new scope and adding new local variables to the stack."""
        for i in range(open_count):
            local_scopes.append(new_locals if i == 0 else set())
            new_locals = set()

    def _compute_indentation(self, processed_line: str, local_scopes: list[set]) -> str:
        """Take care for the indentation based on the current scope depth."""
        return '' if not processed_line else '    ' * len(local_scopes) + processed_line
    
    def transform(self, code: str) -> str:
        """
        Take care for monitoring the scope, local variables and parameters, 
        injects self. and calculates the indentation.
        """
        lines = code.split('\n')
        self._extract_class_variables(lines)
        
        output_lines = []
        local_scopes = []
        
        for line in lines:
            line = line.strip()
            if not line:
                output_lines.append("")
                continue
                
            close_count = line.count('}')
            open_count = line.count('{')
            clean_no_braces = line.replace('{', '').replace('}', '').strip()
            
            # Take care for closing scopes
            self._manage_scope_closing(close_count, local_scopes)
            
            # Extract variables that are seen in the local scope
            current_locals = self._collect_current_locals(local_scopes)
            inside_method = len(local_scopes) > 0
            new_locals = self._extract_new_locals(clean_no_braces, inside_method, line)
            
            # Transform the variables (this. -> self. and add self. to class vars)
            processed_line = self._transform_variables(clean_no_braces, inside_method, current_locals, new_locals)

            # Put the necessary identation
            final_line = self._compute_indentation(processed_line, local_scopes)
            if final_line:
                output_lines.append(final_line)

            # Take care for opening a new scope
            self._manage_scope_opening(open_count, local_scopes, new_locals)

        return '\n'.join(output_lines)