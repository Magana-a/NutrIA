import json
import os
from datetime import datetime
from asistente import NutrIA
from dotenv import load_dotenv



load_dotenv()

ARCHIVO_DIARIO = "diario_nutricional.json"

def cargar_diario():
    """Loads the food history from a JSON file."""
    if os.path.exists(ARCHIVO_DIARIO):
        with open(ARCHIVO_DIARIO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_diario(diario):
    """Saves the food history to a JSON file."""
    with open(ARCHIVO_DIARIO, "w", encoding="utf-8") as f:
        json.dump(diario, f, indent=4, ensure_ascii=False)

def menu_registro_comida(fecha, diario, asistente):
    """Sub-menu to log meals for a specific day."""
    if fecha not in diario:
        diario[fecha] = []
        print(f"\nNew day created ({fecha})")

    while True:
        print(f"\nFOOD REGISTRATION: {fecha} ")
        print("1. Search on FatSecret (Type manual entry)")
        print("2. Back to main menu")

        opcion = input("\nChoose an option (1-2): ").strip()

        if opcion == "1":
            alimento = input("Enter the food to search on FatSecret (e.g., Burrito): ").strip()
            if alimento:
                explicacion_ia = asistente.consultar_api_y_explicar(alimento)
                print(f"\n NutrIA analyzed the API:\n{explicacion_ia}")
                
                # We keep the dictionary keys in Spanish as requested to maintain functional structures
                diario[fecha].append({"categoria": "API Search (FatSecret)", "alimento": alimento})
                guardar_diario(diario)
                print(f"\n '{alimento}' successfully registered in your diary for the day.")
            
        elif opcion == "2":
            break
        else:
            print(" Invalid option. Please enter 1 or 2.")

def revisar_historial(diario):
    print("\nREGISTERED FOOD HISTORY ")
    if not diario:
        print("Your nutritional history is empty. ")
        return

    for fecha, comidas in diario.items():
        print(f"\nDate: {fecha}")
        if not comidas:
            print("   No records for this day.")
        for item in comidas:
            print(f"  - [{item['categoria']}] {item['alimento']}")
    print(" " )

def chat_asistente(asistente):
    print("\nChat with NutrIA active. Ask anything, or type 'salir' to go back.")
    
    while True:
        entrada = input("\nYou: ").strip()

        if not entrada:
            continue
        elif entrada.lower() == "salir": 
            print("Returning to the main menu...")
            break
        else:
            print(f"\nAssistant: {asistente.preguntar(entrada)}")

def main():
    print("Alberto Magana")
    print("39435")
    print(" ")

    load_dotenv()

    asistente = NutrIA()
    diario = cargar_diario()

    while True:
        print("\n    NUTRIA  \n")
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
            print("\nProgram finished successfully! Take care of your nutrition. 🏃‍♂️")
            break
            
        else:
            print(" Invalid option. Please select a number from 1 to 4.")

if __name__ == "__main__":
    main()