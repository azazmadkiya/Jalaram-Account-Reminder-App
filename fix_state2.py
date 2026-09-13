with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    content = f.read()

# Remove the incorrectly placed line
content = content.replace('\n    val storagePermissionState = com.example.notification.rememberStoragePermissionState()}) {', '}) {')

# Find the start of the body of MoreScreen
insert_idx = content.find('fun MoreScreen(')
bracket_idx = content.find('}) {', insert_idx)
if bracket_idx != -1:
    content = content[:bracket_idx + 4] + '\n    val storagePermissionState = com.example.notification.rememberStoragePermissionState()' + content[bracket_idx + 4:]

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.write(content)
