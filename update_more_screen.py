import re

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'r') as f:
    content = f.read()

# Remove fallbackSaveToDownloads function entirely
fallback_func_pattern = r'fun fallbackSaveToDownloads\([\s\S]*?^}$'
content = re.sub(fallback_func_pattern, '', content, flags=re.MULTILINE | re.DOTALL)

# Insert the permission state initialization
insert_idx = content.find('val permissionState = rememberNotificationPermissionState()')
if insert_idx != -1:
    content = content[:insert_idx] + 'val storagePermissionState = com.example.notification.rememberStoragePermissionState()\n    ' + content[insert_idx:]

# Replace Backup Action 2: Save to device file
backup_action_2_pattern = r'// Backup Action 2: Save to device file[\s\S]*?modifier = Modifier\.fillMaxWidth\(\),'
new_backup_action_2 = '''// Backup Action 2: Save to device file
                    OutlinedButton(
                        onClick = {
                            if (!storagePermissionState.hasPermission) {
                                storagePermissionState.requestPermission()
                                return@OutlinedButton
                            }
                            val timestamp = SimpleDateFormat("yyyyMMdd_HHmm", Locale.getDefault()).format(Date())
                            val fileName = "Reminder_Backup_$timestamp.json"
                            try {
                                saveBackupLauncher.launch(fileName)
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),'''
content = re.sub(backup_action_2_pattern, new_backup_action_2, content)

# Replace Restore Action: Pick File to Restore
restore_action_1_pattern = r'// Restore Action: Pick File to Restore[\s\S]*?try \{\s*openBackupLauncher\.launch\(arrayOf\("application/json", "\*/\*"\)\)\s*\} catch \(e: Exception\) \{\s*coroutineScope\.launch \{ snackbarHostState\.showSnackbar\("Cannot open file picker\."\) \}\s*\}'
new_restore_action_1 = '''// Restore Action: Pick File to Restore
                    FilledTonalButton(
                        onClick = {
                            if (!storagePermissionState.hasPermission) {
                                storagePermissionState.requestPermission()
                                return@FilledTonalButton
                            }
                            try {
                                openBackupLauncher.launch(arrayOf("application/json", "*/*"))
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }'''
content = re.sub(restore_action_1_pattern, new_restore_action_1, content)

# Replace OutlinedButton for Export Encrypted Backup
export_enc_pattern = r'OutlinedButton\(\s*onClick = \{\s*val timestamp = SimpleDateFormat\("yyyyMMdd_HHmm", Locale\.getDefault\(\)\)\.format\(Date\(\)\)\s*val fileName = "Reminder_Encrypted_\$timestamp\.enc"\s*try \{\s*saveEncryptedBackupLauncher\.launch\(fileName\)\s*\} catch \(e: Exception\) \{\s*fallbackSaveToDownloads[\s\S]*?\}\s*\}\s*\},'
new_export_enc = '''OutlinedButton(
                        onClick = {
                            if (!storagePermissionState.hasPermission) {
                                storagePermissionState.requestPermission()
                                return@OutlinedButton
                            }
                            val timestamp = SimpleDateFormat("yyyyMMdd_HHmm", Locale.getDefault()).format(Date())
                            val fileName = "Reminder_Encrypted_$timestamp.enc"
                            try {
                                saveEncryptedBackupLauncher.launch(fileName)
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }
                        },'''
content = re.sub(export_enc_pattern, new_export_enc, content)

# Replace FilledTonalButton for Restore Encrypted Backup
restore_enc_pattern = r'FilledTonalButton\(\s*onClick = \{\s*try \{\s*openEncryptedBackupLauncher\.launch\(arrayOf\("application/octet-stream", "\*/\*"\)\)\s*\} catch \(e: Exception\) \{\s*coroutineScope\.launch \{ snackbarHostState\.showSnackbar\("Cannot open file picker\."\) \}\s*\}\s*\},'
new_restore_enc = '''FilledTonalButton(
                        onClick = {
                            if (!storagePermissionState.hasPermission) {
                                storagePermissionState.requestPermission()
                                return@FilledTonalButton
                            }
                            try {
                                openEncryptedBackupLauncher.launch(arrayOf("application/octet-stream", "*/*"))
                            } catch (e: Exception) {
                                coroutineScope.launch { snackbarHostState.showSnackbar("Cannot open file picker.") }
                            }
                        },'''
content = re.sub(restore_enc_pattern, new_restore_enc, content)

with open('app/src/main/java/com/example/ui/more/MoreScreen.kt', 'w') as f:
    f.write(content)
