import os
import re
from datetime import datetime
from asistente import NutrIA
from dotenv import load_dotenv
# Los cambios realizados por GEMINI son marcados con "FIX"



load_dotenv()

# FIX: Crear una ruta absoluta para que siempre encuentre el archivo
# sin importar desde dónde ejecutes la terminal.
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DIARIO = os.path.join(DIRECTORIO_BASE, "nutritional_diary.txt")

def parse_macro(pattern, text):
    match = re.search(pattern, text)
    return float(match.group(1)) if match else 0.0

def cargar_diario():
    #Lee el archivo .txt personalizado y lo convierte nuevamente en un diccionario de Python.
    diario = {}
    if not os.path.exists(ARCHIVO_DIARIO):
        return diario

    # FIX: Usar "utf-8-sig" para ignorar caracteres invisibles (BOM)
    with open(ARCHIVO_DIARIO, "r", encoding="utf-8-sig") as f:
        fecha_actual = None
        for linea in f:
            linea = linea.strip()
            if not linea: continue
            
            # Identificar un nuevo segmento de fecha
            if linea.startswith("DATE:"):
                fecha_actual = linea.replace("DATE:", "").strip()
                if fecha_actual not in diario:
                    diario[fecha_actual] = []
                    
            # Identificar un segmento de alimento
            elif linea.startswith("-") and fecha_actual:
                try:
                    # FIX: Limitar el split a 1 para evitar errores si 
                    # el nombre del alimento incluye caracteres especiales
                    partes = linea[1:].split("|", 1)
                    item_str = partes[0].strip()
                    macros_str = partes[1].strip() if len(partes) > 1 else "Cals: 0, Carbs: 0, Protein: 0, Fat: 0"
                    
                    # FIX: Limitar también el split de los corchetes
                    cat_alimento = item_str.split("]", 1)
                    categoria = cat_alimento[0].replace("[", "").strip()
                    alimento = cat_alimento[1].strip() if len(cat_alimento) > 1 else "Desconocido"
                    
                    cals = parse_macro(r"Cals:\s*([\d\.]+)", macros_str)
                    carbs = parse_macro(r"Carbs:\s*([\d\.]+)", macros_str)
                    prot = parse_macro(r"Protein:\s*([\d\.]+)", macros_str)
                    fat = parse_macro(r"Fat:\s*([\d\.]+)", macros_str)
                    
                    diario[fecha_actual].append({
                        "categoria": categoria,
                        "alimento": alimento,
                        "calories": cals,
                        "carbs": carbs,
                        "protein": prot,
                        "fat": fat
                    })
                except Exception as e:
                    # FIX: Mostrar si una línea en específico falla en lugar de saltarla en silencio
                    print(f"Error al leer la línea del historial: {linea}. Detalle: {e}") 
    return diario

def guardar_diario(diario):
    #Escribe el diccionario en un formato .txt 
    with open(ARCHIVO_DIARIO, "w", encoding="utf-8") as f:
        for fecha, comidas in diario.items():
            f.write(f"DATE: {fecha}\n")
            
            total_cals = sum(c.get('calories', 0) for c in comidas)
            total_carbs = sum(c.get('carbs', 0) for c in comidas)
            total_prot = sum(c.get('protein', 0) for c in comidas)
            total_fat = sum(c.get('fat', 0) for c in comidas)
            
            f.write(f"TOTALS | Cals: {total_cals:.1f} | Carbs: {total_carbs:.1f}g | Protein: {total_prot:.1f}g | Fat: {total_fat:.1f}g\n")
            
            for item in comidas:
                cals = item.get('calories', 0)
                carbs = item.get('carbs', 0)
                prot = item.get('protein', 0)
                fat = item.get('fat', 0)
                f.write(f"- [{item['categoria']}] {item['alimento']} | Cals: {cals}, Carbs: {carbs}, Protein: {prot}, Fat: {fat}\n")
            f.write("\n")

