import re

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    content = f.read()

# 1. Replace saveBackupLauncher fallback
save_backup_target = '''                            try {
                                saveBackupLauncher.launch(fileName)
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }'''

save_backup_replacement = '''                            try {
                                saveBackupLauncher.launch(fileName)
                            } catch (e: Exception) {
                                fallbackSaveToDownloads(context, fileName, "application/json", { uri ->
                                    coroutineScope.launch {
                                        isLoadingBackup = true
                                        val success = backupManager.exportToFile(uri)
                                        isLoadingBackup = false
                                        if (success) {
                                            lastBackupTime = backupManager.getLastBackupTime()
                                            snackbarHostState.showSnackbar("Backup saved to Downloads folder!")
                                        } else {
                                            snackbarHostState.showSnackbar("Failed to export backup file.")
                                        }
                                    }
                                }, { errorMsg ->
                                    coroutineScope.launch { snackbarHostState.showSnackbar(errorMsg) }
                                })
                            }'''
content = content.replace(save_backup_target, save_backup_replacement)

# 2. Replace openBackupLauncher fallback
open_backup_target = '''                            try {
                                openBackupLauncher.launch(arrayOf("application/json", "*/*"))
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }'''

open_backup_replacement = '''                            try {
                                openBackupLauncher.launch(arrayOf("application/json", "*/*"))
                            } catch (e: Exception) {
                                snackbarHostState.showSnackbar("File picker unavailable. Auto-restoring latest from Downloads...")
                                fallbackGetLatestBackupFromDownloads(context, ".json", { uri ->
                                    coroutineScope.launch {
                                        isLoadingBackup = true
                                        val jsonString = backupManager.readTextFromUri(uri)
                                        isLoadingBackup = false
                                        if (jsonString != null) {
                                            val preview = backupManager.parsePreview(jsonString)
                                            if (preview != null) {
                                                pendingRestoreJson = jsonString
                                                pendingRestorePreview = preview
                                                showRestoreConfirmDialog = true
                                            } else {
                                                snackbarHostState.showSnackbar("Invalid backup format in latest file.")
                                            }
                                        } else {
                                            snackbarHostState.showSnackbar("Could not read latest backup.")
                                        }
                                    }
                                }, { errorMsg ->
                                    coroutineScope.launch { snackbarHostState.showSnackbar(errorMsg) }
                                })
                            }'''
content = content.replace(open_backup_target, open_backup_replacement)

# 3. Replace saveEncryptedBackupLauncher fallback
save_enc_target = '''                            try {
                                saveEncryptedBackupLauncher.launch(fileName)
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }'''

save_enc_replacement = '''                            try {
                                saveEncryptedBackupLauncher.launch(fileName)
                            } catch (e: Exception) {
                                fallbackSaveToDownloads(context, fileName, "application/octet-stream", { uri ->
                                    coroutineScope.launch {
                                        isLoadingBackup = true
                                        val result = com.example.data.backup.DatabaseBackupHelper.backupDatabase(context, uri)
                                        isLoadingBackup = false
                                        if (result.isSuccess) {
                                            lastBackupTime = System.currentTimeMillis()
                                            snackbarHostState.showSnackbar("Encrypted backup saved to Downloads folder!")
                                        } else {
                                            snackbarHostState.showSnackbar("Failed to create encrypted backup.")
                                        }
                                    }
                                }, { errorMsg ->
                                    coroutineScope.launch { snackbarHostState.showSnackbar(errorMsg) }
                                })
                            }'''
content = content.replace(save_enc_target, save_enc_replacement)

# 4. Replace openEncryptedBackupLauncher fallback
open_enc_target = '''                            try {
                                openEncryptedBackupLauncher.launch(arrayOf("application/octet-stream", "*/*"))
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }'''

