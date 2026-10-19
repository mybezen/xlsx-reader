from menu import run_loop


def main() -> None:
# Main Menu Loop
    try:
        run_loop()
    except KeyboardInterrupt:
        print("\nProgram dihentikan pengguna.")


if __name__ == "__main__":
    main()
