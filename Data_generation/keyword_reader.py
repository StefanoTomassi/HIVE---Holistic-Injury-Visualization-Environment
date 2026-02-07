def read_keywords(dir_file: str) -> dict:
    """Reads an LS-DYNA keyword file and returns a dictionary of keywords and their associated lines.
    Args:
        dir_file (str): Path to the LS-DYNA keyword file.
    Returns:
        dict: A dictionary where keys are keywords (without the leading '*') and values are lists of lines associated with each keyword."""

    file = open(dir_file, 'r')
    cards = {}
    counters = {}
    current_keyword = None
    for line in file:
        line = line.rstrip('\n\r')
        if line.startswith('*'):
            keyword_base = line
            counters[keyword_base] = counters.get(keyword_base, 0) + 1
            current_keyword = f"{keyword_base}_{counters[keyword_base]}"
            cards[current_keyword] = []
            continue
        if line.startswith('$'):
            continue
        if current_keyword is not None:
            cards[current_keyword].append(line)
    file.close()
    return cards