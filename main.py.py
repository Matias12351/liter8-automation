import os
import time
import subprocess
import datetime
import json
import sys

LOG_FILE = "logs/usbliter8.log"
CONFIG_FILE = "config.json"
HISTORY_FILE = "logs/history.json"

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_command(cmd, description="", retries=3):
    for attempt in range(retries + 1):
        if description:
            print(f"{Colors.BLUE}[+] {description}{Colors.RESET}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=45)
            if result.stdout.strip():
                print(result.stdout.strip()[:700])
            success = result.returncode == 0
            if success:
                log(f"OK: {description}")
                return True
            else:
                print(f"{Colors.YELLOW}   Intento {attempt+1}/{retries} fallido...{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}   Error: {e}{Colors.RESET}")
        time.sleep(3)
    log(f"FALLÓ después de {retries} intentos: {description}")
    return False

# Cargar configuración e historial
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"model": None, "board": "waveshare_usb_a"}

def save_config(model, board):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"model": model, "board": board}, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

os.makedirs("logs", exist_ok=True)
os.makedirs("firmwares", exist_ok=True)

config = load_config()
history = load_history()
selected_model = config.get("model")
selected_board = config.get("board")

clear()
log("=== USBLiter8 Automatizador v0.6 - Ultra Mejorado ===")

while True:
    print(f"\n{Colors.GREEN}Modelo: {selected_model or 'Ninguno'} | Placa: {selected_board}{Colors.RESET}")
    print("="*80)
    print("1. One-Click Full Bypass (Recomendado)")
    print("2. Flash Firmware a RP2350")
    print("3. Detección USB + Exploit")
    print("4. Bypass Manual")
    print("5. Ver Historial")
    print("6. Cambiar Modelo / Placa")
    print("7. Ver Logs")
    print("8. Salir")
    print("="*80)

    opcion = input(f"{Colors.YELLOW}Elige (1-8): {Colors.RESET}").strip()

    if opcion == "1":  # ONE-CLICK FULL BYPASS
        if not selected_model:
            print(f"{Colors.RED}Primero selecciona modelo (opción 6){Colors.RESET}")
            continue
        log(f"ONE-CLICK FULL BYPASS iniciado - {selected_model}")
        print(f"{Colors.CYAN}Iniciando proceso completo...{Colors.RESET}")
        
        # Auto Recovery Loop
        for intento in range(1, 4):
            print(f"{Colors.YELLOW}Intento {intento}/3...{Colors.RESET}")
            success = run_command("python tools/usbliter8ctl test", "Test Handler")
            if success:
                run_command("python tools/usbliter8ctl demote", "Demote")
                run_command(f"python tools/usbliter8ctl boot firmwares/{selected_model}/ibss_patched.raw", "Boot iBSS")
                run_command(f"python tools/usbliter8ctl boot firmwares/{selected_model}/ibec_patched.raw", "Boot iBEC")
                print(f"{Colors.GREEN}Bypass completado con éxito!{Colors.RESET}")
                break
            time.sleep(3)

    elif opcion == "2":
        log("Flasheando firmware")
        print("Pon placa en BOOTSEL y conecta...")
        input("Presiona Enter cuando aparezca la unidad...")
        uf2 = f"firmwares/usbliter8.{selected_board}.uf2"
        run_command(f"copy {uf2} R:\\", "Copiando UF2")

    elif opcion == "3":
        log("Exploit manual")
        input("Conecta a RP2350 y presiona Enter al ver PWND...")

    elif opcion == "5":
        print(f"{Colors.CYAN}Historial:{Colors.RESET}")
        for dev, data in history.items():
            print(f"   {dev}: {data.get('bypasses', 0)} bypasses | Último: {data.get('last', 'N/A')}")

    elif opcion == "6":
        print("\nModelos:")
        for k, v in {"1":"iPhone 11", "2":"iPhone 11 Pro", "3":"iPhone XS", "4":"iPhone XR"}.items():
            print(f"   {k}. {v}")
        m = input("Elige: ")
        print("\nPlacas:")
        print("   1. Waveshare USB-A")
        print("   2. Pico 2")
        b = input("Elige: ")
        selected_model = {"1":"iPhone11","2":"iPhone11Pro","3":"iPhoneXS","4":"iPhoneXR"}.get(m)
        selected_board = "waveshare_usb_a" if b == "1" else "pico2"
        save_config(selected_model, selected_board)
        print(f"{Colors.GREEN}Guardado!{Colors.RESET}")

    elif opcion == "7":
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                print(f.read()[-5000:])

    elif opcion == "8":
        log("Cerrado por usuario")
        print("¡Éxito con tu herramienta!")
        break

    input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.RESET}")
    clear()