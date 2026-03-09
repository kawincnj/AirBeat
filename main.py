import sys
import os

# Add the current directory to sys.path to ensure absolute imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_menu():
    print("\n" + "="*30)
    print("   AIRBEAT - Main Menu")
    print("="*30)
    print("1. Run Cajon")
    print("2. Run Hand Posture Tool")
    print("Q. Quit")
    print("="*30)

def main():
    while True:
        print_menu()
        choice = input("Select an option: ").strip().lower()

        if choice == '1':
            print("\nStarting Cajon... (Press ESC in window to exit)")
            from python_logic_instruments.Cajon.cajon import run_cajon
            run_cajon()
        elif choice == '2':
            print("\nStarting Hand Posture Tool... (Press ESC in window to exit)")
            # We'll wrap hand_posture.py logic if needed, but for now we can run it as a module
            import plugin.hand_posture
        elif choice == 'q':
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
