class Variable:
    nombre = ""
    tipo = ""
    valor = ""

    def __init__(self, n, t, v):
        self.nombre = n
        self.tipo = t
        self.valor = v


def esSimboloEsp(caracter):
    return caracter in "+-*;,.:!#=%&/(){}[]<><=>=="


def esSeparador(caracter):
    return caracter in " \n\t"


def esId(cad):
    return (cad[0] in "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


def esTipo(vad):
    tipos = ["integer", "real", "string"]
    return (cad in tipos)


def tokeniza(linea):
    tokens = []
    tokens2 = []
    dentro = False
    for l in linea:
        if esSimboloEsp(l) and not (dentro):
            tokens.append(l)
        if (esSimboloEsp(l) or esSeparador(l)) and dentro:
            tokens.append(cad)
            dentro = False
            if esSimboloEsp(l):
                tokens.append(l)
        if not (esSimboloEsp(l)) and not (esSeparador(l)) and not (dentro):
            dentro = True
            cad = ""
        if not (esSimboloEsp(l)) and not (esSeparador(l)) and dentro:
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


def obtenerPrioridadOperador(o):
    # Función que trabaja con convertirInfijaA**.
    return {'(': 1, ')': 2, '+': 3, '-': 3, '*': 4, '/': 4, '^': 5}.get(o)


def obtenerListaInfija(cadena_infija):
    if (type(cadena_infija) == list):
        return obtenerListaInfija("".join(cadena_infija))
    '''Devuelve una cadena en notación infija dividida por sus elementos.'''
    infija = []
    cad = ''
    for i in cadena_infija:
        if i in ['+', '-', '*', '/', '(', ')', '^', '=']:
            if cad != '':
                infija.append(cad)
                cad = ''
            infija.append(i)
        elif i == chr(32):  # Si es un espacio.
            cad = cad
        else:
            cad += i
    if cad != '':
        infija.append(cad)
    return infija


def infija2Posfija(expresion_infija):
    '''Convierte una expresión infija a una posfija, devolviendo una lista.'''
    infija = obtenerListaInfija(expresion_infija)
    pila = []
    salida = []
    for e in infija:
        if e == '(':
            pila.append(e)
        elif e == ')':
            while pila[len(pila) - 1] != '(':
                salida.append(pila.pop())
            pila.pop()
        elif e in ['+', '-', '*', '/', '^']:
            while (len(pila) != 0) and (obtenerPrioridadOperador(e)) <= obtenerPrioridadOperador(pila[len(pila) - 1]):
                salida.append(pila.pop())
            pila.append(e)
        else:
            salida.append(e)
    while len(pila) != 0:
        salida.append(pila.pop())
    return salida


def agregaVar(tablaVar, varNombre, tipoVar):
    if esTipo(tipoVar):
        # agregar lógica para variables redeclaradas
        tablaVar.append(Variable(varNombre, tipoVar, "0"))
    else:
        print("tipo de dato inexistente: ", tipoVar)

    return None


def setValor(varNombre, valor):
    print("asignar a la variable", varNombre, "El valor ", valor)
    for v in tablaVar:
        if (v.nombre == varNombre):
            tipo = getTipo(varNombre)
            if (tipo == "int"):
                v.valor = int(valor)
            elif (tipo == "char"):
                v.valor = valor
            elif (tipo == "float"):
                v.valor = float(valor)
    return None


def getValor(varNombre):
    for v in tablaVar:
        if (v.nombre == varNombre):
            return v.valor
        pass


def getTipo(varNombre):
    for v in tablaVar:
        if (v.nombre == varNombre):
            return v.tipo
        pass


def estaEnTabla(n):
    encontrado = False
    for reg in tablaVar:
        if reg.nombre == n:
            encontrado = True
    return (encontrado)


tablaVar = []
renglon = ""
while (renglon != "end;"):
    renglon = input("##")
    tokens = tokeniza(renglon)
    print(tokens)
    if (tokens[0] == "var"):  # Es una declaracion de variable
        agregaVar(tokens[2], tokens[1])
    elif (esId(tokens[0])):  # El primer token es un ID
        if (len(tokens) == 4):  # Es de la forma "ID = valor;"
            if (tokens[1] == "="):
                setValor(tokens[0], tokens[2])
        elif (tokens[0] == "print"):  # El renglon es un print
            if (tokens[3] == ")"):  # Hau un solo token dentro del print
                valor = getValor(tokens[2]);  # recuperamos el valor de la variable
                print(valor)
        elif (len(tokens) == 2):  # Es solo el identificador
            print(getValor(tokens[0]))
        else:  # no se reconoce la expresion
            print("no se reconoce la expresion")



