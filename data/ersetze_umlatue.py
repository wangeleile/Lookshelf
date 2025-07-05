import os

# Mapping von falsch konvertierten Umlauten zu den richtigen Zeichen
REPLACEMENTS = {
    "Ã¤": "ä",
    "Ã„": "Ä",
    "Ã¶": "ö",
    "Ã–": "Ö",
    "Ã¼": "ü",
    "Ãœ": "Ü",
    "ÃŸ": "ß",
    "Ã ": "à",
    "Ã¡": "á",
    "Ã¢": "â",
    "Ã£": "ã",
    "Ã©": "é",
    "Ã¨": "è",
    "Ãª": "ê",
    "Ã¹": "ù",
    "Ãº": "ú",
    "Ã»": "û",
    "Ã±": "ñ",
    "Ã§": "ç",
    "â€“": "–",
    "â€”": "—",
    "â€ž": "„",
    "â€œ": "“",
    "â€": "”",
    "â€˜": "‘",
    "â€™": "’",
    "â€¢": "•",
    "â€¦": "…",
    "Â": "",
    "â‚¬": "€",
    "â„¢": "™",
}

def fix_umlauts(text):
    for wrong, right in REPLACEMENTS.items():
        text = text.replace(wrong, right)
    return text

def main():
    inputfile = "data/Meine_Buchliste_test.yaml"  # <-- Hier den Inputfile anpassen
    outputfile = inputfile.replace(".yaml", "_fixed.yaml")

    with open(inputfile, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    fixed = fix_umlauts(content)

    with open(outputfile, "w", encoding="utf-8") as f:
        f.write(fixed)

    print(f"Umlaute in '{inputfile}' wurden ersetzt und in '{outputfile}' gespeichert.")

if __name__ == "__main__":
    main()