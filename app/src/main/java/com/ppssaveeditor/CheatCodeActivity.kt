package com.ppssaveeditor

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity

class CheatCodeActivity : AppCompatActivity() {
    
    private lateinit var etCheatCodes: EditText
    private lateinit var btnBack: Button
    private lateinit var btnApply: Button
    
    private var data: ByteArray = byteArrayOf()
    private val cheatApplier = CheatCodeApplier()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_cheat_code)
        
        data = intent.getByteArrayExtra("data") ?: byteArrayOf()
        
        initViews()
    }
    
    private fun initViews() {
        etCheatCodes = findViewById(R.id.etCheatCodes)
        btnBack = findViewById(R.id.btnBack)
        btnApply = findViewById(R.id.btnApply)
        
        btnBack.setOnClickListener {
            finish()
        }
        
        btnApply.setOnClickListener {
            applyCheatCodes()
        }
    }
    
    private fun applyCheatCodes() {
        val codeText = etCheatCodes.text.toString()
        
        if (codeText.trim().isEmpty()) {
            Toast.makeText(this, "请输入代码", Toast.LENGTH_SHORT).show()
            return
        }
        
        val lines = codeText.lines()
        val result = cheatApplier.applyCodes(data, lines)
        
        if (result.success) {
            AlertDialog.Builder(this)
                .setTitle("应用成功")
                .setMessage("${result.message}\n\n是否保存修改?")
                .setPositiveButton("保存") { _, _ ->
                    saveAndReturn()
                }
                .setNegativeButton("继续编辑") { _, _ ->
                    // 不关闭，继续编辑
                }
                .show()
        } else {
            Toast.makeText(this, result.message, Toast.LENGTH_LONG).show()
        }
    }
    
    private fun saveAndReturn() {
        val resultIntent = Intent()
        resultIntent.putExtra("modifiedData", data)
        setResult(Activity.RESULT_OK, resultIntent)
        finish()
    }
}
