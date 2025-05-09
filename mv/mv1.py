#Christian Lara
class RiscVSimulator:
    """Simulador simplificado de RISC-V que soporta un subconjunto básico de instrucciones."""

    def __init__(self):
        # Registros: x0-x31 (x0 siempre es 0)
        self.registers = [0] * 32
        # Memoria (simulada como un diccionario para acceso eficiente)
        self.memory = {}
        # Contador de programa
        self.pc = 0
        # Diccionario de instrucciones
        self.instructions = {}
        # Flag para controlar ejecución
        self.running = False

    def load_program(self, program):
        """Carga un programa en la memoria del simulador."""
        # Limpiamos el estado previo
        self.registers = [0] * 32
        self.memory = {}
        self.pc = 0
        self.instructions = {}

        # Procesamos el programa línea por línea
        address = 0
        for line in program.strip().split('\n'):
            # Ignoramos líneas vacías y comentarios
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Procesamos etiquetas
            if ':' in line:
                label, instruction = line.split(':', 1)
                label = label.strip()
                self.memory[label] = address
                line = instruction.strip()
                if not line:  # Si solo era una etiqueta, continuamos
                    continue

            # Guardamos la instrucción
            self.instructions[address] = line
            address += 4  # Cada instrucción ocupa 4 bytes en RISC-V

    def run(self):
        """Ejecuta el programa cargado."""
        self.running = True
        self.pc = 0

        while self.running and self.pc in self.instructions:
            instruction = self.instructions[self.pc]
            self.execute_instruction(instruction)

        return self.registers[10]  # Devuelve el valor en x10 (a0) como resultado

    def execute_instruction(self, instruction):
        """Ejecuta una instrucción individual."""
        parts = instruction.split()
        opcode = parts[0].lower()

        # Incrementamos el PC por defecto (algunas instrucciones lo modificarán)
        next_pc = self.pc + 4

        # Instrucciones aritméticas
        if opcode == 'add':
            rd, rs1, rs2 = self._parse_r_type(parts[1:])
            self.registers[rd] = self.registers[rs1] + self.registers[rs2]

        elif opcode == 'sub':
            rd, rs1, rs2 = self._parse_r_type(parts[1:])
            self.registers[rd] = self.registers[rs1] - self.registers[rs2]

        elif opcode == 'addi':
            rd, rs1, imm = self._parse_i_type(parts[1:])
            self.registers[rd] = self.registers[rs1] + imm

        # Operaciones lógicas
        elif opcode == 'and':
            rd, rs1, rs2 = self._parse_r_type(parts[1:])
            self.registers[rd] = self.registers[rs1] & self.registers[rs2]

        elif opcode == 'or':
            rd, rs1, rs2 = self._parse_r_type(parts[1:])
            self.registers[rd] = self.registers[rs1] | self.registers[rs2]

        elif opcode == 'xor':
            rd, rs1, rs2 = self._parse_r_type(parts[1:])
            self.registers[rd] = self.registers[rs1] ^ self.registers[rs2]

        # Operaciones de memoria
        elif opcode == 'lw':
            rd, offset, rs1 = self._parse_load(parts[1:])
            address = self.registers[rs1] + offset
            self.registers[rd] = self.memory.get(address, 0)

        elif opcode == 'sw':
            rs2, offset, rs1 = self._parse_store(parts[1:])
            address = self.registers[rs1] + offset
            self.memory[address] = self.registers[rs2]

        # Saltos condicionales
        elif opcode == 'beq':
            rs1, rs2, label = self._parse_branch(parts[1:])
            if self.registers[rs1] == self.registers[rs2]:
                next_pc = self._resolve_label(label)

        elif opcode == 'bne':
            rs1, rs2, label = self._parse_branch(parts[1:])
            if self.registers[rs1] != self.registers[rs2]:
                next_pc = self._resolve_label(label)

        elif opcode == 'blt':
            rs1, rs2, label = self._parse_branch(parts[1:])
            if self.registers[rs1] < self.registers[rs2]:
                next_pc = self._resolve_label(label)

        # Saltos incondicionales
        elif opcode == 'j' or opcode == 'jal':
            label = parts[1]
            next_pc = self._resolve_label(label)
            if opcode == 'jal':
                self.registers[1] = self.pc + 4  # ra = pc + 4

        elif opcode == 'jalr':
            rd, offset, rs1 = self._parse_load(parts[1:])
            self.registers[rd] = self.pc + 4
            next_pc = self.registers[rs1] + offset

        # Instrucciones especiales
        elif opcode == 'li':
            rd = self._parse_register(parts[1])
            imm = int(parts[2])
            self.registers[rd] = imm

        elif opcode == 'mv':
            rd = self._parse_register(parts[1])
            rs = self._parse_register(parts[2])
            self.registers[rd] = self.registers[rs]

        # Syscalls simplificados
        elif opcode == 'ecall':
            # Si a7 (x17) = 1, imprime el entero en a0 (x10)
            if self.registers[17] == 1:
                print(f"Output: {self.registers[10]}")
            # Si a7 (x17) = 10, termina el programa
            elif self.registers[17] == 10:
                self.running = False

        else:
            print(f"Instrucción no soportada: {instruction}")

        # Aseguramos que x0 siempre sea 0
        self.registers[0] = 0

        # Actualizamos el PC
        self.pc = next_pc

    def _parse_register(self, reg_str):
        """Convierte una cadena de registro a su índice numérico."""
        reg_str = reg_str.strip(',')
        if reg_str == 'zero':
            return 0
        elif reg_str == 'ra':
            return 1
        elif reg_str == 'sp':
            return 2
        elif reg_str == 'gp':
            return 3
        elif reg_str == 'tp':
            return 4
        elif reg_str.startswith('t') and '0' <= reg_str[1] <= '6':
            return 5 + int(reg_str[1])  # t0-t6: 5-11
        elif reg_str == 'fp' or reg_str == 's0':
            return 8
        elif reg_str.startswith('s') and '1' <= reg_str[1] <= '11':
            return 8 + int(reg_str[1])  # s1-s11: 9-19
        elif reg_str.startswith('a') and '0' <= reg_str[1] <= '7':
            return 10 + int(reg_str[1])  # a0-a7: 10-17
        elif reg_str.startswith('x'):
            return int(reg_str[1:])
        else:
            raise ValueError(f"Registro no reconocido: {reg_str}")

    def _parse_r_type(self, args):
        """Parsea instrucciones tipo R: add rd, rs1, rs2"""
        rd = self._parse_register(args[0])
        rs1 = self._parse_register(args[1])
        rs2 = self._parse_register(args[2])
        return rd, rs1, rs2

    def _parse_i_type(self, args):
        """Parsea instrucciones tipo I: addi rd, rs1, imm"""
        rd = self._parse_register(args[0])
        rs1 = self._parse_register(args[1])
        imm = int(args[2])
        return rd, rs1, imm

    def _parse_load(self, args):
        """Parsea instrucciones de carga: lw rd, offset(rs1)"""
        rd = self._parse_register(args[0])
        offset_base = args[1].split('(')
        offset = int(offset_base[0])
        rs1 = self._parse_register(offset_base[1].strip(')'))
        return rd, offset, rs1

    def _parse_store(self, args):
        """Parsea instrucciones de almacenamiento: sw rs2, offset(rs1)"""
        rs2 = self._parse_register(args[0])
        offset_base = args[1].split('(')
        offset = int(offset_base[0])
        rs1 = self._parse_register(offset_base[1].strip(')'))
        return rs2, offset, rs1

    def _parse_branch(self, args):
        """Parsea instrucciones de salto condicional: beq rs1, rs2, label"""
        rs1 = self._parse_register(args[0])
        rs2 = self._parse_register(args[1])
        label = args[2]
        return rs1, rs2, label

    def _resolve_label(self, label):
        """Resuelve una etiqueta a su dirección correspondiente."""
        if label in self.memory:
            return self.memory[label]
        try:
            # Intenta interpretar como una dirección absoluta
            return int(label)
        except ValueError:
            raise ValueError(f"Etiqueta no encontrada: {label}")

    def print_state(self):
        """Imprime el estado actual de los registros."""
        print("Estado de registros:")
        for i in range(32):
            alias = ""
            if i == 0:
                alias = "zero"
            elif i == 1:
                alias = "ra"
            elif i == 2:
                alias = "sp"
            elif i == 10:
                alias = "a0"
            elif i == 17:
                alias = "a7"

            if alias:
                print(f"x{i} ({alias}): {self.registers[i]}")
            else:
                print(f"x{i}: {self.registers[i]}")