def menu_registro_comida(fecha, diario, asistente):
    if fecha not in diario:
        diario[fecha] = []
        print(f"\nNew day created ({fecha})")

    while True:
        print(f"\nFOOD REGISTRATION: {fecha}")
        print("1. Search on FatSecret (API)")
        print("2. Back to main menu")

        opcion = input("\nChoose an option (1-2): ").strip()

        if opcion == "1":
            alimento = input("Enter the food to search on FatSecret (e.g., Burrito): ").strip()
            if alimento:
                # Pedirle al asistente que calcule/promedie los datos
                datos = asistente.consultar(alimento)
                
                print(f"\nNutrIA analyzed the API:\n{datos.get('explanation', 'No explanation provided.')}")
                print(f"Logged Macros -> Calories: {datos.get('calories')}, Carbs: {datos.get('carbs')}g, Protein: {datos.get('protein')}g, Fat: {datos.get('fat')}g")
                
                diario[fecha].append({
                    "categoria": "API Search (FatSecret)", 
                    "alimento": alimento,
                    "calories": datos.get('calories', 0),
                    "carbs": datos.get('carbs', 0),
                    "protein": datos.get('protein', 0),
                    "fat": datos.get('fat', 0)
                })
                
                guardar_diario(diario)
                print(f"\n'{alimento}' successfully registered in your diary for the day.")
            
        elif opcion == "2":
            break
        else:
            print("Invalid option. Please enter 1 or 2.")

def revisar_historial(diario):
    print("\nREGISTERED FOOD HISTORY")
    if not diario:
        print("Your nutritional history is empty.")
        return

    for fecha, comidas in diario.items():
        print(f"\nDate: {fecha}")
        if not comidas:
            print("  No records for this day.")
        else:
            total_cals = sum(c.get('calories', 0) for c in comidas)
            total_carbs = sum(c.get('carbs', 0) for c in comidas)
            total_prot = sum(c.get('protein', 0) for c in comidas)
            total_fat = sum(c.get('fat', 0) for c in comidas)
            
            print(f"  [DAILY TOTALS] Calories: {total_cals:.1f} | Carbs: {total_carbs:.1f}g | Protein: {total_prot:.1f}g | Fat: {total_fat:.1f}g")
            
            for item in comidas:
                print(f"  - [{item['categoria']}] {item['alimento']} | Cals: {item.get('calories',0)}, Carbs: {item.get('carbs',0)}g, Prot: {item.get('protein',0)}g, Fat: {item.get('fat',0)}g")
    print("\n")

def chat_asistente(asistente):
    print("\nChat with NutrIA active. Ask anything, or type 'out' to go back.")
    
    while True:
        entrada = input("\nYou: ").strip()

        if not entrada:
            continue
        elif entrada.lower() == "out": 
            print("Returning to the main menu")
            break
        else:
            print(f"\nAssistant: {asistente.preguntar(entrada)}")

def main():
    load_dotenv()

    asistente = NutrIA()
    diario = cargar_diario()

    while True:
        print("\nNutrIA ")
        print("1. Create / Modify a day (Log meals)")
        print("2. Review your meal history")
        print("3. Chat with NutrIA (Ask questions about nutrition and foods)")
        print("4. Exit program")

        opcion = input("\nChoose an option (1-4): ").strip()
            
        if opcion == "1":
            hoy = datetime.now().strftime("%Y-%m-%d")
            fecha = input(f"\nEnter the date (Press Enter to use today [{hoy}] or type YYYY-MM-DD): ").strip()
            if not fecha:
                fecha = hoy
            menu_registro_comida(fecha, diario, asistente)
            
        elif opcion == "2":
            revisar_historial(diario)
            
        elif opcion == "3":
            chat_asistente(asistente)
            
        elif opcion == "4":
            print("\nProgram finished successfully.")
            break
            
        else:
            print("Invalid option. Please select a number from 1 to 4.")

if __name__ == "__main__":
    main()