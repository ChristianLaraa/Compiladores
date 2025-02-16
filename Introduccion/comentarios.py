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