# Función para ejecutar un programa
def run_riscv_program(program_code):
    """Ejecuta un programa en ensamblador RISC-V y muestra su resultado."""
    simulator = RiscVSimulator()
    simulator.load_program(program_code)
    result = simulator.run()
    print(f"\nResultado final (a0): {result}")
    return result


# Función principal para demostración
if __name__ == "__main__":
    # Este es solo un ejemplo - los programas reales se cargarán desde archivos o entrada del usuario
    example_program = """
# Ejemplo 3: Mayor de tres números
# Este programa encuentra el mayor de tres números
#
# Registros utilizados:
# a0 (x10): Primer número y resultado final
# a1 (x11): Segundo número
# a2 (x12): Tercer número
# a3 (x13): Mayor temporal

mayor_de_tres:
    li a0, 15      # Primer número
    li a1, 7       # Segundo número
    li a2, 42      # Tercer número
    
    mv a3, a0      # Inicializa mayor con el primer número
    
    bge a3, a1, check_third  # Si mayor >= segundo, salta
    mv a3, a1      # Si no, actualiza mayor con segundo
    
check_third:
    bge a3, a2, fin  # Si mayor >= tercero, salta
    mv a3, a2      # Si no, actualiza mayor con tercero
    
fin:
    mv a0, a3      # Mueve el resultado a a0 para retornar
    
    li a7, 1       # Código para imprimir entero
    ecall          # Llamada al sistema para imprimir
    
    li a7, 10      # Código para terminar programa
    ecall          # Llamada al sistema para terminar

    """

    run_riscv_program(example_program)

