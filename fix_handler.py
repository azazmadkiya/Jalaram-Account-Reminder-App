with open('app/src/main/java/com/example/notification/StoragePermissionHandler.kt', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "The prompt says" in line or "Actually, READ_EXTERNAL_STORAGE" in line or "For Android 13+, generic storage" in line or "But if forced to request" in line:
        continue
    new_lines.append(line)

with open('app/src/main/java/com/example/notification/StoragePermissionHandler.kt', 'w') as f:
    f.writelines(new_lines)
