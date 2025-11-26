# src/final_project/city.py

import random
import pandas as pd
from .place import Place
from .hosts import Host

class City:
    def __init__(self, size, area_rates, seed=42, is_v1_active=False):
        self.size = size
        self.area_rates = area_rates
        self.step = 0
        self.places = {}
        self.hosts = {}
        self.is_v1_active = is_v1_active # Flag para la versión modificada

        # random.seed(seed) # Asegura la reproducibilidad

    # METODO 1
    def initialize(self):
        """Crea todos los objetos Place y Host iniciales."""

        host_id_counter = 0 # aumentaremos este contador a medida que avanzamos de celda
        total_places = self.size * self.size # 10 x 10 = 100 celdas -> los place_id seran: 0, 1, 2, ... , 99

        # range(num): genera una lista que contiene los numeros del 0 al num-1, por ejemplo: range(5) -> [0, 1, 2, 3, 4]
        # Entonces for place_id in range(total_places) seria equivalente a for place_id in [0, 1, ..., total_places-1]
        # Esto significa que place_id ira adquiriendo los valores de la lista en cada iteracion, es decir:
        #   iteracion 1: place_id = 0
        #   iteracion 2: place_id = 1
        #   iteracion 3: place_id = 2
        #   ...
        #   iteracion 100: place_id = 99

        for place_id in range(total_places):
            #Creamos una INSTANCIA de la clase PLACE
            place = Place(place_id, host_id_counter, self)

             # Inicializamos la instancia con la informacion necesaria
            place.setup(self.size, self.area_rates)

             # Añadimos el Place generado al diccionario que almacena todos los Places de la ciudad
            # El diccionario tiene la forma de {key: valor} -> {place_id: instacia_de_la_clase_Place}
            self.places[place_id] = place

            # Crea el Host. Le pasamos el área de origen
            host = Host(host_id_counter, place, self)
            self.hosts[host_id_counter] = host

            host_id_counter += 1 # Aumentamos el contador, es decir pasamos a la siguiente celda

     # METODO AUXLIAR
    def get_area_avg_rate(self, area):
        """Calcula la tarifa promedio actual en un área."""
        rates = [place.rate for place in self.places.values() if place.area == area]
        # Devuelve un valor por defecto si no hay listings (aunque siempre habrá)
        return sum(rates) / len(rates) if rates else 100

    # METODO 2
    def approve_bids(self, bids):
        """Ordena las ofertas y determina qué transacciones son válidas."""
        if not bids: #si no hay ofertas...
            return [] # devolvemos una lista vacia de ofertas aprovadas

          # Esto lo que hace es pasar las ofertas a un DataFrame (es como una hoja de calculo del excel)
        df_bids = pd.DataFrame(bids)
        # Ordenar por 'spread' descendente (oferta más alta sobre el precio de venta)
        df_bids = df_bids.sort_values(by='spread', ascending=False)

         # Una lista vacia donde iremos guardando las transacciones que vayamos aprovando
        approved_transactions = []

         # Conjunto vacio donde iremos guardando los Places que se han aprovado.
        # Esto lo hacemos para consultar que Places han sido comprados y cuales no de forma rapida
        sold_places = set()

        # Lo mismo que con sold_places pero con compradores
        buyers_who_bought = set()

        for _, bid in df_bids.iterrows():
            place_id = bid['place_id']
            buyer_id = bid['buyer_id']

            # 2. Comprobar disponibilidad
            #Un comprador puede comprar como mucho 1 Place/propiedad (es decir 0 o 1 propiedades) al mes (mes = step)
            # Y una propiedad puede ser vendida solo una vez por iteracion (es decir, solo puede ser vendida una vez al mes)
            # if place_id not in sold_places: es decir si el identificador no esta marcado como vendido
            # buyer_id not in buyers_who_bought: y el comprador aun no ha realizado ninguna compra
            if place_id not in sold_places and buyer_id not in buyers_who_bought:

                # Comprobar que el host comprador todavía tiene fondos (por si se modificó)
                buyer = self.hosts.get(buyer_id) # obtenemos la instancia del host a partir de su id
                if buyer and buyer.profits >= bid['bid_price']: # si el host tiene fondos suficientes
                    approved_transactions.append(bid.to_dict()) # añadimos la transaccion a la lista de transacciones aprovadas. bid.to_dict() hace que el dataframe vuelva a ser un diccionario.
                    sold_places.add(place_id) # actualizamos el conjunto de Places vendidos con la propiedad que acabamos de marcar como vendida
                    buyers_who_bought.add(buyer_id) # lo mismo pero con el host

        return approved_transactions # Devolvemos la lista de transacciones aprovadas
    
     # METODO 3
    def execute_transactions(self, transactions):
        """Realiza las transferencias de dinero y propiedad."""
        for tx in transactions:
             # Para cada una de las transacciones recuperamos la informacion que nos pide el enunciado
            # Primero obtenmos los identificadores
            place_id = tx['place_id']
            buyer_id = tx['buyer_id']
            seller_id = tx['seller_id']
            bid_price = tx['bid_price']

             # Y ahora las intancias a partir de los identidicadores
            place = self.places[place_id]
            buyer = self.hosts[buyer_id]
            seller = self.hosts[seller_id]

            # 1. Actualizar Propiedad
            if place_id in seller.assets:
                seller.assets.remove(place_id)  #Eliminamos la propiedad de los assets que posee el seller
            buyer.assets.add(place_id) # añadimos la propiedad comprada al comprador
            place.host_id = buyer_id # actualizamos el propietario de la vivienda comprada, es decir, asignamos el id del comprador a la vivienda

            # 2. Actualizar Fondos
            buyer.profits -= bid_price
            seller.profits += bid_price

            # 3. Registrar Historial de Precios
            place.price_history[self.step] = bid_price

    #METODO 4
    def clear_market(self):
        """Coordina el proceso completo de clearing."""
        all_bids = []
        for host in self.hosts.values(): # Para cada uno de los hosts miramos si...
            # tienes propiedades y su presupuesto es mayor a 0.
            if host.assets and host.profits > 0:
                # extend es como append pero para varios elementos. Añades todas las bids creadas a all_bids
                all_bids.extend(host.make_bids(self))

        approved_transactions = self.approve_bids(all_bids) #Creamos todas las transacciones

        if approved_transactions: # si hay una o mas transacciones las ejecutamos
            self.execute_transactions(approved_transactions)

        return approved_transactions # devolvemos las transacciones aprovadas

    #METODO 5
    def iterate(self):
        """Avanza la simulación un paso (mes)."""
        self.step += 1

        # 1. Actualizar Ocupación/Demanda
        for place in self.places.values():
            place.update_occupancy()

        # 2. Actualizar Ganancias (antes de pujar)
        for host in self.hosts.values():
            host.update_profits(self)

        # 3. Limpiar el Mercado (Bids y Transactions)
        transactions = self.clear_market()

        return transactions