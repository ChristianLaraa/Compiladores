import re
class Variable:
    contador_int = 0
    contador_float = 0
    contador_temp_int = 0
    contador_temp_float = 0

    def __init__(self, nombre, tipo, es_temporal=False):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = None
        self.es_temporal = es_temporal
        # Asignación de registros
        if tipo == "int":
            if es_temporal:
                self.registro = f"t{Variable.contador_temp_int}"
                Variable.contador_temp_int += 1
            else:
                self.registro = f"t{Variable.contador_int}"
                Variable.contador_int += 1
        elif tipo == "float":
            if es_temporal:
                self.registro = f"ft{Variable.contador_temp_float}"
                Variable.contador_temp_float += 1
            else:
                self.registro = f"ft{Variable.contador_float}"
                Variable.contador_float += 1
        else:
            # Para string y char se asigna memoria (simplificado)
            self.registro = "mem"


tabla_var = []


def existe_var(nombre):
    return any(v.nombre == nombre for v in tabla_var)


def agrega_var(nombre, tipo, es_temporal=False):
    if existe_var(nombre) and not es_temporal:
        print(f"Error: Variable '{nombre}' ya declarada")
        return False
    tabla_var.append(Variable(nombre, tipo, es_temporal))
    return True


def get_var(nombre):
    for v in tabla_var:
        if v.nombre == nombre:
            return v
    return None


def set_var_valor(nombre, valor):
    v = get_var(nombre)
    if not v:
        print(f"Error: Variable '{nombre}' no declarada")
        return
    try:
        if v.tipo == "int":
            v.valor = int(valor)
        elif v.tipo == "float":
            v.valor = float(valor)
        elif v.tipo == "string":
            v.valor = str(valor)
        else:
            v.valor = valor
    except:
        print(f"Error: Tipo incorrecto para asignar a '{nombre}'")


def imprime_tabla_vars():
    print("\nTabla de variables:")
    print(f"{'Nombre':10} {'Tipo':8} {'Valor':10} {'Registro'}")
    for v in tabla_var:
        print(f"{v.nombre:10} {v.tipo:8} {str(v.valor):10} {v.registro}")


def eliminar_comentarios(codigo):
    return re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)


def es_simbolo_esp(car):
    return car in "+-*;/,()=<>"


def es_separador(car):
    return car in " \n\t"


def separa_tokens(linea):
    tokens = []
    token = ""
    i = 0
    dentro_cadena = False
    while i < len(linea):
        c = linea[i]
        if dentro_cadena:
            token += c
            if c == '"':
                tokens.append(token)
                token = ""
                dentro_cadena = False
        else:
            if c == '"':
                if token:
                    tokens.append(token)
                    token = ""
                token = c
                dentro_cadena = True
            elif es_simbolo_esp(c):
                if token:
                    tokens.append(token)
                    token = ""
                if c == '=' and i + 1 < len(linea) and linea[i + 1] == '=':
                    tokens.append("==")
                    i += 1
                else:
                    tokens.append(c)
            elif es_separador(c):
                if token:
                    tokens.append(token)
                    token = ""
            else:
                token += c
        i += 1
    if token:
        tokens.append(token)
    return tokens


palabras_reservadas = ['var', 'int', 'float', 'string', 'char', 'print', 'println', 'read', 'for', 'sin', 'cos', 'tan',
                       'end']

tipos_validos = ['int', 'float', 'string', 'char']