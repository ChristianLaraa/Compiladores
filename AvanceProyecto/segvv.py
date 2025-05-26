
from math import sin, cos, tan
import re

class InterpreteMiniPascal:
    def __init__(self):
        self.tabla_simbolos = {}
        self.lineas = []
        self.indice = 0

    def eliminar_comentarios(self, codigo):
        return re.sub(r'\(\*.*?\*\)', '', codigo, flags=re.DOTALL)

    def dividir_lineas(self, codigo):
        self.lineas = [linea.strip() for linea in codigo.split('\n') if linea.strip()]
        self.indice = 0

    def declarar_variable(self, nombre, tipo):
        if nombre in self.tabla_simbolos:
            raise Exception(f"Error: La variable '{nombre}' ya fue declarada.")
        self.tabla_simbolos[nombre] = {"tipo": tipo, "valor": None}

    def procesar_declaracion(self, linea):
        patron = r'var\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(integer|real|string|char);'
        coincidencia = re.match(patron, linea)
        if not coincidencia:
            raise Exception(f"Error de sintaxis en declaración: {linea}")
        self.declarar_variable(coincidencia.group(1), coincidencia.group(2))

    def infija_a_postfija(self, tokens):
        precedencia = {'+':1, '-':1, '*':2, '/':2}
        salida, pila = [], []
        for token in tokens:
            if token in precedencia:
                while pila and precedencia.get(pila[-1], 0) >= precedencia[token]:
                    salida.append(pila.pop())
                pila.append(token)
            elif token == '(':
                pila.append(token)
            elif token == ')':
                while pila[-1] != '(':
                    salida.append(pila.pop())
                pila.pop()
            else:
                salida.append(token)
        while pila:
            salida.append(pila.pop())
        return salida

    def evaluar_postfija(self, postfija):
        pila = []
        for token in postfija:
            if token in '+-*/':
                b = pila.pop()
                a = pila.pop()
                if token == '+': pila.append(a + b)
                elif token == '-': pila.append(a - b)
                elif token == '*': pila.append(a * b)
                elif token == '/': pila.append(float(a) / b)
            elif token in self.tabla_simbolos:
                valor = self.tabla_simbolos[token]['valor']
                if valor is None: raise Exception(f"La variable '{token}' no tiene valor.")
                pila.append(valor)
            elif re.match(r'\d+(\.\d+)?', token):
                pila.append(float(token) if '.' in token else int(token))
            elif token in ['sin', 'cos', 'tan']:
                a = pila.pop()
                pila.append(getattr(__import__('math'), token)(a))
        return pila[0]

    def evaluar_expresion(self, expresion):
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\d+\.\d+|\d+|[()+\-*/]', expresion)
        postfija = self.infija_a_postfija(tokens)
        return self.evaluar_postfija(postfija)

    def ejecutar_linea(self, linea):
        if linea.startswith('var'):
            self.procesar_declaracion(linea)
        elif linea.startswith('leer('):
            variable = re.match(r'leer\((\w+)\);', linea).group(1)
            if variable not in self.tabla_simbolos:
                raise Exception(f"Variable '{variable}' no declarada.")
            entrada = input(f"Ingrese valor para {variable}: ")
            tipo = self.tabla_simbolos[variable]['tipo']
            if tipo == 'integer':
                self.tabla_simbolos[variable]['valor'] = int(entrada)
            elif tipo == 'real':
                self.tabla_simbolos[variable]['valor'] = float(entrada)
            else:
                self.tabla_simbolos[variable]['valor'] = entrada
        elif linea.startswith('escribir(') or linea.startswith('escribirln('):
            salto = linea.startswith('escribirln')
            contenido = re.search(r'\((.*)\);', linea).group(1)
            partes = [p.strip() for p in contenido.split(',')]
            salida = ""
            for parte in partes:
                if parte.startswith('"') and parte.endswith('"'):
                    salida += parte.strip('"')
                elif parte in self.tabla_simbolos:
                    val = self.tabla_simbolos[parte]['valor']
                    salida += str(val) if val is not None else 'nil'
            print(salida, end='\n' if salto else '')
        elif linea.startswith('para'):
            patron = r'para\s*\((\w+)\s*=\s*(\d+);\s*(\d+)\)\s*\{'
            coincidencia = re.match(patron, linea)
            variable, inicio, fin = coincidencia.groups()
            self.declarar_variable(variable, 'integer')
            cuerpo = []
            self.indice += 1
            while not self.lineas[self.indice].strip() == '}':
                cuerpo.append(self.lineas[self.indice].strip())
                self.indice += 1
            for i in range(int(inicio), int(fin)+1):
                self.tabla_simbolos[variable]['valor'] = i
                for l in cuerpo:
                    self.ejecutar_linea(l)
        elif '=' in linea:
            if not linea.endswith(';'):
                raise Exception(f"Falta ';' en la línea: {linea}")
            variable, expresion = linea.split('=', 1)
            variable = variable.strip()
            expresion = expresion.strip(';').strip()
            if variable not in self.tabla_simbolos:
                raise Exception(f"Variable '{variable}' no declarada.")
            resultado = self.evaluar_expresion(expresion)
            self.tabla_simbolos[variable]['valor'] = resultado
        elif linea == 'fin.':
            print("\n--- Fin del programa ---")
        else:
            raise Exception(f"Instrucción no reconocida: {linea}")

    def ejecutar(self, codigo):
        limpio = self.eliminar_comentarios(codigo)
        self.dividir_lineas(limpio)
        while self.indice < len(self.lineas):
            self.ejecutar_linea(self.lineas[self.indice])
            self.indice += 1

# Programa de prueba
if __name__ == "__main__":
    codigo = """
    (* Programa de prueba en español *)
    var x real;
    var y real;
    leer(x);
    leer(y);
    var resultado real;
    resultado = (x + y) / 2;
    escribirln("Promedio: ", resultado);
    fin.
    """

    interprete = InterpreteMiniPascal()
    interprete.ejecutar(codigo)