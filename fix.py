with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip() == '}, { errorMsg ->':
        skip = True
        continue
    if skip:
        if line.strip() == '},':
            skip = False
            new_lines.append(line)
        continue
    new_lines.append(line)

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.writelines(new_lines)
