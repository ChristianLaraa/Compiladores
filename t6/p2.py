# Clase Variable para manejar las variables
class Variable:
    nombre = ""
    tipo = ""
    valor = ""

    def __init__(self, n, t, v):
        self.nombre = n
        self.tipo = t
        self.valor = v


# Lista para guardar todas las variables
tablaVar = []


# Funciones auxiliares
def esSimboloEsp(caracter):
    return caracter in "+-*;,.:!=%&/()[]<><=>=="


def esSeparador(caracter):
    return caracter in " \n\t"


def esEntero(cad):
    try:
        int(cad)
        return True
    except:
        return False


def esId(cad):
    return cad[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"


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
    if tokens:
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


# Funciones para manejar la tabla de variables
def agregaVar(varNombre, tipoVar):
    tablaVar.append(Variable(varNombre, tipoVar, 0))
    return None


def setValor(varNombre, valor):
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


def getTipo(varNombre):
    for v in tablaVar:
        if (v.nombre == varNombre):
            return v.tipo


def estaEnTabla(n):
    for reg in tablaVar:
        if reg.nombre == n:
            return True
    return False


# Intérprete principal
renglon = ""
while (renglon != "end;"):
    renglon = input("## ")
    tokens = tokeniza(renglon)
    if not tokens:
        continue  # Si no hay tokens, seguimos al siguiente ciclo

    if (tokens[0] == "var"):  # Declaración de variable
        if len(tokens) >= 3:
            if not estaEnTabla(tokens[2]):
                agregaVar(tokens[2], tokens[1])
                print(f"Variable '{tokens[2]}' de tipo '{tokens[1]}' creada.")
            else:
                print(f"La variable '{tokens[2]}' ya existe.")
        else:
            print("Error en la declaración de variable.")
    elif (tokens[0] == "print"):  # Print
        if len(tokens) >= 4 and tokens[1] == "(" and tokens[3] == ")":
            valor = getValor(tokens[2])
            if valor is not None:
                print(valor)
            else:
                print(f"Variable '{tokens[2]}' no encontrada.")
        else:
            print("Error en la sintaxis del print.")
    elif (esId(tokens[0])):  # Es un identificador
        if len(tokens) == 4 and tokens[1] == "=":  # Asignación
            if estaEnTabla(tokens[0]):
                setValor(tokens[0], tokens[2])
                print(f"Variable '{tokens[0]}' actualizada a {tokens[2]}.")
            else:
                print(f"Variable '{tokens[0]}' no declarada.")
        elif len(tokens) == 2 and tokens[1] == ";":  # Mostrar valor
            if estaEnTabla(tokens[0]):
                print(getValor(tokens[0]))
            else:
                print(f"Variable '{tokens[0]}' no declarada.")
        else:
            print("No se reconoce la expresión.")
    elif (tokens[0] == "end" and tokens[1] == ";"):
        print("Finalizando intérprete.")
        break
    else:
        print("No se reconoce la expresión.")
