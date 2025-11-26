# src/final_project/hosts.py

class Host:
    def __init__(self, host_id, place, city):
        self.host_id = host_id
        self.city = city
        self.profits = 0.0
        
        # place es un OBJETO Place
        self.area = place.area
        self.assets = {place.place_id}

        # Para Graph 1:
        self.area_of_origin = place.area

    def update_profits(self, city):
        """Actualiza los fondos del host con las ganancias mensuales de sus listings."""
        total_earnings = 0.0
        # Es crucial usar una copia de self.assets porque la propiedad puede cambiar
        # si una transacción se ejecuta en el paso intermedio.
        #Bucle que pasa por todos los propiedades del host.
        for place_id in list(self.assets): #se puede leer como: Para cada place_id dentro de self.assets haz...
            if place_id in city.places:
                place = city.places[place_id] ## Recuperamos la ciudad a partir de su identificador
                total_earnings += place.get_monthly_earnings() ## Vamos acumulando las ganancias
                # Es lo mismo que: total_earnings = total_earnings + place.get_monthly_earnings()

        self.profits += total_earnings ## Actualizamos el profit con el total acumulado de cada vivienda

    def make_bids(self, city):
        """Genera una lista de ofertas para adquirir propiedades adyacentes."""
        bids = [] # lista vacia que almacenará las ofertas que hará el host
        opportunities = set() # Conjunto vacio de oportunidades

        # 1. Identificar Oportunidades
        for my_place_id in self.assets: ## para cada propiedad que tengo...
            if my_place_id in city.places:
                my_place = city.places[my_place_id] #recupero el objeto al que hace referencia el Place a partir de su identificador
                for neighbor_id in my_place.neighbors: ## Para cada una de las celdas de alrededor de mi Place...
                    neighbor_place = city.places[neighbor_id] # recupero el Place vecino a partir de su identificador
                    # Oportunidad: vecino que NO es propiedad de este host
                    if neighbor_place.host_id != self.host_id:
                        opportunities.add(neighbor_id) # Añadimos el identificador del Place vecino al conjunto de oportunidades

        # 2. Crear Ofertas
        for pid in opportunities: # Para cada identificador que esta en el conjunto de oportunidades...
            place = city.places[pid] # recuperamos el objeto Place a partir de su identificador
            ask_price = place.get_ask_price() # Obtenemos el precio de venta

            # Lógica V1: El host solo puede comprar en su área de origen
            if city.is_v1_active and place.area != self.area_of_origin:
                continue # El host solo puede comprar en su área de origen (V1)
            
            # [Fin] Lógica V1
            

            # Condición de oferta: el host puede pagar
            if self.profits >= ask_price:
                # La oferta (bid_price) es el total de sus ganancias disponibles
                bid = {
                    'place_id': pid,
                    'seller_id': place.host_id,
                    'buyer_id': self.host_id,
                    'spread': self.profits - ask_price,
                    'bid_price': self.profits
                }
                bids.append(bid) # Añadimos la oferta actual a la lista de ofertas

        return bids #Devolvemos las ofertas