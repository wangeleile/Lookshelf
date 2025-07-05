import re

input_file = "data/Meine_Buchliste.yaml"
output_file = "data/Meine_Buchliste.yaml"  # Backup vorher empfohlen!
search_field = "Description"  # Hier das gewünschte Feld eintragen
stop_field = "image_url"       # Hier das Feld eintragen, bis wohin gesammelt wird

def remove_quotes(text):
    return text.replace('"', '')

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

out_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    match = re.match(rf"^(\s*){search_field}:(.*)", line)
    if match:
        indent = match.group(1)
        desc_lines = []
        # Falls direkt nach dem Feld noch Text steht, nimm ihn mit
        rest = match.group(2)
        if rest.strip():
            desc_lines.append(rest.lstrip())
        i += 1
        # Sammle alle Zeilen bis zum nächsten gewünschten Feld (stop_field)
        while i < len(lines):
            next_line = lines[i]
            if re.match(rf"^{indent}{stop_field}:", next_line):
                break
            desc_lines.append(next_line.strip())
            i += 1
        # Baue den String, entferne Anführungszeichen, fasse alles zu einer Zeile zusammen
        desc_content = " ".join(l for l in desc_lines if l).strip()
        desc_content = remove_quotes(desc_content)
        out_lines.append(f'{indent}{search_field}: "{desc_content}"\n')
        # Jetzt die stop_field-Zeile übernehmen
        if i < len(lines):
            out_lines.append(lines[i])
            i += 1
    else:
        out_lines.append(line)
        i += 1

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(out_lines)

print(f"Alle {search_field}-Felder wurden als einzeiliger String zwischen {search_field}: und {stop_field}: in Anführungszeichen gesetzt.")
