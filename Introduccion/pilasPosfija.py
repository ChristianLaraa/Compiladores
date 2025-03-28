def evalua(posfija):
    pila = []
    for e in posfija:
        if e in '*+-/':
            op2 = pila.pop()
            op1 = pila.pop()
            if e == '*':
                pila.append(int(op1) * int(op2))
            elif e == '/':
                pila.append(int(op1) / int(op2))
            elif e == '+':
                pila.append(int(op1) + int(op2))
            elif e == '-':
                pila.append(int(op1) - int(op2))
        else:
            pila.append(int(e))  

    return pila[-1]



expresion = ["3", "4", "+", "2", "*", "7", "/"]
print(evalua(expresion))
