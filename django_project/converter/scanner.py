import re
from .scan_exceptions import JavaSyntaxError

class JavaScanner:
    def __init__(self):
        self.class_vars = set()

    def _is_field_definition(self, line: str, indentation_depth: int) -> bool:
        return False if indentation_depth != 1 else bool(re.match(r'^\s*self\.[a-zA-Z_][a-zA-Z0-9_]*(\s*=\s*.*)?\s*$', line))

    def _extract_class_variables(self, lines: list[str]):
        """Scan the code and extract all member-variables of the class."""
        self.class_vars.clear()
        identation_level = 0
        for line in lines:
            line = line.strip()
            if identation_level == 1 and not line.startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'elif ', 'else ', '{', '}')):
                if '=' in line:

                    var_name = line.split('=')[0].strip()
                else:

                    var_name = line.strip()
                if var_name and var_name.isidentifier():

                    self.class_vars.add(var_name)
            identation_level += line.count('{') - line.count('}')

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
                raise JavaSyntaxError("Unmatched closing brace '}' detected in the code.")

    def _collect_current_locals(self, local_scopes: list[set]) -> set:
        """Make a set from all variables that are seen in the current scope"""
        current_locals = set()
        for scope in local_scopes:
            current_locals.update(scope)
        return current_locals

    def _extract_new_locals(self, clean_line: str, inside_method: bool, original_line: str) -> set:
        new_locals = set()

        if any(char in clean_line for char in ['"', "'"]) or 'print' in clean_line:
            return set()

        if clean_line.startswith(('if ', 'while ', 'elif ', 'else:')):
            return set()

        if clean_line.startswith('for '):
            match = re.search(r'for\s*\(\w+\s+(\w+)', clean_line)
            if match:
                new_locals.add(match.group(1))
            return new_locals
        elif clean_line.startswith('def '):
            match = re.search(r'def [\w\_]+\((.*?)\):', clean_line)
            if match:
                for p in match.group(1).split(','):
                    p = p.strip()
                    if p and p != 'self':
                        new_locals.add(p)
        elif '=' in clean_line:
            if inside_method:
                if any(op + '=' in clean_line for op in ['+', '-', '*', '/', '%', '&', '|', '^', '<', '>', '!']):
                    return set()
                
                var_name = clean_line.split('=')[0].strip()
                
                if '.' in var_name or var_name in ['in', 'for', 'while', 'if']:
                    return set()
                    
                if var_name.isidentifier():
                    new_locals.add(var_name)
                else:
                    return set()        
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
            line = self._transform_variables(clean_no_braces, inside_method, current_locals, new_locals)

            # Put the necessary identation
            line = self._compute_indentation(line, local_scopes)
            if line and not self._is_field_definition(line, len(local_scopes)):
                output_lines.append(line)

            # Take care for opening a new scope
            self._manage_scope_opening(open_count, local_scopes, new_locals)

        return '\n'.join(output_lines)