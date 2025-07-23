import sierra._about as sierra_about


def cli() -> None:
    print(f"sierra-dev {sierra_about.__version__}")
    print(f"Github: {sierra_about.__github__}")
