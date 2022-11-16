

def parse_expense(text: str):
    return text.split()


def parse_add_category(text: str):
    return ' '.join(text.split()[2:])

def parse_report(text: str):
    return text.split()[1]
