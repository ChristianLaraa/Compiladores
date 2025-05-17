import re
class Variable:
    contador_int = 0
    contador_float = 0
    contador_temp_int = 0
    contador_temp_float = 0

    def __init__(self, nombre, tipo, es_temporal=False):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = None
        self.es_temporal = es_temporal
        # Asignación de registros
        if tipo == "int":
            if es_temporal:
                self.registro = f"t{Variable.contador_temp_int}"
                Variable.contador_temp_int += 1
            else:
                self.registro = f"t{Variable.contador_int}"
                Variable.contador_int += 1
        elif tipo == "float":
            if es_temporal:
                self.registro = f"ft{Variable.contador_temp_float}"
                Variable.contador_temp_float += 1
            else:
                self.registro = f"ft{Variable.contador_float}"
                Variable.contador_float += 1
        else:
            # Para string y char se asigna memoria (simplificado)
            self.registro = "mem"


tabla_var = []


def existe_var(nombre):
    return any(v.nombre == nombre for v in tabla_var)


def agrega_var(nombre, tipo, es_temporal=False):
    if existe_var(nombre) and not es_temporal:
        print(f"Error: Variable '{nombre}' ya declarada")
        return False
    tabla_var.append(Variable(nombre, tipo, es_temporal))
    return True


def get_var(nombre):
    for v in tabla_var:
        if v.nombre == nombre:
            return v
    return None


def set_var_valor(nombre, valor):
    v = get_var(nombre)
    if not v:
        print(f"Error: Variable '{nombre}' no declarada")
        return
    try:
        if v.tipo == "int":
            v.valor = int(valor)
        elif v.tipo == "float":
            v.valor = float(valor)
        elif v.tipo == "string":
            v.valor = str(valor)
        else:
            v.valor = valor
    except:
        print(f"Error: Tipo incorrecto para asignar a '{nombre}'")


def imprime_tabla_vars():
    print("\nTabla de variables:")
    print(f"{'Nombre':10} {'Tipo':8} {'Valor':10} {'Registro'}")
    for v in tabla_var:
        print(f"{v.nombre:10} {v.tipo:8} {str(v.valor):10} {v.registro}")


# ------------------- Utilidades Léxico -------------------

def eliminar_comentarios(codigo):
    return re.sub(r'/\*.*?\*/', '', codigo, flags=re.DOTALL)


def es_simbolo_esp(car):
    return car in "+-*;/,()=<>"


def es_separador(car):
    return car in " \n\t"


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


palabras_reservadas = ['var', 'int', 'float', 'string', 'char', 'print', 'println', 'read', 'for', 'sin', 'cos', 'tan',
                       'end']

tipos_validos = ['int', 'float', 'string', 'char']

# ------------------- Expresiones -------------------

prioridad_op = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}


def convertir_infija_a_postfija(exp):
    pila = []
    salida = []
    for e in exp:
        if e == '(':
            pila.append(e)
        elif e == ')':
            while pila and pila[-1] != '(':
                salida.append(pila.pop())
            pila.pop()  # sacar '('
        elif e in prioridad_op:
            while pila and pila[-1] != '(' and prioridad_op.get(pila[-1], 0) >= prioridad_op.get(e, 0):
                salida.append(pila.pop())
            pila.append(e)
        else:
            salida.append(e)
    while pila:
        salida.append(pila.pop())
    return salida


def es_numero(cad):
    try:
        float(cad)
        return True
    except:
        return False


# Genera código intermedio en forma de lista de instrucciones tipo: (temp, op, op1, op2)
def generar_codigo_intermedio(postfija):
    pila = []
    instrucciones = []
    contador_temp = 1

    for token in postfija:
        if token not in prioridad_op:
            pila.append(token)
        else:
            op2 = pila.pop()
            op1 = pila.pop()
            temp = f"T{contador_temp}"
            contador_temp += 1
            instrucciones.append((temp, token, op1, op2))
            pila.append(temp)
    return instrucciones


# ------------------- Generación de Ensamblador RISC-V -------------------

