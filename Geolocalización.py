import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"

key = "06418ae5-906d-4244-af0d-206f3466b259" 


def geocoding(location, key):
    """
    Función para obtener latitud, longitud y nombre formateado
    desde la API de geocodificación de Graphhopper.
    """
    while location == "":
        location = input("Ubicación no válida. Ingrese la ubicación de nuevo: ")
        
    geocode_url = "https://graphhopper.com/api/1/geocode?" 
    url = geocode_url + urllib.parse.urlencode({"q": location, "limit": "1", "key": key, "locale": "es"})
    
    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code
    
    if json_status == 200 and len(json_data.get("hits", [])) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]
        
        if "country" in json_data["hits"][0]:
            country = json_data["hits"][0]["country"]
        else:
            country = ""
        
        if "state" in json_data["hits"][0]:
            state = json_data["hits"][0]["state"]
        else:
            state = ""
        
        if len(state) != 0 and len(country) != 0:
            new_loc = name + ", " + state + ", " + country
        elif len(country) != 0:
            new_loc = name + ", " + country
        else:
            new_loc = name
        
        print("URL de la API de Geocodificación para " + new_loc + " (Tipo de ubicación: " + value + ")\n" + url)
    else:
        lat = "null"
        lng = "null"
        new_loc = location
        if json_status != 200:
            mensaje_err = json_data.get("message", "Error de conexión o clave no válida.")
            print("Estado de la API de Geocodificación: " + str(json_status) + "\nMensaje de error: " + mensaje_err)
            
    return json_status, lat, lng, new_loc


# --- BUCLE PRINCIPAL DE LA APLICACIÓN ---

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfiles de vehículos disponibles en Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("car (auto), bike (bicicleta), foot (a pie)")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    
    profile = ["car", "bike", "foot"]
    vehicle = input("Ingrese un perfil de vehículo de la lista anterior (o 's' / 'salir' para finalizar): ").strip().lower()
    
    # Requisito: Opción para salir ingresando "s" o "salir"
    if vehicle in ["s", "salir", "q", "quit"]:
        print("\n¡Gracias por usar el sistema de geolocalización! Programa finalizado.")
        break
    elif vehicle in profile:
        vehicle = vehicle
    else: 
        vehicle = "car"
        print("No se ingresó un perfil válido. Usando el perfil predeterminado 'car'.")
    
    loc1 = input("\nUbicación de origen (o 's' / 'salir' para finalizar): ").strip()
    if loc1.lower() in ["s", "salir", "q", "quit"]:
        print("\n¡Gracias por usar el sistema de geolocalización! Programa finalizado.")
        break
        
    orig = geocoding(loc1, key)
    
    loc2 = input("Ubicación de destino (o 's' / 'salir' para finalizar): ").strip()
    if loc2.lower() in ["s", "salir", "q", "quit"]:
        print("\n¡Gracias por usar el sistema de geolocalización! Programa finalizado.")
        break
        
    dest = geocoding(loc2, key)
    
    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        op = "&point=" + str(orig[1]) + "%2C" + str(orig[2])
        dp = "&point=" + str(dest[1]) + "%2C" + str(dest[2])
        
        # Requisito: "locale": "es" solicita a Graphhopper la narrativa/instrucciones en español
        paths_url = route_url + urllib.parse.urlencode({"key": key, "vehicle": vehicle, "locale": "es"}) + op + dp
        
        respuesta_ruta = requests.get(paths_url)
        paths_status = respuesta_ruta.status_code
        paths_data = respuesta_ruta.json()
        
        print("Estado de la API de Routing: " + str(paths_status))
        print("URL de la API de Routing:\n" + paths_url)
        print("=================================================")
        print("Indicaciones desde " + orig[3] + " hasta " + dest[3] + " en " + vehicle)
        print("=================================================")
        
        if paths_status == 200:
            miles = (paths_data["paths"][0]["distance"]) / 1000 / 1.61
            km = (paths_data["paths"][0]["distance"]) / 1000
            sec = int(paths_data["paths"][0]["time"] / 1000 % 60)
            min = int(paths_data["paths"][0]["time"] / 1000 / 60 % 60)
            hr = int(paths_data["paths"][0]["time"] / 1000 / 60 / 60)
            
            # Requisito: Valores numéricos formateados con un máximo de 2 decimales (.2f)
            print("Distancia recorrida: {0:.2f} millas / {1:.2f} km".format(miles, km))
            print("Duración del viaje: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
            print("=================================================")
            
            # Requisito: Narrativa e instrucciones paso a paso en español con 2 decimales
            for each in range(len(paths_data["paths"][0]["instructions"])):
                path = paths_data["paths"][0]["instructions"][each]["text"]
                distance = paths_data["paths"][0]["instructions"][each]["distance"]
                print("{0} ( {1:.2f} km / {2:.2f} millas )".format(path, distance / 1000, (distance / 1000) / 1.61))
                
            print("=================================================")
        else:
            mensaje_error = paths_data.get("message", "No se encontró una conexión por tierra entre las ubicaciones.")
            print("Mensaje de error: " + mensaje_error)
            print("*************************************************")