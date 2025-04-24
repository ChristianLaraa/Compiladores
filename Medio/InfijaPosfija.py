def infija_a_posfija(expresion):
    # Definir la precedencia de los operadores
    precedencia = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
    # Pila para almacenar operadores
    pila = []
    # Lista para la salida en notación posfija
    salida = []

    # Función para verificar si un carácter es un operador
    def es_operador(c):
        return c in precedencia

    # Recorrer cada carácter en la expresión
    for c in expresion:
        if c.isalnum():  # Si el carácter es un operando (número o letra)
            salida.append(c)
        elif c == '(':  # Si el carácter es un paréntesis izquierdo
            pila.append(c)
        elif c == ')':  # Si el carácter es un paréntesis derecho
            while pila and pila[-1] != '(':
                salida.append(pila.pop())
            pila.pop()  # Eliminar el paréntesis izquierdo de la pila
        else:  # Si el carácter es un operador
            while pila and pila[-1] != '(' and precedencia[c] <= precedencia[pila[-1]]:
                salida.append(pila.pop())
            pila.append(c)

    # Vaciar la pila y agregar cualquier operador restante a la salida
    while pila:
        salida.append(pila.pop())

    return salida

# Ejemplo de uso
expresion_infija = ['(', 'a', '+', '(', 'b', '*', 'c', ')', '/', 'd', ')', '/', 'e']
expresion_posfija = infija_a_posfija(expresion_infija)
print("Expresión infija:", expresion_infija)
print("Expresión posfija:", expresion_posfija)