def generar_ensamblador_asignacion(var_dest, valor):
    # var_dest: objeto Variable
    # valor: puede ser literal o variable/temporal
    lines = []
    if es_numero(valor):
        # cargar literal a registro
        if var_dest.tipo == 'int':
            lines.append(f"li {var_dest.registro}, {int(float(valor))}  # carga literal int")
        elif var_dest.tipo == 'float':
            lines.append(f"li t0, {valor}    # carga literal float en int temporal (simulación)")
            lines.append(f"fmv.s {var_dest.registro}, t0  # mueve literal float")
        else:
            lines.append(f"# No soportado literal para tipo {var_dest.tipo}")
    else:
        # asignación entre registros
        var_or_temp = get_var(valor)
        if var_or_temp:
            if var_dest.tipo == 'int':
                lines.append(f"mv {var_dest.registro}, {var_or_temp.registro}  # asigna int {valor}")
            elif var_dest.tipo == 'float':
                lines.append(f"fmv.s {var_dest.registro}, {var_or_temp.registro}  # asigna float {valor}")
            else:
                lines.append(f"# Asignación no soportada para tipo {var_dest.tipo}")
        else:
            lines.append(f"# Variable o temporal '{valor}' no encontrada")
    return lines


def generar_ensamblador_codigo_intermedio(instrucciones):
    lines = []
    for temp, op, op1, op2 in instrucciones:
        vtemp = get_var(temp)
        if not vtemp:
            agrega_var(temp, 'float' if (op in ['/', '*', '+', '-']) else 'int', es_temporal=True)
            vtemp = get_var(temp)
        vop1 = get_var(op1)
        vop2 = get_var(op2)

        # Asumimos operaciones de float si alguna es float
        tipo = 'int'
        if (vop1 and vop1.tipo == 'float') or (vop2 and vop2.tipo == 'float'):
            tipo = 'float'
            vtemp.tipo = 'float'

        if tipo == 'int':
            if op == '+':
                lines.append(f"add {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} + {op2}")
            elif op == '-':
                lines.append(f"sub {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} - {op2}")
            elif op == '*':
                lines.append(f"mul {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} * {op2}")
            elif op == '/':
                lines.append(f"div {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} / {op2}")
        else:
            if op == '+':
                lines.append(f"fadd.s {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} + {op2}")
            elif op == '-':
                lines.append(f"fsub.s {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} - {op2}")
            elif op == '*':
                lines.append(f"fmul.s {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} * {op2}")
            elif op == '/':
                lines.append(f"fdiv.s {vtemp.registro}, {vop1.registro}, {vop2.registro}  # {temp} = {op1} / {op2}")

    return lines


def generar_ensamblador_print(var):
    lines = []
    if var.tipo == 'int':
        lines.append(f"mv a0, {var.registro}")
        lines.append("li a7, 1")
        lines.append("ecall")
    elif var.tipo == 'float':
        lines.append(f"fmv.s fa0, {var.registro}")
        lines.append("li a7, 2")
        lines.append("ecall")
    elif var.tipo == 'string':
        # Aquí simplificado asumiendo cadena en .data y registro apunta a la dirección
        lines.append(f"mv a0, {var.registro}")
        lines.append("li a7, 4")
        lines.append("ecall")
    else:
        lines.append("# print para tipo no soportado")
    return lines


def generar_ensamblador_read(var):
    lines = []
    if var.tipo == 'int':
        lines.append("li a7, 5")
        lines.append("ecall")
        lines.append(f"mv {var.registro}, a0")
    elif var.tipo == 'float':
        lines.append("li a7, 6")
        lines.append("ecall")
        lines.append(f"fmv.s {var.registro}, fa0")
    elif var.tipo == 'char':
        lines.append("li a7, 12")
        lines.append("ecall")
        lines.append(f"mv {var.registro}, a0")
    else:
        lines.append("# read para tipo no soportado")
    return lines


def generar_ensamblador_end():
    return ["li a7, 10", "ecall  # Terminar programa"]


# ------------------- Soporte para funciones trigonométricas -------------------

