import re

input_file = "data/Meine_Buchliste.yaml"
output_file = "data/Meine_Buchliste.yaml"  # Backup vorher empfohlen!

def remove_quotes(text):
    return text.replace('"', '')

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

out_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    match = re.match(r"^(\s*)Description:(.*)", line)
    if match:
        indent = match.group(1)
        desc_lines = []
        # Falls direkt nach Description: noch Text steht, nimm ihn mit
        rest = match.group(2)
        if rest.strip():
            desc_lines.append(rest.lstrip())
        i += 1
        # Sammle alle Zeilen bis ImageURL:
        while i < len(lines):
            next_line = lines[i]
            if re.match(rf"^{indent}ImageURL:", next_line):
                break
            desc_lines.append(next_line.strip())
            i += 1
        # Baue den String, entferne Anführungszeichen, fasse alles zu einer Zeile zusammen
        desc_content = " ".join(l for l in desc_lines if l).strip()
        desc_content = remove_quotes(desc_content)
        out_lines.append(f'{indent}Description: "{desc_content}"\n')
        # Jetzt die ImageURL-Zeile übernehmen
        if i < len(lines):
            out_lines.append(lines[i])
            i += 1
    else:
        out_lines.append(line)
        i += 1

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(out_lines)

print("Alle Description-Felder wurden als einzeiliger String zwischen Description: und ImageURL: in Anführungszeichen gesetzt.")
