blank_pattern = [
    {"TEXT": {"REGEX": r".*"}},  # Match the starting word "I"
    {"TEXT": {"REGEX": r"_+"}},  # Match one or more underscores
    {"TEXT": {"REGEX": r"\(.*?\)"}},  # Match text within parentheses
    # {"TEXT": {"REGEX": r"_+"}, "OP": "*"},  # Match zero or more underscores
    {"TEXT": {"REGEX": r".*"}}  # Match the remaining text
]
