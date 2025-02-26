#Christian Gael Lara Martinez Tarea1, 260225
def es_ID(token):
    minusculas = 'abcdefghijklmnopqrstuvwxyz'
    mayusculas = minusculas.upper()
    if token and (token[0] in minusculas or token[0] in mayusculas):
        return True
    return False

def es_palabra_reservada(token):
    reservadas = ['main', 'void', 'int', 'float', 'char', 'for', 'if']
    return token in reservadas

def es_tipo(token):
    tipos = ['int', 'float', 'char']
    return token in tipos

def es_operador(token):
    operadores = ['+', '-', '*', '/', '=', '==', '!=', '<=', '>=']
    return token in operadores

def es_simbolo_especial(token):
    simbolos = '!"#$%&/()=?¡¿*+{}][-_:;,. '
    return token in simbolos

def get_etiqueta(token):
    if es_ID(token):
        if es_palabra_reservada(token):
            if es_tipo(token):
                return 'tipo'
            return 'palres'
        return 'ID'
    elif es_simbolo_especial(token):
        if es_operador(token):
            return 'op'
        return 'simb_esp'
    elif token.isdigit():
        return 'entero'
    return 'desconocido'

arch = open('prueba.c', 'r')
texto = arch.read()
arch.close()

texto2 = ''
estado = 'Z'
for c in texto:
    if estado == 'Z':
        if c == '/':
            estado = 'A'
        else:
            texto2 += c
    elif estado == 'A':
        if c == '*':
            estado = 'B'
        else:
            estado = 'Z'
            texto2 += '/' + c
    elif estado == 'B':
        if c == '*':
            estado = 'C'
    elif estado == 'C':
        if c == '/':
            estado = 'Z'
        elif c != '*':
            estado = 'B'



tokens = []
token = ''
estado = 'fuera'

for c in texto2:
    if estado == 'fuera':
        if c in '+-*/=!<>[]{};,:.':
            tokens.append(c)
        elif not(c in [' ', '\n', '\t']):
            estado = 'dentro'
            token = c
    else:
        if c in [' ', '\n', '\t']:
            tokens.append(token)
            token = ''
            estado = 'fuera'
        elif c in '+-*/=!<>[]{};,:.':
            tokens.append(token)
            tokens.append(c)
            token = ''
            estado = 'fuera'
        else:
            token += c

if token:
    tokens.append(token)

for t in tokens:
    etiqueta = get_etiqueta(t)
    print(f'{t} es {etiqueta}')
