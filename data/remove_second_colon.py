input_file = "data/Meine_Buchliste.yaml"
output_file = "data/Meine_Buchliste.yaml"

with open(input_file, encoding="utf-8") as f:
    lines = f.readlines()

fixed_lines = []
for idx, line in enumerate(lines, 1):
    # Finde Zeilen mit mehr als einem Doppelpunkt
    if line.count(":") > 1:
        first = line.find(":")
        # Entferne alle weiteren Doppelpunkte nach dem ersten
        before = line[:first+1]
        after = line[first+1:].replace(":", "")
        new_line = before + after
        fixed_lines.append(new_line)
        print(f"Zeile {idx}: {line.strip()} -> {new_line.strip()}")
    else:
        fixed_lines.append(line)

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)

print(f"Fertig! Die Datei mit entfernten zweiten und weiteren Doppelpunkten ist: {output_file}")
