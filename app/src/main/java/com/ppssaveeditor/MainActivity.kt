package com.ppssaveeditor

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.documentfile.DocumentFile
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

class MainActivity : AppCompatActivity() {
    
    private lateinit var btnSelectSaveData: Button
    private lateinit var tvSaveDataPath: TextView
    private lateinit var tvGameTitle: TextView
    private lateinit var tvSaveTitle: TextView
    private lateinit var tvSaveDetail: TextView
    private lateinit var btnDecrypt: Button
    private lateinit var btnEncrypt: Button
    private lateinit var btnHexEditor: Button
    private lateinit var btnCheatCode: Button
    
    private var currentSaveDataUri: Uri? = null
    private var currentSaveDataDir: File? = null
    private var decryptedData: ByteArray? = null
    private var currentDataFile: File? = null
    private var currentSFOData: SFOParser.SFOData? = null
    
    private val sfoParser = SFOParser()
    private val crypto = SaveDataCrypto()
    
    private val pickDirectory = registerForActivityResult(
        ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        uri?.let {
            currentSaveDataUri = it
            processSaveDataDirectory(it)
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        checkPermissions()
    }
    
    private fun initViews() {
        btnSelectSaveData = findViewById(R.id.btnSelectSaveData)
        tvSaveDataPath = findViewById(R.id.tvSaveDataPath)
        tvGameTitle = findViewById(R.id.tvGameTitle)
        tvSaveTitle = findViewById(R.id.tvSaveTitle)
        tvSaveDetail = findViewById(R.id.tvSaveDetail)
        btnDecrypt = findViewById(R.id.btnDecrypt)
        btnEncrypt = findViewById(R.id.btnEncrypt)
        btnHexEditor = findViewById(R.id.btnHexEditor)
        btnCheatCode = findViewById(R.id.btnCheatCode)
        
        btnSelectSaveData.setOnClickListener {
            openDirectoryPicker()
        }
        
        btnDecrypt.setOnClickListener {
            decryptSaveData()
        }
        
        btnEncrypt.setOnClickListener {
            encryptSaveData()
        }
        
        btnHexEditor.setOnClickListener {
            openHexEditor()
        }
        
        btnCheatCode.setOnClickListener {
            openCheatCodeActivity()
        }
    }
    
    private fun checkPermissions() {
        when {
            Build.VERSION.SDK_INT >= Build.VERSION_CODES.R -> {
                if (!Environment.isExternalStorageManager()) {
                    val intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                    startActivity(intent)
                }
            }
            else -> {
                val permissions = arrayOf(
                    Manifest.permission.READ_EXTERNAL_STORAGE,
                    Manifest.permission.WRITE_EXTERNAL_STORAGE
                )
                
                if (permissions.any {
                    ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
                }) {
                    ActivityCompat.requestPermissions(this, permissions, 100)
                }
            }
        }
    }
    
    private fun openDirectoryPicker() {
        pickDirectory.launch(null)
    }
    
    private fun processSaveDataDirectory(uri: Uri) {
        lifecycleScope.launch {
            try {
                val docFile = androidx.documentfile.DocumentFile.fromTreeUri(this@MainActivity, uri)
                tvSaveDataPath.text = docFile?.name ?: uri.path ?: "未知路径"
                
                // 查找PARAM.SFO文件
                val sfoFile = findFileInDirectory(uri, "PARAM.SFO")
                val dataFile = findDataFile(uri)
                
                if (sfoFile != null) {
                    currentSFOData = withContext(Dispatchers.IO) {
                        sfoParser.parse(sfoFile)
                    }
                    
                    currentSFOData?.let { sfo ->
                        tvGameTitle.text = "游戏标题: ${sfo.gameTitle}"
                        tvSaveTitle.text = "存档标题: ${sfo.saveTitle}"
                        tvSaveDetail.text = "存档详情: ${sfo.saveDetail}"
                    }
                } else {
                    Toast.makeText(this@MainActivity, "未找到PARAM.SFO文件", Toast.LENGTH_SHORT).show()
                }
                
                if (dataFile != null) {
                    currentDataFile = dataFile
                    decryptedData = null
                    updateButtonStates()
                } else {
                    Toast.makeText(this@MainActivity, "未找到数据文件", Toast.LENGTH_SHORT).show()
                }
                
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "错误: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private suspend fun findFileInDirectory(treeUri: Uri, fileName: String): File? =
        withContext(Dispatchers.IO) {
            try {
                val docFile = androidx.documentfile.DocumentFile.fromTreeUri(this@MainActivity, treeUri)
                val file = docFile?.findFile(fileName)
                file?.uri?.let { uri: Uri ->
                    copyUriToTemp(uri, fileName)
                }
            } catch (e: Exception) {
                null
            }
        }
    
    private suspend fun findDataFile(treeUri: Uri): File? = withContext(Dispatchers.IO) {
        try {
            val docFile = androidx.documentfile.DocumentFile.fromTreeUri(this@MainActivity, treeUri)
            val possibleNames = listOf("DATA.BIN", "data.bin", "SECURE.BIN", "secure.bin", "SDDATA.BIN", "sddata.bin")
            
            for (name in possibleNames) {
                val file = docFile?.findFile(name)
                if (file != null) {
                    return@withContext copyUriToTemp(file.uri, name)
                }
            }
            null
        } catch (e: Exception) {
            null
        }
    }
    
    private fun copyUriToTemp(uri: Uri, fileName: String): File {
        val tempFile = File(cacheDir, fileName)
        contentResolver.openInputStream(uri)?.use { input ->
            tempFile.outputStream().use { output ->
                input.copyTo(output)
            }
        }
        return tempFile
    }
    
    private fun decryptSaveData() {
        val dataFile = currentDataFile ?: return
        
        lifecycleScope.launch {
            withContext(Dispatchers.IO) {
                val data = dataFile.readBytes()
                val result = crypto.autoDecrypt(data)
                
                withContext(Dispatchers.Main) {
                    if (result.success) {
                        decryptedData = result.data
                        updateButtonStates()
                        Toast.makeText(this@MainActivity, "解密成功", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@MainActivity, "解密失败: ${result.error}", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }
    }
    
    private fun encryptSaveData() {
        val data = decryptedData ?: return
        val dataFile = currentDataFile ?: return
        
        lifecycleScope.launch {
            withContext(Dispatchers.IO) {
                // 检测原始加密模式
                val originalData = dataFile.readBytes()
                val mode = crypto.detectEncryptionMode(originalData)
                
                val result = crypto.encrypt(data, if (mode > 0) mode else 1)
                
                withContext(Dispatchers.Main) {
                    if (result.success) {
                        result.data?.let { encrypted ->
                            // 保存到缓存文件
                            val tempFile = File(cacheDir, "encrypted_${dataFile.name}")
                            tempFile.writeBytes(encrypted)
                            Toast.makeText(
                                this@MainActivity, 
                                "加密完成，请在导出菜单中保存", 
                                Toast.LENGTH_SHORT
                            ).show()
                        }
                    } else {
                        Toast.makeText(this@MainActivity, "加密失败: ${result.error}", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }
    }
    
    private fun openHexEditor() {
        val data = decryptedData
        if (data == null) {
            Toast.makeText(this, "请先解密存档", Toast.LENGTH_SHORT).show()
            return
        }
        
        val intent = Intent(this, HexEditorActivity::class.java)
        intent.putExtra("data", data)
        hexEditorLauncher.launch(intent)
    }
    
    private val hexEditorLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            result.data?.getByteArrayExtra("modifiedData")?.let {
                decryptedData = it
                Toast.makeText(this, "数据已修改", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun openCheatCodeActivity() {
        val data = decryptedData
        if (data == null) {
            Toast.makeText(this, "请先解密存档", Toast.LENGTH_SHORT).show()
            return
        }
        
        val intent = Intent(this, CheatCodeActivity::class.java)
        intent.putExtra("data", data)
        cheatCodeLauncher.launch(intent)
    }
    
    private val cheatCodeLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            result.data?.getByteArrayExtra("modifiedData")?.let {
                decryptedData = it
                Toast.makeText(this, "代码已应用", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun updateButtonStates() {
        val hasData = currentDataFile != null
        val isDecrypted = decryptedData != null
        
        btnDecrypt.isEnabled = hasData && !isDecrypted
        btnEncrypt.isEnabled = isDecrypted
        btnHexEditor.isEnabled = isDecrypted
        btnCheatCode.isEnabled = isDecrypted
    }
}
