import subprocess
import os
import sys

def run_command(command, cwd=None):
    print(f"Esecuzione: {command} in {cwd if cwd else 'root'}")
    try:
        subprocess.check_call(command, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di: {command}")
        sys.exit(1)

def main():
    # 1. Installazione dipendenze Python
    print("--- 1. Installazione dipendenze Backend (Python) ---")
    run_command("pip install -r requirements.txt")

    # 2. Setup Frontend
    print("\n--- 2. Building Frontend (React/Vite) ---")
    frontend_dir = "templates"
    if os.path.exists(os.path.join(frontend_dir, "package.json")):
        run_command("npm install", cwd=frontend_dir)
        run_command("npm run build", cwd=frontend_dir)
    else:
        print("Errore: cartella 'templates' o 'package.json' non trovata.")
        sys.exit(1)

    # 3. Avvio App
    print("\n--- 3. Avvio WebApp su http://localhost:5000 ---")
    print("Nota: Il backend servirà i file statici dalla cartella templates/dist")
    run_command("python app.py")

if __name__ == "__main__":
    main()
