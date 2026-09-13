with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    content = f.read()

target1 = 'coroutineScope.launch { snackbarHostState.showSnackbar("File picker unavailable. Auto-restoring latest from Downloads...") }'
content = content.replace(target1, '// Silently fallback to auto-restore')

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.write(content)
