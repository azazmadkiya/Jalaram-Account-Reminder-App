with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    content = f.read()

target = '''                                        if (result.isSuccess) {
                                            lastBackupTime = System.currentTimeMillis()
                                            snackbarHostState.showSnackbar("Successfully restored from latest encrypted backup.")
                                        } else {
                                            snackbarHostState.showSnackbar("Failed to restore latest encrypted backup.")
                                        }'''

repl = '''                                        if (result.isSuccess) {
                                            lastBackupTime = System.currentTimeMillis()
                                            snackbarHostState.showSnackbar("Successfully restored from latest encrypted backup.")
                                        } else {
                                            val errMsg = result.exceptionOrNull()?.message ?: "Unknown error"
                                            snackbarHostState.showSnackbar("Failed to restore: $errMsg")
                                        }'''

content = content.replace(target, repl)

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.write(content)
