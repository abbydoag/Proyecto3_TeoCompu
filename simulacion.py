import yaml
import sys

class MaquinaTuring:
    def __init__(self, config_file):
        self.load_config(config_file)
        self.tape = []
        self.head_position = 0
        self.current_state = None
        self.mt_steps = []
    
    def load_config(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        self.states = set(config['q_states']['q_list'])
        self.initial_state = config['q_states']['initial']
        self.final_states = set([config['q_states']['final']])
        self.alphabet = set(config['alphabet'])
        self.tape_alphabet = set(config['tape_alphabet'])
        self.transitions = {}
        self.test_strings = config['sim_strings']

        #proces. transicioens
        for transition in config['delta']:
            params = transition['params']
            output = transition['output']

            key = (params['initial_state'], params['tape_input'])
            value = (output['final_state'], 
                     output['tape_output'],
                     output['tape_displacement'])
            self.transitions[key] = value

        print("Transiciones cargadas:")
        for k, v in self.transitions.items():
            print(f"  {k} -> {v}")

    def init_tape(self, input_string):
        #iniciar cinta con la cadena
        self.tape = list(input_string)
        self.head_position = 0
        self.current_state = self.initial_state
        self.mt_steps = []

    def get_current_symbol(self):
        #simbolo actual en cabezal
        if self.head_position < 0 or self.head_position >= len(self.tape):
            return ' '
        return self.tape[self.head_position]
    
    def write_symbol(self, symbol):
        #escribe simoblo donde sta cabezal
        if self.head_position < 0:
            # izquierda
            self.tape = [symbol] + self.tape
            self.head_position = 0
        elif self.head_position >= len(self.tape):
            # derecha
            self.tape.append(symbol)
        else:
            self.tape[self.head_position] = symbol
    
    def move_head(self, direction):
        #mover cabeza a izq y der
        if direction == 'L':
            self.head_position -= 1
        elif direction == 'R':
            self.head_position += 1
    
    def get_instant_description(self):
        #descn inst
        tape_copy = self.tape.copy()
        if self.head_position < 0:
            tape_copy = [' '] + tape_copy
            head_pos = 0
        elif self.head_position >= len(tape_copy):
            tape_copy.append(' ')
            head_pos = self.head_position
        else:
            head_pos = self.head_position

        tape_str = ''.join(tape_copy)
        pointer = ' ' * head_pos + '^'
        state_info = f"Estado: {self.current_state}"

        return f"{tape_str}\n{pointer}\n{state_info}"
    
    def simulation(self, input_string, max_steps=1000):
        #sim maquina
        print(f"\n{'='*20}")
        print(f"Simulacion de cadena -'{input_string}'-")
        print(f"{'='*20}")
        self.init_tape(input_string)

        step_count = 0
        accepted = False

        #guardar init. desc
        initial_desc = self.get_instant_description()
        self.mt_steps.append(initial_desc)
        print(f"Configuracion inicial:")
        print(initial_desc)

        while step_count < max_steps:
            current_symbol = self.get_current_symbol()
            transition_key = (self.current_state, current_symbol)

            print(f"\n--- Paso {step_count} ---")
            print(f"Estado actual: {self.current_state}, Simbolo leido: '{current_symbol}'")
            print(f"Buscando transicion para: {transition_key}")

            #verficacion
            if transition_key not in self.transitions:
                print("No hay transición definida -- RECHAZADO")
                break

            #aplicaion transision
            next_state, write_symbol, direction = self.transitions[transition_key]
            print(f"Transicion encontrada: {transition_key} -> ({next_state}, '{write_symbol}', '{direction}')")

            #escribir simbolo
            self.write_symbol(write_symbol)
            
            #mover cabezal
            self.move_head(direction)
            
            #act. estado
            self.current_state = next_state
            
            #guardar desc. isntanteanea
            current_desc = self.get_instant_description()
            self.mt_steps.append(current_desc)
            print(f"Nueva configuracion:")
            print(current_desc)
            
            #verificar estado aceptacion
            if self.current_state in self.final_states:
                accepted = True
                print("Cadena Aceptada (qf alcanzado)")
                break
            
            step_count += 1

            if step_count >= max_steps:
                print("** Limite de pasos alcanzado ***")
        
        # Resultados
        print(f"\n{'='*30}")
        print(f"Resultado final de '{input_string}'")
        print(f"{'='*30}")
        print(f"Estado final: {self.current_state}")
        print(f"Cinta final: '{''.join(self.tape).strip()}'")
        print(f"¿Aceptada?: {'Si' if accepted else 'No'}")
        
        return accepted, self.mt_steps

def main():
    
    config_file = sys.argv[1]
    
    try:
        tm = MaquinaTuring(config_file)
        
        print("╔" + "=" * 58 + "╗")
        print("║ Simulacion Maquina Turin con lenguaje aⁿbⁿ               ║")
        print("╚"+ "=" * 58 + "╝")
        print(f"Estados: {tm.states}")
        print(f"Estado inicial: {tm.initial_state}")
        print(f"Estados finales: {tm.final_states}")
        print(f"Alfabeto: {tm.alphabet}")
        print(f"Alfabeto de cinta: {tm.tape_alphabet}")
        print(f"Cadenas a probar: {tm.test_strings}")
        print(f"Total de transiciones: {len(tm.transitions)}")
        
        #Probar cadenas
        results = []
        for test_string in tm.test_strings:
            accepted, steps = tm.simulation(test_string)
            results.append((test_string, accepted, steps))
            
            print(f"\n{'='*35}")
            print(f"Descripcion instanea de  «{test_string}»")
            print(f"{'='*35}")
            for i, step in enumerate(steps):
                print(f"Paso {i}:")
                print(step)
                print("-" * 35)
        
        #Resumen
        print(f"\n{'#'*40}")
        print("°°°°°° Resumen Final °°°°°°")
        print(f"{'#'*40}")
        for test_string, accepted, steps in results:
            status = " Cadena Aceptada " if accepted else " Cadena Rechazada"
            print(f"'{test_string}': {status}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()