# ---------------------------------------------------------------------------
# Input helpers (Lab 9, Section 5.1)
# Each helper keeps asking until it gets a valid value, so the rest of the
# program never continues with incomplete or invalid data.
# ---------------------------------------------------------------------------

def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))   # float() raises ValueError for text like "abc"
            if value <= 0:                 # validation rule
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Please enter a whole number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number, e.g. 3")


def get_non_negative_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a whole number that is zero or more.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number, e.g. 10")


def get_non_empty_string(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value == '':
            print("This field cannot be empty.")
            continue
        return value
