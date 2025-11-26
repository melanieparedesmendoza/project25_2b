# src/final_project/place.py

import random

class Place:
    #Atributos de la clase
    def __init__(self, place_id, host_id, city):
        self.place_id = place_id
        self.host_id = host_id
        self.city = city
        self.rate = 0          # Tarifa nocturna
        self.area = 0          # Área (0, 1, 2, o 3)
        self.neighbors = []    # Lista de place_id de los vecinos
        self.price_history = {0: 0} # {step: ask_price}
        self.occupancy = 0.0     # Ocupación mensual (0.0 a 1.0)

    def setup(self, grid_size, area_rates):
        """Calcula el área, tarifa inicial, precio inicial y vecinos del lugar."""

        # 1. Determinar el Área
        row = self.place_id // grid_size
        col = self.place_id % grid_size
        mid = grid_size // 2

        if row < mid and col < mid:      self.area = 0 # Top-Left
        elif row < mid and col >= mid:   self.area = 1 # Top-Right
        elif row >= mid and col < mid:   self.area = 2 # Bottom-Left
        else:                            self.area = 3 # Bottom-Right

        # 2. Determinar Tarifa (Rate) y Precio Inicial (Ask Price)
        # Obtenemos primero el rango de precios de la area en la que se encuentra el Place
        min_rate, max_rate = area_rates[self.area]
         # Asigna un numero aleatorio dentro de ese rango
        # randint.(limite_inf, limite_sup) genera un numero aleatorio entre los limites que le digas
        self.rate = random.randint(min_rate, max_rate)

        # Precio de venta inicial (900 veces la tarifa)
        initial_ask_price = self.rate * 900
        self.price_history[0] = initial_ask_price

        # 3. Determinar Vecinos (Neighbors) - Movimientos en cruz
        # A partir de la ciudad obetenemos el tamaño de la grid
        grid = self.city.size
        r, c = row, col

        potential_neighbors = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1), (r - 1,c - 1), (r + 1, c + 1), (r - 1, c + 1), (r + 1, c - 1)]

        # Un bucle que se encagar de mirar en todas las 8 direcciones
        for next_r, next_c in potential_neighbors:
            # Aqui comprueba que las celdas adyacentes sean validas, es decir,
            #que ninguna celda esté fuera de la grid.
            if 0 <= next_r < grid and 0 <= next_c < grid:
                 # Aqui calcula el identificador del vecino. Es la operacion inversa a
                # calcaular la fila y columna de un place_id.
                neighbor_id = next_r * grid + next_c

                # Añade identificador del vecino al la lista de vecinos
                self.neighbors.append(neighbor_id)

    def update_occupancy(self):
        #Consultamos el la tarifa del Place
        nightly_rate = self.rate

        #Consultamos la tarifa de la zona
        mean_area_rate = self.city.get_area_avg_rate(self.area)

        #Establecemos los días según el enunciado
        if nightly_rate > mean_area_rate:
            self.occupancy = random.randint(5,15)
        else:
            self.occupancy = random.randint(10,20)

    def calculate_demand(self):
        """
        Actualiza la ocupación (demanda) basándose en la tarifa vs. el promedio del área.
        La ocupación debe ser un valor entre 0.0 y 1.0.
        """
        area_avg_rate = self.city.get_area_avg_rate(self.area)

        # Factor de ajuste: un rate_ratio bajo implica más demanda.
        rate_ratio = self.rate / area_avg_rate if area_avg_rate > 0 else 1.0

        # Fórmula simplificada: Ocupación alta si el precio es bajo, baja si es alto.
        # Usa min/max para asegurar que esté entre 0.0 y 1.0.
        self.occupancy = max(0.2, min(1.0, 1.2 - rate_ratio))

    def get_monthly_earnings(self):
        """Calcula la ganancia mensual (tarifa * ocupación)"""
        return self.rate * self.occupancy

    def get_ask_price(self):
        """Devuelve el precio de venta (ask_price) más reciente."""
        # Obtiene la clave más grande (el paso de tiempo más reciente)
        return self.price_history[max(self.price_history.keys())]