def generar_ensamblador_funcion(func, arg_var, ret_var):
    lines = []
    # Pasar argumento
    if arg_var.tipo == 'float':
        lines.append(f"fmv.s fa0, {arg_var.registro}")
        # Simulamos llamada a función de librería
        lines.append(f"call {func}")
        lines.append(f"fmv.s {ret_var.registro}, fa0")
    else:
        lines.append(f"# Función {func} solo soporta float")
    return lines


# ------------------- Soporte para ciclos for -------------------

def generar_ensamblador_for(var_c, inicio, fin, cuerpo_asm):
    # var_c: objeto Variable para contador
    # inicio, fin: enteros
    # cuerpo_asm: lista de instrucciones (strings)
    etiquetas = {
        'inicio': 'for_start',
        'fin': 'for_end'
    }
    lines = []
    lines.append(f"li {var_c.registro}, {inicio}    # Inicio for")
    lines.append(f"{etiquetas['inicio']}:")
    lines.append(f"bgt {var_c.registro}, {fin}, {etiquetas['fin']}  # Condición fin for")
    lines.extend(cuerpo_asm)
    lines.append(f"addi {var_c.registro}, {var_c.registro}, 1  # Incremento contador")
    lines.append(f"j {etiquetas['inicio']}")
    lines.append(f"{etiquetas['fin']}:")
    return lines


# ------------------- PROGRAMA PRINCIPAL -------------------

