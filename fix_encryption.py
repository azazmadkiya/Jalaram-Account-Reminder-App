import re

with open('app/src/main/java/com/example/data/backup/DatabaseBackupHelper.kt', 'w') as f:
    f.write('''package com.example.data.backup

import android.content.Context
import android.net.Uri
import com.example.data.local.AppDatabase
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import javax.crypto.Cipher
import javax.crypto.CipherInputStream
import javax.crypto.CipherOutputStream
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

object DatabaseBackupHelper {
    private const val DB_NAME = "reminder_database"
    
    // Static keys to ensure backups survive app uninstalls/reinstalls. 
    // In a production app, this should ideally be derived from a user-provided password using PBKDF2.
    private val SECRET_KEY = "ReminderApp_SecureBackupKey_32B!".toByteArray(Charsets.UTF_8)
    private val IV = "ReminderApp_IV16".toByteArray(Charsets.UTF_8)

    suspend fun backupDatabase(context: Context, targetUri: Uri): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            // Force a WAL checkpoint to ensure all data is in the main DB file
            val db = AppDatabase.getDatabase(context)
            db.query(androidx.sqlite.db.SimpleSQLiteQuery("pragma wal_checkpoint(full)")).moveToFirst()

            val dbFile = context.getDatabasePath(DB_NAME)
            if (!dbFile.exists()) {
                return@withContext Result.failure(Exception("Database file not found"))
            }

            // Initialize standard AES Cipher
            val secretKeySpec = SecretKeySpec(SECRET_KEY, "AES")
            val ivSpec = IvParameterSpec(IV)
            val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
            cipher.init(Cipher.ENCRYPT_MODE, secretKeySpec, ivSpec)

            // We need a temporary file to write the encrypted data before copying to targetUri
            val tempEncryptedFile = File(context.cacheDir, "backup_temp.enc")
            if (tempEncryptedFile.exists()) tempEncryptedFile.delete()

            // Encrypt and write DB contents to temp file
            FileInputStream(dbFile).use { inputStream ->
                FileOutputStream(tempEncryptedFile).use { fos ->
                    CipherOutputStream(fos, cipher).use { cipherOut ->
                        inputStream.copyTo(cipherOut)
                    }
                }
            }

            // Copy temp encrypted file to the user-selected Uri
            context.contentResolver.openOutputStream(targetUri)?.use { outputStream ->
                FileInputStream(tempEncryptedFile).use { inputStream ->
                    inputStream.copyTo(outputStream)
                }
            } ?: return@withContext Result.failure(Exception("Could not open target URI"))

            tempEncryptedFile.delete()
            
            Result.success(Unit)
        } catch (e: Exception) {
            e.printStackTrace()
            Result.failure(e)
        }
    }

    suspend fun restoreDatabase(context: Context, sourceUri: Uri): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            // Close existing database
            AppDatabase.getDatabase(context).close()

            // Copy encrypted file from URI to temp file
            val tempEncryptedFile = File(context.cacheDir, "restore_temp.enc")
            if (tempEncryptedFile.exists()) tempEncryptedFile.delete()

            context.contentResolver.openInputStream(sourceUri)?.use { inputStream ->
                FileOutputStream(tempEncryptedFile).use { outputStream ->
                    inputStream.copyTo(outputStream)
                }
            } ?: return@withContext Result.failure(Exception("Could not open source URI"))

            // Initialize standard AES Cipher for decryption
            val secretKeySpec = SecretKeySpec(SECRET_KEY, "AES")
            val ivSpec = IvParameterSpec(IV)
            val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
            cipher.init(Cipher.DECRYPT_MODE, secretKeySpec, ivSpec)

            val dbFile = context.getDatabasePath(DB_NAME)
            
            // Decrypt temp file and write directly to DB file
            val tempDecryptedFile = File(context.cacheDir, "decrypted_temp.db")
            if (tempDecryptedFile.exists()) tempDecryptedFile.delete()

            try {
                FileInputStream(tempEncryptedFile).use { fis ->
                    CipherInputStream(fis, cipher).use { cipherIn ->
                        FileOutputStream(tempDecryptedFile).use { fos ->
                            cipherIn.copyTo(fos)
                        }
                    }
                }
            } catch (e: Exception) {
                return@withContext Result.failure(Exception("Invalid encryption key or corrupted backup."))
            }

            // If decryption succeeded, replace the actual DB file
            if (dbFile.exists()) {
                dbFile.delete()
            }
            tempDecryptedFile.copyTo(dbFile, overwrite = true)
            tempDecryptedFile.delete()
            tempEncryptedFile.delete()
            
            // Delete journal and WAL files so we don't rollback to old state
            val journalFile = context.getDatabasePath("$DB_NAME-journal")
            if (journalFile.exists()) journalFile.delete()
            val walFile = context.getDatabasePath("$DB_NAME-wal")
            if (walFile.exists()) walFile.delete()
            val shmFile = context.getDatabasePath("$DB_NAME-shm")
            if (shmFile.exists()) shmFile.delete()

            AppDatabase.resetInstance()
            
            Result.success(Unit)
        } catch (e: Exception) {
            e.printStackTrace()
            Result.failure(e)
        }
    }
}
''')
