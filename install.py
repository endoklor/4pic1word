import subprocess
import sys

def install(package):
    """Устанавливает пакет через pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    print("Установка необходимых библиотек для игры '4 фото 1 слово'...\n")
    
    try:
        # устанавливаем pygame
        install("pygame")
        print("\n✅ Все необходимые библиотеки успешно установлены!")
    except Exception as e:
        print("\n❌ Ошибка при установке:")
        print(e)

    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()
