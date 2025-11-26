# main.py

import random
import matplotlib.pyplot as plt
import pandas as pd
from src.final_project.city import City

# Configuración
GRID_SIZE = 10
AREA_RATES = {0: (100, 200), 1: (50, 250), 2: (250, 350), 3: (150, 450)}
SIMULATION_STEPS = 180 # 15 años * 12 meses
SEED = 42

def run_simulation(city):
    """Ejecuta el bucle principal de la simulación."""
    
    # Inicializar la ciudad
    city.initialize()
    
    # Datos para el seguimiento a lo largo del tiempo (opcional, pero útil para graph2)
    # Ejemplo: seguimiento del precio medio de venta
    avg_price_history = [] 
    
    # Bucle de simulación
    for _ in range(1, SIMULATION_STEPS + 1):
        city.iterate()
        
        # Recopilar datos para el seguimiento
        all_prices = [place.get_ask_price() for place in city.places.values()]
        if all_prices:
            avg_price_history.append(sum(all_prices) / len(all_prices))

    return avg_price_history

def calculate_host_wealth(city):
    """Calcula la riqueza total de cada host."""
    wealth_data = []
    
    for host_id, host in city.hosts.items():
        total_assets_value = 0
        # Suma el precio de venta más reciente de todas las propiedades
        for place_id in host.assets:
            place = city.places[place_id]
            total_assets_value += place.get_ask_price()
            
        # Riqueza = Ganancias + Valor de los Activos
        total_wealth = host.profits + total_assets_value
        
        wealth_data.append({
            'host_id': host_id,
            'wealth': total_wealth,
            'area_of_origin': host.area_of_origin
        })
        
    return pd.DataFrame(wealth_data)