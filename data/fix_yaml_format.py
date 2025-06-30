import re

input_file = "data/Meine_Buchliste.yaml"
output_file = "data/Meine_Buchliste_fixed.yaml"

with open(input_file, encoding="utf-8") as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # Entferne führende Leerzeichen, außer bei Listeneinträgen
    if re.match(r'^\s+- ', line):
        fixed_lines.append(line.lstrip())
    elif re.match(r'^\s*$', line):
        fixed_lines.append(line)  # Leere Zeile bleibt leer
    else:
        fixed_lines.append(line.lstrip())

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print(f"Fertig! Die bereinigte Datei ist: {output_file}")
