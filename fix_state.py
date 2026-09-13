with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    content = f.read()

insert_idx = content.find('fun MoreScreen(')
# find the next '{'
bracket_idx = content.find('{', insert_idx)
if bracket_idx != -1:
    content = content[:bracket_idx + 1] + '\n    val storagePermissionState = com.example.notification.rememberStoragePermissionState()' + content[bracket_idx + 1:]

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.write(content)