def main():
    print("Compilador Mini-C simplificado (generador de ensamblador RISC-V)")
    codigo_completo = ""
    print("Introduce el código (termina con 'end.'):")
    while True:
        linea = input()
        if linea.strip() == "end.":
            break
        codigo_completo += linea + "\n"

    codigo_completo = eliminar_comentarios(codigo_completo)

    lineas = codigo_completo.split('\n')
    ensamblador = []
    i = 0

    while i < len(lineas):
        linea = lineas[i].strip()
        if not linea:
            i += 1
            continue
        if linea[-1] != ';' and not linea.startswith('for') and linea != 'end.':
            print(f"Error: Falta ';' en línea {i + 1}")
            return
        tokens = separa_tokens(linea)
        if not tokens:
            i += 1
            continue

        # Declaracion de variable: var tipo nombre;
        if len(tokens) == 4 and tokens[0] == 'var' and tokens[1] in tipos_validos and tokens[3] == ';':
            agrega_var(tokens[2], tokens[1])
            i += 1
            continue

        # read(variable);
        if tokens[0] == 'read' and tokens[1] == '(' and len(tokens) >= 4 and tokens[-2] == ')' and tokens[-1] == ';':
            varname = tokens[2]
            var = get_var(varname)
            if not var:
                print(f"Error: variable {varname} no declarada")
                return
            ensamblador.extend(generar_ensamblador_read(var))
            i += 1
            continue

        # print(variable); o println(variable);
        if tokens[0] in ['print', 'println'] and tokens[1] == '(' and tokens[-2] == ')' and tokens[-1] == ';':
            varname = tokens[2]
            var = get_var(varname)
            if not var:
                print(f"Error: variable {varname} no declarada")
                return
            ensamblador.extend(generar_ensamblador_print(var))
            if tokens[0] == 'println':
                ensamblador.append("li a0, 10  # newline")
                ensamblador.append("li a7, 11")
                ensamblador.append("ecall")
            i += 1
            continue

        # Asignacion simple y expresiones:
        # Ejemplo: m = (y2 - y1) / (x2 - x1);
        if '=' in tokens:
            try:
                pos_igual = tokens.index('=')
                varname = tokens[pos_igual - 1]
                var = get_var(varname)
                if not var:
                    print(f"Error: variable {varname} no declarada")
                    return
                # Expresión a la derecha
                expresion = tokens[pos_igual + 1:-1]  # Excluyendo ; al final

                # Si es solo un literal o variable
                if len(expresion) == 1:
                    ensamblador.extend(generar_ensamblador_asignacion(var, expresion[0]))
                    i += 1
                    continue

                # Si es expresión compleja
                postfija = convertir_infija_a_postfija(expresion)
                codigo_intermedio = generar_codigo_intermedio(postfija)
                # Agregar temporales a tabla (ya en generar_ensamblador lo hace)
                asm_expr = generar_ensamblador_codigo_intermedio(codigo_intermedio)
                ensamblador.extend(asm_expr)
                # Finalmente asignar último temporal a variable destino
                ultimo_temp = codigo_intermedio[-1][0]
                ensamblador.extend(generar_ensamblador_asignacion(var, ultimo_temp))
                i += 1
                continue
            except Exception as e:
                print("Error en procesamiento de asignación:", e)
                return

        # Ciclo for (ejemplo: for (c = 1; 5) { ... })
        if tokens[0] == 'for':
            # Formato esperado: for ( c = inicio ; fin ) { (instrucciones) }
            # Aquí haremos una implementación simple:
            if len(tokens) >= 11 and tokens[1] == '(' and tokens[3] == '=' and tokens[5] == ';' and tokens[7] == ')' and \
                    tokens[8] == '{' and tokens[-1] == '}':
                varname = tokens[2]
                inicio = int(tokens[4])
                fin = int(tokens[6])
                cuerpo_tokens = tokens[9:-1]  # instrucciones dentro del for (asumimos solo una asignacion simple)
                var_c = get_var(varname)
                if not var_c:
                    print(f"Error: variable contador {varname} no declarada")
                    return
                # Procesar cuerpo del for: solo asignacion simple del estilo a = a * 2;
                cuerpo_asm = []
                # convertir cuerpo_tokens en línea
                linea_cuerpo = " ".join(cuerpo_tokens)
                # ejemplo: a = a * 2 ;
                tokens_cuerpo = separa_tokens(linea_cuerpo)
                if '=' in tokens_cuerpo:
                    pos_eq = tokens_cuerpo.index('=')
                    var_dest_cuerpo = get_var(tokens_cuerpo[pos_eq - 1])
                    if not var_dest_cuerpo:
                        print(f"Error: variable {tokens_cuerpo[pos_eq - 1]} no declarada en for")
                        return
                    expr_cuerpo = tokens_cuerpo[pos_eq + 1:-1]
                    post_cuerpo = convertir_infija_a_postfija(expr_cuerpo)
                    ci_cuerpo = generar_codigo_intermedio(post_cuerpo)
                    asm_cuerpo = generar_ensamblador_codigo_intermedio(ci_cuerpo)
                    ultimo_temp_cuerpo = ci_cuerpo[-1][0]
                    asm_cuerpo.extend(generar_ensamblador_asignacion(var_dest_cuerpo, ultimo_temp_cuerpo))
                else:
                    print("Error: cuerpo del for inválido")
                    return

                # Generar código for completo
                ensamblador.extend(generar_ensamblador_for(var_c, inicio, fin, asm_cuerpo))
                i += 1
                continue
            else:
                print("Error: Sintaxis for inválida")
                return

        # Funciones trigonométricas sin, cos, tan (ejemplo: m = sin(x1);)
        if len(tokens) >= 6 and tokens[2] == '=' and tokens[3] in ['sin', 'cos', 'tan'] and tokens[4] == '(' and tokens[
            6] == ')' and tokens[7] == ';':
            var_dest = get_var(tokens[0])
            func = tokens[3]
            var_arg = get_var(tokens[5])
            if not var_dest or not var_arg:
                print("Error: variable destino o argumento no declarada")
                return
            # Crear temporal para resultado
            temp_res = f"T_func_{func}"
            agrega_var(temp_res, 'float', es_temporal=True)
            ret_var = get_var(temp_res)
            asm_func = generar_ensamblador_funcion(func, var_arg, ret_var)
            ensamblador.extend(asm_func)
            ensamblador.extend(generar_ensamblador_asignacion(var_dest, temp_res))
            i += 1
            continue

        print(f"Error: No se reconoce la instrucción en línea {i + 1}: {linea}")
        return

    ensamblador.extend(generar_ensamblador_end())

    print("\n--- Código Ensamblador generado ---\n")
    for l in ensamblador:
        print(l)


if __name__ == "__main__":
    main()
