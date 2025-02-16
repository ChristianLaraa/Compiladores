arch = open('prog1.c', 'r')
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
print(texto)
print('--------------------------------')
print(texto2)

tokens = []
token = ''
estado = 'fuera'

for c in texto2:
    if estado == 'fuera':
        if c in '+*!"#$%&/()=?¡¿¨´+*[]{};,:.-_':
            tokens.append(c)
        elif not(c in [' ','\n', '\t']):
            estado = 'dentro'
            token = c
        else: #estado = dentro
            if c in [' ','\n', '\t']:
                tokens.append(token)
                token = ''
                estado = 'fuera'
            elif c in '+*!"#$%&/()=?¡¿¨´+*[]{};,:.-_':
                tokens.append(token)
                tokens.append(c)
                token = ''
                estado = 'fuera'
            else:
                token += c
print(tokens)

