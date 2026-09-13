import re

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    content = f.read()

# Fix the two occurrences
target_1 = '''snackbarHostState.showSnackbar("File picker unavailable. Auto-restoring latest from Downloads...")'''
repl_1 = '''coroutineScope.launch { snackbarHostState.showSnackbar("File picker unavailable. Auto-restoring latest from Downloads...") }'''
content = content.replace(target_1, repl_1)

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.write(content)