open_enc_replacement = '''                            try {
                                openEncryptedBackupLauncher.launch(arrayOf("application/octet-stream", "*/*"))
                            } catch (e: Exception) {
                                snackbarHostState.showSnackbar("File picker unavailable. Auto-restoring latest from Downloads...")
                                fallbackGetLatestBackupFromDownloads(context, ".enc", { uri ->
                                    coroutineScope.launch {
                                        isLoadingBackup = true
                                        val result = com.example.data.backup.DatabaseBackupHelper.restoreDatabase(context, uri)
                                        isLoadingBackup = false
                                        if (result.isSuccess) {
                                            lastBackupTime = System.currentTimeMillis()
                                            snackbarHostState.showSnackbar("Successfully restored from latest encrypted backup.")
                                        } else {
                                            snackbarHostState.showSnackbar("Failed to restore latest encrypted backup.")
                                        }
                                    }
                                }, { errorMsg ->
                                    coroutineScope.launch { snackbarHostState.showSnackbar(errorMsg) }
                                })
                            }'''
content = content.replace(open_enc_target, open_enc_replacement)

# 5. Add the helper functions at the end of the file
helpers = '''
fun fallbackSaveToDownloads(
    context: android.content.Context,
    fileName: String,
    mimeType: String,
    onUriCreated: (android.net.Uri) -> Unit,
    onError: (String) -> Unit
) {
    try {
        val resolver = context.contentResolver
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            val contentValues = android.content.ContentValues().apply {
                put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, fileName)
                put(android.provider.MediaStore.MediaColumns.MIME_TYPE, mimeType)
                put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH, android.os.Environment.DIRECTORY_DOWNLOADS)
            }
            val uri = resolver.insert(android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues)
            if (uri != null) {
                onUriCreated(uri)
            } else {
                onError("Failed to create file in Downloads.")
            }
        } else {
            val downloadsDir = android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOWNLOADS)
            if (!downloadsDir.exists()) downloadsDir.mkdirs()
            val file = java.io.File(downloadsDir, fileName)
            onUriCreated(android.net.Uri.fromFile(file))
        }
    } catch (e: Exception) {
        e.printStackTrace()
        onError("Storage permission required or unavailable.")
    }
}

fun fallbackGetLatestBackupFromDownloads(
    context: android.content.Context,
    extension: String,
    onUriFound: (android.net.Uri) -> Unit,
    onError: (String) -> Unit
) {
    try {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            val resolver = context.contentResolver
            val uri = android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI
            val projection = arrayOf(android.provider.MediaStore.MediaColumns._ID, android.provider.MediaStore.MediaColumns.DISPLAY_NAME)
            val cursor = resolver.query(
                uri,
                projection,
                "${android.provider.MediaStore.MediaColumns.DISPLAY_NAME} LIKE ?",
                arrayOf("%$extension"),
                "${android.provider.MediaStore.MediaColumns.DATE_ADDED} DESC"
            )
            cursor?.use {
                if (it.moveToFirst()) {
                    val idColumn = it.getColumnIndexOrThrow(android.provider.MediaStore.MediaColumns._ID)
                    val id = it.getLong(idColumn)
                    val contentUri = android.content.ContentUris.withAppendedId(uri, id)
                    onUriFound(contentUri)
                    return
                }
            }
            onError("No backup ($extension) found in Downloads.")
        } else {
            val downloadsDir = android.os.Environment.getExternalStoragePublicDirectory(android.os.Environment.DIRECTORY_DOWNLOADS)
            val files = downloadsDir.listFiles { _, name -> name.endsWith(extension) }
            if (files != null && files.isNotEmpty()) {
                val latestFile = files.maxByOrNull { it.lastModified() }
                if (latestFile != null) {
                    onUriFound(android.net.Uri.fromFile(latestFile))
                    return
                }
            }
            onError("No backup ($extension) found in Downloads.")
        }
    } catch (e: Exception) {
        e.printStackTrace()
        onError("Failed to search Downloads: ${e.message}")
    }
}
'''

content = content + helpers

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.write(content)
