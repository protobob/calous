"""Entry point for the hiollama package."""
from hiollama.app import HiOllamaChat

def main():
    chat = HiOllamaChat()
    chat.run()

if __name__ == "__main__":
    main()