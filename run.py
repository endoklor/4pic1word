import subprocess
import sys
import os

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    try:
        install("pygame")
    except:
        input("Ошибка при установке библиотек. Нажмите Enter для выхода...")
        sys.exit(1)

    if os.path.exists("main.py"):
        subprocess.run([sys.executable, "main.py"])
    else:
        input("Файл main.py не найден. Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
