import re
import math
from collections import defaultdict


class MiniCInteractiveInterpreter:
    def __init__(self):
        self.variables = {}  # {nombre: (tipo, valor)}
        self.temp_count = 0
        self.current_line = 0
        self.code_buffer = []
        self.in_for_loop = False
        self.for_loop_info = {}
        self.in_block = False
        self.block_lines = []
        self.remove_comments = True
        self.running = True
        self.prompt = "miniC> "
        self.multiline_prompt = "....> "

        # Configuración de colores para mensajes
        self.COLORS = {
            'error': '\033[91m',
            'success': '\033[92m',
            'warning': '\033[93m',
            'info': '\033[94m',
            'reset': '\033[0m'
        }

    def color_print(self, text, color=None):
        """Imprime texto con color"""
        if color in self.COLORS:
            print(f"{self.COLORS[color]}{text}{self.COLORS['reset']}")
        else:
            print(text)

    def remove_comments(self, code):
        """Elimina comentarios /* ... */ del código"""
        return re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

    def preprocess_line(self, line):
        """Preprocesa una línea de código"""
        line = line.strip()
        if self.remove_comments:
            line = self.remove_comments(line)
        return line

    def parse_variable_declaration(self, line):
        """Analiza declaración de variable: var tipo nombre;"""
        if not line.startswith('var '):
            raise SyntaxError("Declaración debe comenzar con 'var'")

        parts = line[4:].rstrip(';').split()
        if len(parts) < 2:
            raise SyntaxError("Formato incorrecto. Uso: var tipo nombre;")

        var_type = parts[0]
        var_name = parts[1]

        if var_name in self.variables:
            raise NameError(f"Variable '{var_name}' ya declarada")

        # Valores por defecto según tipo
        if var_type == 'int':
            self.variables[var_name] = ('int', 0)
        elif var_type == 'float':
            self.variables[var_name] = ('float', 0.0)
        elif var_type == 'string':
            self.variables[var_name] = ('string', "")
        elif var_type == 'char':
            self.variables[var_name] = ('char', '\0')
        else:
            raise TypeError(f"Tipo '{var_type}' no soportado")

    def execute_read(self, line):
        """Ejecuta read(variable)"""
        match = re.match(r'read\((\w+)\);', line)
        if not match:
            raise SyntaxError("Formato incorrecto. Uso: read(variable);")

        var_name = match.group(1)
        if var_name not in self.variables:
            raise NameError(f"Variable '{var_name}' no declarada")

        var_type, _ = self.variables[var_name]
        value = input("> ")

        try:
            if var_type == 'int':
                self.variables[var_name] = (var_type, int(value))
            elif var_type == 'float':
                self.variables[var_name] = (var_type, float(value))
            elif var_type == 'char':
                self.variables[var_name] = (var_type, value[0] if value else '\0')
            elif var_type == 'string':
                self.variables[var_name] = (var_type, value)
        except ValueError:
            raise ValueError(f"Valor inválido para tipo {var_type}")

    def execute_print(self, line, newline=False):
        """Ejecuta print(...) o println(...)"""
        match = re.match(r'(?:print|println)\((.*)\);', line)
        if not match:
            raise SyntaxError("Formato incorrecto. Uso: print(expr1, expr2, ...);")

        content = match.group(1)
        args = self.parse_print_arguments(content)

        output = []
        for arg in args:
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                output.append(arg[1:-1])
            elif arg in self.variables:
                _, value = self.variables[arg]
                output.append(str(value))
            else:
                try:
                    # Intentar evaluar como expresión
                    value = self.evaluate_expression(arg)
                    output.append(str(value))
                except:
                    raise NameError(f"Variable o expresión '{arg}' no reconocida")

        print(''.join(output), end='\n' if newline else '')

    def parse_print_arguments(self, content):
        """Analiza los argumentos de print/println"""
        args = []
        current = ""
        in_string = False
        quote_char = None

        for char in content:
            if char in ('"', "'") and not in_string:
                in_string = True
                quote_char = char
                current += char
            elif char == quote_char and in_string:
                in_string = False
                current += char
                args.append(current)
                current = ""
            elif in_string:
                current += char
            elif char == ',' and not in_string:
                if current.strip():
                    args.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            args.append(current.strip())

        return args

    def execute_assignment(self, line):
        """Ejecuta asignación: variable = expresión;"""
        parts = line.split('=', 1)
        if len(parts) != 2:
            raise SyntaxError("Formato incorrecto. Uso: variable = expresión;")

        var_name = parts[0].strip()
        expr = parts[1].rstrip(';').strip()

        if var_name not in self.variables:
            raise NameError(f"Variable '{var_name}' no declarada")

        var_type, _ = self.variables[var_name]
        value = self.evaluate_expression(expr)

        # Conversión de tipos
        if var_type == 'int':
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            elif not isinstance(value, int):
                raise TypeError(f"No se puede asignar {type(value).__name__} a int")
        elif var_type == 'float':
            value = float(value)
        elif var_type == 'string':
            value = str(value)
        elif var_type == 'char':
            if not isinstance(value, str) or len(value) != 1:
                raise ValueError("Se requiere un solo carácter")

        self.variables[var_name] = (var_type, value)

    def evaluate_expression(self, expr):
        """Evalúa una expresión matemática o de cadena"""
        expr = expr.strip()

        # Manejar paréntesis
        while expr.startswith('(') and expr.endswith(')'):
            expr = expr[1:-1].strip()

        # Funciones matemáticas
        func_match = re.match(r'(sin|cos|tan)\((.+)\)', expr)
        if func_match:
            func = func_match.group(1)
            arg = self.evaluate_expression(func_match.group(2))

            if not isinstance(arg, (int, float)):
                raise TypeError(f"La función {func} requiere argumento numérico")

            if func == 'sin':
                return math.sin(arg)
            elif func == 'cos':
                return math.cos(arg)
            elif func == 'tan':
                return math.tan(arg)

        # Operadores binarios
        for op in ['+', '-', '*', '/']:
            if op in expr:
                left, right = expr.split(op, 1)
                left_val = self.evaluate_expression(left.strip())
                right_val = self.evaluate_expression(right.strip())

                if op == '+':
                    if isinstance(left_val, str) or isinstance(right_val, str):
                        return str(left_val) + str(right_val)
                    return left_val + right_val
                elif op == '-':
                    if isinstance(left_val, str) or isinstance(right_val, str):
                        raise TypeError("No se puede restar cadenas")
                    return left_val - right_val
                elif op == '*':
                    if isinstance(left_val, str) or isinstance(right_val, str):
                        raise TypeError("No se puede multiplicar cadenas")
                    return left_val * right_val
                elif op == '/':
                    if isinstance(left_val, str) or isinstance(right_val, str):
                        raise TypeError("No se puede dividir cadenas")
                    if right_val == 0:
                        raise ZeroDivisionError("División por cero")
                    return left_val / right_val

        # Variables o literales
        if expr in self.variables:
            return self.variables[expr][1]
        elif expr.replace('.', '', 1).isdigit():
            return float(expr) if '.' in expr else int(expr)
        elif (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        else:
            raise ValueError(f"Expresión no reconocida: {expr}")

    def execute_for_loop(self, line):
        """Maneja bucles for: for (var = inicio; fin) { ... }"""
        if not self.in_for_loop:
            # Inicio del bucle
            match = re.match(r'for\s*\(\s*(\w+)\s*=\s*(\d+)\s*;\s*(\d+)\s*\)', line)
            if not match:
                raise SyntaxError("Formato incorrecto. Uso: for (var = inicio; fin) { ... }")

            var_name = match.group(1)
            start = int(match.group(2))
            end = int(match.group(3))

            if var_name not in self.variables:
                raise NameError(f"Variable '{var_name}' no declarada")

            var_type, _ = self.variables[var_name]
            if var_type != 'int':
                raise TypeError("La variable de control debe ser int")

            self.for_loop_info = {
                'var_name': var_name,
                'start': start,
                'current': start,
                'end': end,
                'loop_start': len(self.block_lines) + 1
            }

            self.variables[var_name] = (var_type, start)
            self.in_for_loop = True
            self.in_block = True
        else:
            # Dentro del bucle
            if line.strip() == '}':
                # Fin del bloque - verificar condición
                var_name = self.for_loop_info['var_name']
                var_type, current = self.variables[var_name]
                end = self.for_loop_info['end']

                if current < end:
                    # Incrementar y repetir
                    self.variables[var_name] = (var_type, current + 1)
                    self.execute_block(self.block_lines)
                else:
                    # Fin del bucle
                    self.in_for_loop = False
                    self.for_loop_info = {}
                    self.in_block = False
                    self.block_lines = []
            else:
                self.block_lines.append(line)

    def execute_block(self, lines):
        """Ejecuta un bloque de código"""
        saved_vars = self.variables.copy()

        for line in lines:
            self.execute_line(line)

        # Restaurar variables (excepto la de control del bucle)
        if self.in_for_loop:
            var_name = self.for_loop_info['var_name']
            self.variables = {var_name: self.variables[var_name]}
            self.variables.update(saved_vars)

    def execute_line(self, line):
        """Ejecuta una línea de código"""
        line = self.preprocess_line(line)
        if not line:
            return

        try:
            if line.startswith('var '):
                self.parse_variable_declaration(line)
            elif line.startswith('read('):
                self.execute_read(line)
            elif line.startswith('print('):
                self.execute_print(line)
            elif line.startswith('println('):
                self.execute_print(line, newline=True)
            elif line.startswith('for '):
                self.execute_for_loop(line)
            elif '=' in line:
                self.execute_assignment(line)
            elif line == 'end.':
                self.running = False
            elif line == '{':
                self.in_block = True
            elif line == '}':
                if self.in_for_loop:
                    self.execute_for_loop(line)
                else:
                    self.in_block = False
            else:
                raise SyntaxError(f"Instrucción no reconocida: {line}")
        except Exception as e:
            self.color_print(f"Error: {e}", 'error')

    def show_help(self):
        """Muestra ayuda interactiva"""
        help_text = """
        Mini C Interpreter Help:
        - Declaración de variables: var tipo nombre; (tipos: int, float, string, char)
        - Asignación: variable = expresión;
        - Entrada: read(variable);
        - Salida: print(expr1, expr2, ...); o println(...) para salto de línea
        - Bucles: for (var = inicio; fin) { ... }
        - Funciones matemáticas: sin(expr), cos(expr), tan(expr)
        - Terminar programa: end.
        - Comentarios: /* ... */
        """
        self.color_print(help_text, 'info')

    def show_variables(self):
        """Muestra las variables declaradas"""
        if not self.variables:
            self.color_print("No hay variables declaradas.", 'info')
            return

        self.color_print("\nVariables declaradas:", 'info')
        for name, (var_type, value) in self.variables.items():
            print(f"  {name}: {var_type} = {value}")

    def start_interactive(self):
        """Inicia el intérprete interactivo"""
        self.color_print("Mini C Interactive Interpreter", 'success')
        self.color_print("Type 'help' for help, 'vars' to show variables, 'exit' to quit\n", 'info')

        while self.running:
            try:
                if not self.in_block:
                    line = input(self.prompt).strip()
                else:
                    line = input(self.multiline_prompt).strip()

                if not line:
                    continue

                # Comandos especiales
                if line.lower() == 'help' and not self.in_block:
                    self.show_help()
                    continue
                elif line.lower() == 'vars' and not self.in_block:
                    self.show_variables()
                    continue
                elif line.lower() in ('exit', 'quit') and not self.in_block:
                    break

                # Ejecutar línea de código
                self.execute_line(line)

                # Si estamos en un bloque, almacenar líneas
                if self.in_block and line != '{' and not line.startswith('for '):
                    self.block_lines.append(line)

            except KeyboardInterrupt:
                self.color_print("\nUse 'exit' or 'quit' to exit", 'warning')
            except EOFError:
                break
            except Exception as e:
                self.color_print(f"Error: {e}", 'error')


if __name__ == "__main__":
    interpreter = MiniCInteractiveInterpreter()
    interpreter.start_interactive()