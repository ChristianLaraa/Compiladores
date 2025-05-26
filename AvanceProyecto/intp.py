import re
import math

tabla_vars = {}

def eliminar_comentarios(codigo):
    return re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)

def es_simbolo_esp(car):
    return car in "+-*/()=;,"

def es_separador(car):
    return car in " \t\n"

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

def evaluar_expresion(tokens):
    expr = ' '.join(tokens)
    for var in tabla_vars:
        expr = expr.replace(var, str(tabla_vars[var]["valor"]))
    try:
        return eval(expr, {"__builtins__": None}, {"sin": math.sin, "cos": math.cos, "tan": math.tan})
    except:
        print(f"Error al evaluar: {' '.join(tokens)}")
        return None

def interpretar_linea(tokens):
    if not tokens:
        return

    if tokens[0] == "var" and tokens[1] in ["int", "float", "string", "char"]:
        nombre = tokens[2]
        if nombre in tabla_vars:
            print(f"Error: variable '{nombre}' ya declarada")
            return
        tabla_vars[nombre] = {"tipo": tokens[1], "valor": 0 if tokens[1] in ["int", "float"] else ""}
        return

    if tokens[0] == "read" and tokens[1] == "(" and tokens[3] == ")" and tokens[4] == ";":
        nombre = tokens[2]
        if nombre not in tabla_vars:
            print(f"Error: variable '{nombre}' no declarada")
            return
        tipo = tabla_vars[nombre]["tipo"]
        entrada = input(f"{nombre}? ")
        if tipo == "int":
            tabla_vars[nombre]["valor"] = int(entrada)
        elif tipo == "float":
            tabla_vars[nombre]["valor"] = float(entrada)
        elif tipo == "string":
            tabla_vars[nombre]["valor"] = str(entrada)
        else:
            tabla_vars[nombre]["valor"] = entrada[0]
        return

    if tokens[0] in ["print", "println"] and tokens[1] == "(":
        contenido = []
        i = 2
        while tokens[i] != ")":
            if tokens[i] != ",":
                contenido.append(tokens[i])
            i += 1
        salida = ""
        for item in contenido:
            if item.startswith('"'):
                salida += item.strip('"')
            elif item in tabla_vars:
                salida += str(tabla_vars[item]["valor"])
            else:
                salida += item
        if tokens[0] == "println":
            print(salida)
        else:
            print(salida, end="")
        return

    if "=" in tokens:
        idx = tokens.index("=")
        nombre = tokens[idx - 1]
        if nombre not in tabla_vars:
            print(f"Error: variable '{nombre}' no declarada")
            return
        expresion = tokens[idx + 1:-1]  # sin el ;
        valor = evaluar_expresion(expresion)
        tabla_vars[nombre]["valor"] = valor
        return

def interpretar_bloque(cuerpo_lineas):
    for linea in cuerpo_lineas:
        tokens = separa_tokens(linea.strip())
        interpretar_linea(tokens)

def main():
    print("Intérprete Mini C - Ejecución directa")
    print("Ingresa tu código (termina con 'end.'):")

    codigo = ""
    while True:
        linea = input()
        if linea.strip() == "end.":
            break
        codigo += linea + "\n"

    codigo = eliminar_comentarios(codigo)
    lineas = codigo.split("\n")
    i = 0

    while i < len(lineas):
        linea = lineas[i].strip()
        if not linea:
            i += 1
            continue

        if not linea.endswith(";") and not linea.startswith("for"):
            print(f"Error: falta ';' en línea {i+1}")
            return

        tokens = separa_tokens(linea)

        if tokens and tokens[0] == "for":
            if len(tokens) >= 8 and tokens[1] == '(' and tokens[3] == '=' and tokens[5] == ';' and tokens[7] == ')':
                var_name = tokens[2]
                if var_name not in tabla_vars:
                    print(f"Error: variable '{var_name}' no declarada")
                    return
                inicio = int(tokens[4])
                fin = int(tokens[6])
                cuerpo = []
                j = i + 1
                while j < len(lineas):
                    l2 = lineas[j].strip()
                    if l2 == "}":
                        break
                    cuerpo.append(l2)
                    j += 1
                else:
                    print("Error: falta '}' que cierre el bloque del for")
                    return
                for val in range(inicio, fin + 1):
                    tabla_vars[var_name]["valor"] = val
                    interpretar_bloque(cuerpo)
                i = j
                i += 1
                continue
            else:
                print("Error: sintaxis inválida del for")
                return

        interpretar_linea(tokens)
        i += 1

if __name__ == "__main__":
    main()