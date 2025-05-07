# interprete Christian Lara

class Variable:
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = None


def agrega_var(tabla_var, nombre, tipo):
    tabla_var.append(Variable(nombre, tipo))
    pass


def existe_var(tabla_var, nombre):
    encontrado = False
    for v in tabla_var:
        if v.nombre == nombre:
            encontrado = True
    return encontrado


def set_var(tabla_var, nombre, valor):
    if existe_var(tabla_var, nombre):
        for v in tabla_var:
            if v.nombre == nombre:
                v.valor = valor
    else:
        print('variable ', nombre, 'no encontrada')
        return None


def imprime_tabla_var(tabla_var):
    print()
    print('   Tabla de variables')
    print('nombre\t\ttipo\t\tvalor')
    for v in tabla_var:
        print(v.nombre, '\t\t', v.tipo, '\t\t', v.valor)
    return None


def es_simbolo_esp(caracter):
    return caracter in "+-*;,.:!#=%&/(){}[]<><=>=="


def es_separador(caracter):
    return caracter in " \n\t"


def es_id(cad):
    return (cad[0] in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


def es_pal_res(cad):
    palres = ["int", "real", "string", 'print', 'read', 'tabla']
    return (cad in palres)


def es_tipo(cad):
    tipos = ["int", "real", "string"]
    return (cad in tipos)


def separa_tokens(linea):
    if len(linea) < 3:
        return []
    else:
        tokens = []
        tokens2 = []
        dentro = False
        for l in linea:
            if es_simbolo_esp(l) and not (dentro):
                tokens.append(l)
            if (es_simbolo_esp(l) or es_separador(l)) and dentro:
                tokens.append(cad)
                dentro = False
                if es_simbolo_esp(l):
                    tokens.append(l)
            if not (es_simbolo_esp(l)) and not (es_separador(l)) and not (dentro):
                dentro = True
                cad = ""
            if not (es_simbolo_esp(l)) and not (es_separador(l)) and dentro:
                cad = cad + l
        compuesto = False
        for c in range(len(tokens) - 1):
            if compuesto:
                compuesto = False
                continue
            if tokens[c] in "=<>!" and tokens[c + 1] == "=":
                tokens2.append(tokens[c] + "=")
                compuesto = True
            else:
                tokens2.append(tokens[c])
        tokens2.append(tokens[-1])
        for c in range(1, len(tokens2) - 1):
            if tokens2[c] == "." and esEntero(tokens2[c - 1]) and esEntero(tokens2[c + 1]):
                tokens2[c] = tokens2[c - 1] + tokens2[c] + tokens2[c + 1]
                tokens2[c - 1] = "borrar"
                tokens2[c + 1] = "borrar"
        porBorrar = tokens2.count("borrar")
        for c in range(porBorrar):
            tokens2.remove("borrar")
        tokens = []
        dentroCad = False
        cadena = ""
        for t in tokens2:
            if dentroCad:
                if t[-1] == '"':
                    cadena = cadena + " " + t
                    tokens.append(cadena[1:-1])
                    dentroCad = False
                else:
                    cadena = cadena + " " + t
            elif ((t[0] == '"')):
                cadena = t;
                dentroCad = True
            else:
                tokens.append(t)
    return tokens


tabla_var = []
ren = ""
while (ren != 'end;'):
    ren = input('$:')
    tokens = separa_tokens(ren)
    if es_id(tokens[0]):
        if es_pal_res(tokens[0]):
            if es_tipo(tokens[0]):
                if es_id(tokens[1]):
                    agrega_var(tabla_var, tokens[1], tokens[0])
            elif tokens[0] == 'read':
                if tokens[1] == '(' and es_id(tokens[2]) and tokens[3] == ')':
                    leido = input()
                    set_valor(tabla_var, tokens[2], leido)
            elif tokens[0] == 'tabla':
                imprime_tabla_var(tabla_var)

           ##Pt3 Lineas de codigos para poder leer variables tipo a= 10;  e imprimir
            elif tokens[0] == 'print':
                if tokens[1] == '(' and es_id(tokens[2]) and tokens[3] == ')':
                    encontrado = False
                    for v in tabla_var:
                        if v.nombre == tokens[2]:
                            print(v.valor)
                            encontrado = True
                    if not encontrado:
                        print('variable', tokens[2], 'no encontrada')
        else:
            if len(tokens) >= 3 and tokens[1] == '=':
                set_var(tabla_var, tokens[0], tokens[2])