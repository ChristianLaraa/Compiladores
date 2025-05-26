#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compilador de Pseudo-C a RISC-V
Este compilador convierte programas escritos en una versión simplificada de C
a código ensamblador para la arquitectura RISC-V de 32 bits (RV32I).
"""

import re
import sys
from enum import Enum, auto

class Token:
    """Clase para representar un token del lenguaje"""
    
    def __init__(self, token_type, value, line=None):
        self.type = token_type
        self.value = value
        self.line = line
    
    def __str__(self):
        return f"Token({self.type}, '{self.value}')"
    
    def __repr__(self):
        return self.__str__()

class TokenType(Enum):
    """Enumeración de tipos de tokens del lenguaje"""
    
    VAR = auto()        # 'var'
    TYPE = auto()       # 'int', 'float', 'char', 'string'
    IDENTIFIER = auto() # identificadores de variables
    SEMICOLON = auto()  # ';'
    ASSIGN = auto()     # '='
    LPAREN = auto()     # '('
    RPAREN = auto()     # ')'
    LBRACE = auto()     # '{'
    RBRACE = auto()     # '}'
    NUMBER = auto()     # números literales
    STRING = auto()     # cadenas literales
    PLUS = auto()       # '+'
    MINUS = auto()      # '-'
    TIMES = auto()      # '*'
    DIVIDE = auto()     # '/'
    READ = auto()       # 'read'
    PRINT = auto()      # 'print'
    PRINTLN = auto()    # 'println'
    COMMA = auto()      # ','
    FOR = auto()        # 'for'
    EQUALS = auto()     # '=='
    END = auto()        # 'end'
    DOT = auto()        # '.'
    SIN = auto()        # 'sin'
    COS = auto()        # 'cos'
    TAN = auto()        # 'tan'
    EOF = auto()        # fin de archivo

class Lexer:
    """Analizador léxico que convierte texto a tokens"""
    
    def __init__(self, text):
        # Eliminar comentarios de estilo C
        self.text = self._remove_comments(text)
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
        self.line = 1
        
    def _remove_comments(self, text):
        """Elimina comentarios de estilo C (/* */) del texto"""
        return re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    
    def error(self):
        """Lanza un error de análisis léxico"""
        raise Exception(f'Error léxico: carácter inesperado "{self.current_char}" en línea {self.line}')
    
    def advance(self):
        """Avanza un carácter y actualiza current_char"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            if self.current_char == '\n':
                self.line += 1
    
    def peek(self):
        """Mira el siguiente carácter sin avanzar"""
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]
    
    def skip_whitespace(self):
        """Salta espacios en blanco"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def number(self):
        """Procesa un número (entero o flotante)"""
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        
        if '.' in result:
            return Token(TokenType.NUMBER, float(result), self.line)
        else:
            return Token(TokenType.NUMBER, int(result), self.line)
    
    def string(self):
        """Procesa una cadena literal"""
        result = ''
        # Saltar comilla inicial
        self.advance()
        
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        
        # Saltar comilla final
        if self.current_char == '"':
            self.advance()
        else:
            raise Exception(f'Error léxico: cadena sin cerrar en línea {self.line}')
            
        return Token(TokenType.STRING, result, self.line)
    
    def identifier(self):
        """Procesa un identificador o palabra clave"""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
            
        # Palabras clave
        if result == 'var':
            return Token(TokenType.VAR, result, self.line)
        elif result in ('int', 'float', 'string', 'char'):
            return Token(TokenType.TYPE, result, self.line)
        elif result == 'read':
            return Token(TokenType.READ, result, self.line)
        elif result == 'print':
            return Token(TokenType.PRINT, result, self.line)
        elif result == 'println':
            return Token(TokenType.PRINTLN, result, self.line)
        elif result == 'for':
            return Token(TokenType.FOR, result, self.line)
        elif result == 'end':
            return Token(TokenType.END, result, self.line)
        elif result == 'sin':
            return Token(TokenType.SIN, result, self.line)
        elif result == 'cos':
            return Token(TokenType.COS, result, self.line)
        elif result == 'tan':
            return Token(TokenType.TAN, result, self.line)
        else:
            return Token(TokenType.IDENTIFIER, result, self.line)
    
    def get_next_token(self):
        """Obtiene el siguiente token del texto de entrada"""
        while self.current_char is not None:
            
            # Saltar espacios en blanco
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Identificadores y palabras clave
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Números
            if self.current_char.isdigit():
                return self.number()
            
            # Cadenas
            if self.current_char == '"':
                return self.string()
            
            # Operadores y símbolos
            if self.current_char == ';':
                char = self.current_char
                self.advance()
                return Token(TokenType.SEMICOLON, char, self.line)
                
            if self.current_char == '=':
                self.advance()
                # Verificar si es '==' o solo '='
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUALS, '==', self.line)
                return Token(TokenType.ASSIGN, '=', self.line)
                
            if self.current_char == '(':
                char = self.current_char
                self.advance()
                return Token(TokenType.LPAREN, char, self.line)
                
            if self.current_char == ')':
                char = self.current_char
                self.advance()
                return Token(TokenType.RPAREN, char, self.line)
                
            if self.current_char == '{':
                char = self.current_char
                self.advance()
                return Token(TokenType.LBRACE, char, self.line)
                
            if self.current_char == '}':
                char = self.current_char
                self.advance()
                return Token(TokenType.RBRACE, char, self.line)
                
            if self.current_char == '+':
                char = self.current_char
                self.advance()
                return Token(TokenType.PLUS, char, self.line)
                
            if self.current_char == '-':
                char = self.current_char
                self.advance()
                return Token(TokenType.MINUS, char, self.line)
                
            if self.current_char == '*':
                char = self.current_char
                self.advance()
                return Token(TokenType.TIMES, char, self.line)
                
            if self.current_char == '/':
                char = self.current_char
                self.advance()
                return Token(TokenType.DIVIDE, char, self.line)
                
            if self.current_char == ',':
                char = self.current_char
                self.advance()
                return Token(TokenType.COMMA, char, self.line)
                
            if self.current_char == '.':
                char = self.current_char
                self.advance()
                return Token(TokenType.DOT, char, self.line)
            
            self.error()
        
        # Fin de archivo
        return Token(TokenType.EOF, None, self.line)

class SymbolTable:
    """Tabla de símbolos para el compilador"""
    
    def __init__(self):
        self.symbols = {}
        self.float_reg_idx = 0  # Índice para registros float (ft0-ft31)
        self.int_reg_idx = 0    # Índice para registros int (t0-t6, a0-a7)
        
    def add_variable(self, name, type_name):
        """Añade una variable a la tabla de símbolos"""
        if name in self.symbols:
            raise Exception(f"Error semántico: Variable '{name}' ya declarada")
        
        # Asignar un registro apropiado según el tipo
        register = None
        if type_name == 'float':
            register = f"ft{self.float_reg_idx}"
            self.float_reg_idx += 1
            # Verificar si hemos agotado los registros float disponibles
            if self.float_reg_idx > 31:
                # Implementar manejo de "spilling" si se desea (guardar en memoria)
                raise Exception("Error: Se han agotado los registros de punto flotante")
        elif type_name in ('int', 'char'):
            # Usar registros temporales t0-t6 (7 registros)
            if self.int_reg_idx < 7:
                register = f"t{self.int_reg_idx}"
            # Luego usar registros de argumento a0-a7 (8 registros)
            elif self.int_reg_idx < 15:
                register = f"a{self.int_reg_idx - 7}"
            else:
                # Implementar manejo de "spilling" si se desea (guardar en memoria)
                raise Exception("Error: Se han agotado los registros de entero")
            self.int_reg_idx += 1
        elif type_name == 'string':
            # Para strings, vamos a usar un puntero en un registro
            # y la cadena real en el segmento .data
            register = f"string_{name}"  # Esto sería un label en .data
        
        self.symbols[name] = {
            'type': type_name,
            'register': register
        }
        
        return self.symbols[name]
    
    def lookup(self, name):
        """Busca una variable en la tabla de símbolos"""
        if name not in self.symbols:
            raise Exception(f"Error semántico: Variable '{name}' no declarada")
        return self.symbols[name]
    
    def get_temp_var(self, type_name):
        """Crea una variable temporal y la añade a la tabla de símbolos"""
        name = f"T{len([s for s in self.symbols if s.startswith('T')])}"
        return self.add_variable(name, type_name)

class Parser:
    """Analizador sintáctico para el compilador"""
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.symbol_table = SymbolTable()
        self.code_generator = CodeGenerator(self.symbol_table)
    
    def error(self, expected_type=None):
        token_str = f"'{self.current_token.value}'" if self.current_token.value else self.current_token.type.name
        if expected_type:
            raise Exception(f"Error de sintaxis: Se esperaba {expected_type.name} pero se encontró {token_str} en línea {self.current_token.line}")
        else:
            raise Exception(f"Error de sintaxis: Token inesperado {token_str} en línea {self.current_token.line}")
    
    def eat(self, token_type):
        """Consume el token actual si coincide con el tipo esperado"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(token_type)
    
    def program(self):
        """
        program : declaration_list statement_list END DOT
        """
        # Sección inicial del código ensamblador
        self.code_generator.emit_program_header()
        
        # Procesar declaraciones de variables
        self.declaration_list()
        
        # Procesar instrucciones
        self.statement_list()
        
        # Fin del programa
        self.eat(TokenType.END)
        self.eat(TokenType.DOT)
        
        # Sección final del código ensamblador
        self.code_generator.emit_program_footer()
        
        return self.code_generator.get_code()
    
    def declaration_list(self):
        """
        declaration_list : (variable_declaration)*
        """
        while self.current_token.type == TokenType.VAR:
            self.variable_declaration()
    
    def variable_declaration(self):
        """
        variable_declaration : VAR TYPE IDENTIFIER SEMICOLON
        """
        self.eat(TokenType.VAR)
        
        type_token = self.current_token
        self.eat(TokenType.TYPE)
        
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Añadir variable a la tabla de símbolos
        self.symbol_table.add_variable(var_name, type_token.value)
        
        self.eat(TokenType.SEMICOLON)
    
    def statement_list(self):
        """
        statement_list : (statement)*
        """
        while self.current_token.type not in (TokenType.END, TokenType.EOF):
            self.statement()
    
    def statement(self):
        """
        statement : assignment_statement
                  | read_statement
                  | print_statement
                  | println_statement
                  | for_statement
        """
        if self.current_token.type == TokenType.IDENTIFIER:
            self.assignment_statement()
        elif self.current_token.type == TokenType.READ:
            self.read_statement()
        elif self.current_token.type == TokenType.PRINT:
            self.print_statement()
        elif self.current_token.type == TokenType.PRINTLN:
            self.println_statement()
        elif self.current_token.type == TokenType.FOR:
            self.for_statement()
        else:
            self.error()
    
    def assignment_statement(self):
        """
        assignment_statement : IDENTIFIER ASSIGN expr SEMICOLON
        """
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Verificar que la variable esté declarada
        var_info = self.symbol_table.lookup(var_name)
        
        self.eat(TokenType.ASSIGN)
        
        # Evaluar la expresión y obtener su tipo y registro temporal
        expr_result = self.expr()
        
        # Generar código para la asignación
        self.code_generator.emit_assignment(var_name, var_info['register'], var_info['type'],
                                          expr_result['register'], expr_result['type'])
        
        self.eat(TokenType.SEMICOLON)
    
    def read_statement(self):
        """
        read_statement : READ LPAREN IDENTIFIER RPAREN SEMICOLON
        """
        self.eat(TokenType.READ)
        self.eat(TokenType.LPAREN)
        
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Verificar que la variable esté declarada
        var_info = self.symbol_table.lookup(var_name)
        
        # Generar código para la lectura
        self.code_generator.emit_read(var_name, var_info['register'], var_info['type'])
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
    
    def print_statement(self):
        """
        print_statement : PRINT LPAREN print_args RPAREN SEMICOLON
        """
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        
        args = self.print_args()
        
        # Generar código para la impresión
        self.code_generator.emit_print(args)
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
    
    def println_statement(self):
        """
        println_statement : PRINTLN LPAREN print_args RPAREN SEMICOLON
        """
        self.eat(TokenType.PRINTLN)
        self.eat(TokenType.LPAREN)
        
        args = self.print_args()
        
        # Generar código para la impresión con salto de línea
        self.code_generator.emit_println(args)
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.SEMICOLON)
    
    def print_args(self):
        """
        print_args : (STRING | expr) (COMMA (STRING | expr))*
        """
        args = []
        
        # Primera expresión o cadena
        if self.current_token.type == TokenType.STRING:
            args.append({
                'type': 'string',
                'value': self.current_token.value
            })
            self.eat(TokenType.STRING)
        else:
            expr_result = self.expr()
            args.append({
                'type': expr_result['type'],
                'register': expr_result['register']
            })
        
        # Expresiones o cadenas adicionales
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            
            if self.current_token.type == TokenType.STRING:
                args.append({
                    'type': 'string',
                    'value': self.current_token.value
                })
                self.eat(TokenType.STRING)
            else:
                expr_result = self.expr()
                args.append({
                    'type': expr_result['type'],
                    'register': expr_result['register']
                })
        
        return args
    
    def for_statement(self):
        """
        for_statement : FOR LPAREN IDENTIFIER ASSIGN expr SEMICOLON expr RPAREN LBRACE statement_list RBRACE
        """
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)
        
        # Variable de control
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Verificar que la variable esté declarada
        var_info = self.symbol_table.lookup(var_name)
        
        self.eat(TokenType.ASSIGN)
        
        # Valor inicial
        start_expr = self.expr()
        
        # Generar código para la asignación inicial
        self.code_generator.emit_assignment(var_name, var_info['register'], var_info['type'],
                                          start_expr['register'], start_expr['type'])
        
        self.eat(TokenType.SEMICOLON)
        
        # Valor final
        end_expr = self.expr()
        
        # Generar etiquetas para el bucle
        loop_start_label = self.code_generator.get_new_label("for_start")
        loop_end_label = self.code_generator.get_new_label("for_end")
        
        # Generar código para el inicio del bucle
        self.code_generator.emit_for_start(loop_start_label, var_name, var_info['register'], 
                                         var_info['type'], end_expr['register'], end_expr['type'],
                                         loop_end_label)
        
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        
        # Cuerpo del bucle
        self.statement_list()
        
        # Generar código para el final del bucle
        self.code_generator.emit_for_end(loop_start_label, var_name, var_info['register'], 
                                       var_info['type'])
        
        self.eat(TokenType.RBRACE)
        
        # Emitir etiqueta de fin de bucle
        self.code_generator.emit_label(loop_end_label)
    
    def expr(self):
        """
        expr : term ((PLUS | MINUS) term)*
        """
        result = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                term_result = self.term()
                result = self.code_generator.emit_binary_op('+', result, term_result)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                term_result = self.term()
                result = self.code_generator.emit_binary_op('-', result, term_result)
        
        return result
    
    def term(self):
        """
        term : factor ((TIMES | DIVIDE) factor)*
        """
        result = self.factor()
        
        while self.current_token.type in (TokenType.TIMES, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.TIMES:
                self.eat(TokenType.TIMES)
                factor_result = self.factor()
                result = self.code_generator.emit_binary_op('*', result, factor_result)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
                factor_result = self.factor()
                result = self.code_generator.emit_binary_op('/', result, factor_result)
        
        return result
    
    def factor(self):
        """
        factor : NUMBER
               | IDENTIFIER
               | LPAREN expr RPAREN
               | (SIN | COS | TAN) LPAREN expr RPAREN
        """
        token = self.current_token
        
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            # Determinar el tipo del número
            type_name = 'float' if isinstance(token.value, float) else 'int'
            # Generar código para cargar el número
            temp_var = self.symbol_table.get_temp_var(type_name)
            self.code_generator.emit_load_constant(temp_var['register'], token.value, type_name)
            return {'type': type_name, 'register': temp_var['register']}
            
        elif token.type == TokenType.IDENTIFIER:
            var_name = token.value
            self.eat(TokenType.IDENTIFIER)
            # Verificar que la variable esté declarada
            var_info = self.symbol_table.lookup(var_name)
            return {'type': var_info['type'], 'register': var_info['register']}
            
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.expr()
            self.eat(TokenType.RPAREN)
            return result
            
        elif token.type in (TokenType.SIN, TokenType.COS, TokenType.TAN):
            func_type = token.type
            func_name = token.value
            
            if func_type == TokenType.SIN:
                self.eat(TokenType.SIN)
            elif func_type == TokenType.COS:
                self.eat(TokenType.COS)
            elif func_type == TokenType.TAN:
                self.eat(TokenType.TAN)
                
            self.eat(TokenType.LPAREN)
            arg_result = self.expr()
            self.eat(TokenType.RPAREN)
            
            # Verificar que el argumento sea de tipo float
            if arg_result['type'] != 'float':
                raise Exception(f"Error semántico: La función {func_name} requiere un argumento de tipo float")
            
            # Generar código para la función matemática
            temp_var = self.symbol_table.get_temp_var('float')
            self.code_generator.emit_math_function(func_name, arg_result['register'], temp_var['register'])
            
            return {'type': 'float', 'register': temp_var['register']}
        else:
            self.error()

class CodeGenerator:
    """Generador de código ensamblador RISC-V"""
    
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.code = []
        self.data_section = []
        self.label_count = 0
        self.string_count = 0
    
    def emit(self, instruction):
        """Emite una instrucción de código ensamblador"""
        self.code.append(instruction)
    
    def emit_data(self, data):
        """Emite una definición de datos para el segmento .data"""
        self.data_section.append(data)
    
    def get_new_label(self, prefix="label"):
        """Genera una nueva etiqueta única"""
        label = f"{prefix}_{self.label_count}"
        self.label_count += 1
        return label
    
    def emit_label(self, label):
        """Emite una etiqueta en el código"""
        self.emit(f"{label}:")
    
    def emit_program_header(self):
        """Emite el encabezado del programa ensamblador"""
        self.emit(".text")
        self.emit(".globl main")
        self.emit("main:")
        # Guardar el registro de retorno
        self.emit("    addi sp, sp, -4")
        self.emit("    sw ra, 0(sp)")
    
    def emit_program_footer(self):
        """Emite el pie del programa ensamblador"""
        # Cargar el registro de retorno
        self.emit("    lw ra, 0(sp)")
        self.emit("    addi sp, sp, 4")
        # Salir del programa
        self.emit("    li a7, 10")  # Syscall número 10 (exit)
        self.emit("    ecall")
        
        # Sección de datos
        if self.data_section:
            self.emit("")
            self.emit(".data")
            for data in self.data_section:
                self.emit(data)
    
    def get_code(self):
        """Obtiene el código ensamblador generado"""
        return "\n".join(self.code)
    
    def add_string_to_data(self, string):
        """Añade una cadena literal al segmento .data y devuelve su etiqueta"""
        label = f"string_{self.string_count}"
        self.string_count += 1
        # Escapar comillas dobles en la cadena
        escaped_string = string.replace('"', '\\"')
        self.emit_data(f'{label}: .string "{escaped_string}"')
        return label
    
    def emit_load_constant(self, register, value, type_name):
        """Emite código para cargar una constante en un registro"""
        if type_name == 'float':
            # Cargar un flotante a un registro de punto flotante
            if value == 0.0:
                self.emit(f"    fmv.s.x {register}, zero")
            else:
                # Añadir el flotante al segmento .data
                label = f"float_{self.label_count}"
                self.label_count += 1
                self.emit_data(f"{label}: .float {value}")
                # Cargar el flotante desde memoria
                self.emit(f"    la t0, {label}")
                self.emit(f"    flw {register}, 0(t0)")
        elif type_name == 'int':
            # Cargar un entero a un registro de entero
            self.emit(f"    li {register}, {value}")
        # Nota: No hay constantes de tipo string aquí
    
    def emit_assignment(self, var_name, var_register, var_type, expr_register, expr_type):
        """Emite código para una asignación"""
        # Convertir tipo si es necesario
        if var_type == expr_type:
            # Mismos tipos, copiar directamente
            if var_type == 'float':
                self.emit(f"    fmv.s {var_register}, {expr_register}")
            elif var_type in ('int', 'char'):
                self.emit(f"    mv {var_register}, {expr_register}")
            elif var_type == 'string':
                # Para strings, copiar la dirección
                self.emit(f"    la {var_register}, {expr_register}")
        else:
            # Conversión de tipos
            if var_type == 'float' and expr_type == 'int':
                # Convertir int a float
                self.emit(f"    fcvt.s.w {var_register}, {expr_register}")
            elif var_type == 'int' and expr_type == 'float':
                # Convertir float a int (truncar)
                self.emit(f"    fcvt.w.s {var_register}, {expr_register}, rtz")
            else:
                raise Exception(f"Error semántico: No se puede convertir de {expr_type} a {var_type}")
    
    def emit_read(self, var_name, var_register, var_type):
        """Emite código para una instrucción read"""
        if var_type == 'int':
            # read(int_var)
            self.emit(f"    # Lectura de entero para {var_name}")
            self.emit(f"    li a7, 5")  # Syscall número 5 (read_int)
            self.emit(f"    ecall")
            self.emit(f"    mv {var_register}, a0")
        elif var_type == 'float':
            # read(float_var)
            self.emit(f"    # Lectura de flotante para {var_name}")
            self.emit(f"    li a7, 6")  # Syscall número 6 (read_float)
            self.emit(f"    ecall")
            self.emit(f"    fmv.s {var_register}, fa0")
        elif var_type == 'char':
            # read(char_var)
            self.emit(f"    # Lectura de carácter para {var_name}")
            self.emit(f"    li a7, 12")  # Syscall número 12 (read_char)
            self.emit(f"    ecall")
            self.emit(f"    mv {var_register}, a0")
        elif var_type == 'string':
            # read(string_var)
            self.emit(f"    # Lectura de cadena para {var_name}")
            # Asignar un búfer para la cadena en .data
            buffer_label = f"string_buffer_{var_name}"
            self.emit_data(f"{buffer_label}: .space 100")  # Espacio para 100 caracteres
            
            # Emitir syscall para read_string
            self.emit(f"    la a0, {buffer_label}")  # Dirección del buffer
            self.emit(f"    li a1, 100")           # Longitud máxima
            self.emit(f"    li a7, 8")             # Syscall número 8 (read_string)
            self.emit(f"    ecall")
            
            # Actualizar la variable para que apunte al buffer
            self.emit(f"    la {var_register}, {buffer_label}")
        else:
            raise Exception(f"Error semántico: Tipo {var_type} no soportado para read")
    
    def emit_print(self, args):
        """Emite código para una instrucción print"""
        for arg in args:
            if arg['type'] == 'string' and 'value' in arg:
                # Cadena literal
                string_label = self.add_string_to_data(arg['value'])
                self.emit(f"    # Imprimir cadena")
                self.emit(f"    la a0, {string_label}")
                self.emit(f"    li a7, 4")  # Syscall número 4 (print_string)
                self.emit(f"    ecall")
            elif arg['type'] == 'string':
                # Variable de tipo string
                self.emit(f"    # Imprimir variable string")
                self.emit(f"    mv a0, {arg['register']}")
                self.emit(f"    li a7, 4")  # Syscall número 4 (print_string)
                self.emit(f"    ecall")
            elif arg['type'] == 'int':
                # Entero
                self.emit(f"    # Imprimir entero")
                self.emit(f"    mv a0, {arg['register']}")
                self.emit(f"    li a7, 1")  # Syscall número 1 (print_int)
                self.emit(f"    ecall")
            elif arg['type'] == 'float':
                # Flotante
                self.emit(f"    # Imprimir flotante")
                self.emit(f"    fmv.s fa0, {arg['register']}")
                self.emit(f"    li a7, 2")  # Syscall número 2 (print_float)
                self.emit(f"    ecall")
            elif arg['type'] == 'char':
                # Carácter
                self.emit(f"    # Imprimir carácter")
                self.emit(f"    mv a0, {arg['register']}")
                self.emit(f"    li a7, 11")  # Syscall número 11 (print_char)
                self.emit(f"    ecall")
    
    def emit_println(self, args):
        """Emite código para una instrucción println"""
        # Primero imprimir los argumentos
        self.emit_print(args)
        
        # Luego imprimir un salto de línea
        self.emit(f"    # Imprimir salto de línea")
        self.emit(f"    li a0, 10")  # ASCII de nueva línea
        self.emit(f"    li a7, 11")  # Syscall número 11 (print_char)
        self.emit(f"    ecall")
    
    def emit_for_start(self, loop_start_label, var_name, var_register, var_type, 
                     end_reg, end_type, loop_end_label):
        """Emite código para el inicio de un bucle for"""
        self.emit(f"    # Inicio del bucle for con {var_name}")
        self.emit_label(loop_start_label)
        
        # Comparar la variable de control con el valor final
        if var_type == 'int':
            self.emit(f"    # Comparar {var_name} <= fin")
            self.emit(f"    ble {var_register}, {end_reg}, 1f")
            self.emit(f"    j {loop_end_label}")
            self.emit(f"1:")
        elif var_type == 'float':
            # Para comparaciones de punto flotante, necesitamos usar fle.s
            self.emit(f"    # Comparar {var_name} <= fin")
            self.emit(f"    fle.s t0, {var_register}, {end_reg}")
            self.emit(f"    beqz t0, {loop_end_label}")
    
    def emit_for_end(self, loop_start_label, var_name, var_register, var_type):
        """Emite código para el final de un bucle for"""
        self.emit(f"    # Incrementar {var_name} y volver al inicio del bucle")
        if var_type == 'int':
            self.emit(f"    addi {var_register}, {var_register}, 1")
        elif var_type == 'float':
            # Cargar 1.0 y sumarlo
            temp_label = f"float_one_{self.label_count}"
            self.label_count += 1
            self.emit_data(f"{temp_label}: .float 1.0")
            self.emit(f"    la t0, {temp_label}")
            self.emit(f"    flw ft11, 0(t0)")
            self.emit(f"    fadd.s {var_register}, {var_register}, ft11")
        
        self.emit(f"    j {loop_start_label}")
    
    def emit_binary_op(self, op, left, right):
        """Emite código para una operación binaria y devuelve el registro resultado"""
        # Determinar el tipo de resultado según las reglas de promoción
        result_type = self._get_result_type(op, left['type'], right['type'])
        
        # Obtener un registro temporal para el resultado
        temp_var = self.symbol_table.get_temp_var(result_type)
        result_reg = temp_var['register']
        
        # Convertir operandos si es necesario
        left_reg = self._ensure_type(left['register'], left['type'], result_type)
        right_reg = self._ensure_type(right['register'], right['type'], result_type)
        
        # Emitir la operación según el tipo
        if result_type == 'float':
            if op == '+':
                self.emit(f"    fadd.s {result_reg}, {left_reg}, {right_reg}")
            elif op == '-':
                self.emit(f"    fsub.s {result_reg}, {left_reg}, {right_reg}")
            elif op == '*':
                self.emit(f"    fmul.s {result_reg}, {left_reg}, {right_reg}")
            elif op == '/':
                self.emit(f"    fdiv.s {result_reg}, {left_reg}, {right_reg}")
        elif result_type == 'int':
            if op == '+':
                self.emit(f"    add {result_reg}, {left_reg}, {right_reg}")
            elif op == '-':
                self.emit(f"    sub {result_reg}, {left_reg}, {right_reg}")
            elif op == '*':
                self.emit(f"    mul {result_reg}, {left_reg}, {right_reg}")
            elif op == '/':
                # Para división de enteros que produce flotante
                if self._get_result_type('/', 'int', 'int') == 'float':
                    # Convertir enteros a float
                    float_left = self.symbol_table.get_temp_var('float')['register']
                    float_right = self.symbol_table.get_temp_var('float')['register']
                    self.emit(f"    fcvt.s.w {float_left}, {left_reg}")
                    self.emit(f"    fcvt.s.w {float_right}, {right_reg}")
                    self.emit(f"    fdiv.s {result_reg}, {float_left}, {float_right}")
                else:
                    self.emit(f"    div {result_reg}, {left_reg}, {right_reg}")
        
        return {'type': result_type, 'register': result_reg}
    
    def _get_result_type(self, op, left_type, right_type):
        """Determina el tipo de resultado para una operación binaria"""
        # Reglas de promoción de tipos
        if left_type == 'float' or right_type == 'float':
            return 'float'
        elif op == '/' and left_type == 'int' and right_type == 'int':
            # División de enteros produce flotante según las reglas especificadas
            return 'float'
        else:
            return 'int'
    
    def _ensure_type(self, reg, current_type, target_type):
        """Asegura que un valor esté en el tipo correcto, convirtiendo si es necesario"""
        if current_type == target_type:
            return reg
        
        # Convertir entre tipos
        if current_type == 'int' and target_type == 'float':
            # Convertir int a float
            temp_reg = self.symbol_table.get_temp_var('float')['register']
            self.emit(f"    fcvt.s.w {temp_reg}, {reg}")
            return temp_reg
        elif current_type == 'float' and target_type == 'int':
            # Convertir float a int
            temp_reg = self.symbol_table.get_temp_var('int')['register']
            self.emit(f"    fcvt.w.s {temp_reg}, {reg}, rtz")
            return temp_reg
        else:
            raise Exception(f"Error semántico: No se puede convertir de {current_type} a {target_type}")
    
    def emit_math_function(self, func_name, arg_reg, result_reg):
        """Emite código para una función matemática (sin, cos, tan)"""
        # Cargar la dirección de la función
        self.emit(f"    # Llamada a función matemática {func_name}")
        
        # Guardar registros que se usan durante la llamada
        self.emit(f"    addi sp, sp, -8")
        self.emit(f"    sw ra, 0(sp)")
        self.emit(f"    fsw {arg_reg}, 4(sp)")
        
        # Mover el argumento al registro fa0
        self.emit(f"    fmv.s fa0, {arg_reg}")
        
        # Llamar a la función de la librería matemática
        self.emit(f"    call {func_name}")
        
        # Mover el resultado al registro destino
        self.emit(f"    fmv.s {result_reg}, fa0")
        
        # Restaurar registros
        self.emit(f"    lw ra, 0(sp)")
        self.emit(f"    flw {arg_reg}, 4(sp)")
        self.emit(f"    addi sp, sp, 8")

class Compiler:
    """Clase principal del compilador"""
    
    def __init__(self):
        pass
    
    def compile(self, code):
        """Compila el código fuente y devuelve el código ensamblador"""
        try:
            # Inicializar el lexer
            lexer = Lexer(code)
            
            # Inicializar el parser
            parser = Parser(lexer)
            
            # Analizar y generar código
            assembly_code = parser.program()
            
            return assembly_code
        except Exception as e:
            return f"Error de compilación: {str(e)}"


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python compiler.py <archivo_fuente> [archivo_salida]")
        return
    
    input_file = sys.argv[1]
    
    # Determinar archivo de salida
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # Por defecto, usar el mismo nombre pero con extensión .s
        output_file = input_file.rsplit('.', 1)[0] + '.s'
    
    try:
        # Leer archivo de entrada
        with open(input_file, 'r') as f:
            source_code = f.read()
        
        # Compilar
        compiler = Compiler()
        assembly_code = compiler.compile(source_code)
        
        # Escribir archivo de salida
        with open(output_file, 'w') as f:
            f.write(assembly_code)
        
        print(f"Compilación exitosa. Código ensamblador guardado en {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()