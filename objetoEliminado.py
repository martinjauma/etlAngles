# Este codigo borra todo el objeto de llave a llave de un json

import json

def eliminar_objetos(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Iterar sobre cada objeto en la lista "rows"
    for row in data["rows"]:
        # Iterar sobre cada objeto "clip" en la lista "clips"
        for clip in row["clips"]:
            # Verificar si el objeto coincide con los criterios
            if "qualifiers" in clip and "qualifiers_array" in clip["qualifiers"]:
                qualifiers = clip["qualifiers"]["qualifiers_array"]
                # Crear una lista de índices de elementos a eliminar
                indices_a_eliminar = [i for i, q in enumerate(qualifiers) if "category" in q and q["category"] == "ACTION" and "name" in q and q["name"] == "TOU"]
                
                # Eliminar los objetos en orden inverso para evitar problemas de desplazamiento de índices
                for idx in reversed(indices_a_eliminar):
                    del qualifiers[idx]
               

    # Escribir los datos actualizados en el archivo
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

# Ruta al archivo JSON
archivo_json = "datoseliminados.json"

# Llamar a la función para eliminar los objetos
eliminar_objetos(archivo_json)

print("Los objetos que coinciden con los criterios han sido eliminados del archivo JSON.")
