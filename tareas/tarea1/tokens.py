# Christian Gael Lara Martinez Tarea1, 260225
def get_etiqueta(t):
    operadores = '+-*/='
    minusculas = 'abcdefghijklmnopqrstuvwxyz_'
    mayusculas = minusculas.upper()
    if t in especiales:
        if t in operadores:
            return 'operador'
        else:
            return 'simb esp'
    else:
        if t[0] in minusculas or t[0] in mayusculas:
            return 'ID'
        elif t[0] in '0123456789':
            return 'entero'
    return None


arch1 = open('prueba.c', 'r')
texto = arch1.read()
arch1.close()
print(texto)

estado = 'Z'
texto2 = ''
for letra in texto:    
    if estado == 'Z':
        if letra == '/':
            estado = 'A'            
        else:
            texto2 += letra
    elif estado == 'A':
        if letra == '*':
            estado = 'B'            
        else:
            estado = 'Z'
            texto2 += '/'
    elif estado == 'B':
        if letra == '*':
            estado = 'C'            
    elif estado == 'C':
        if letra == '/':
            estado = 'Z'            
        elif letra != '*':
            estado = 'B'            
print ('terminado')

print(texto)
print('_______________________________')
print(texto2)

#    aqui empieza lo de los tokens
separadores = [' ','\t', '\n']
especiales = '{},;!":#$%&/()=?¡¨*[]-`^'
tokens = []
dentro = False
token = ''
for letra in texto2:
    if not(dentro):
        if letra in especiales:
            tokens.append(letra)
        elif not(letra in separadores):
            dentro = True
            token += letra
    else:
        if letra in separadores:            
            tokens.append(token)
            token = ''
            dentro = False
        elif letra in especiales:           
            tokens.append(token)
            tokens.append(letra)
            token = ''
            dentro = False
        else:
            token += letra

for t in tokens:
    print(t)


# etiqueta los tokens

for t in tokens:
    etiqueta = get_etiqueta(t)
    print(t, 'es',etiqueta)
            
    
