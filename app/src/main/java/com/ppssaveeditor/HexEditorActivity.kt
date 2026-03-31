package com.ppssaveeditor

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class HexEditorActivity : AppCompatActivity() {
    
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: HexEditorAdapter
    private lateinit var btnBack: Button
    private lateinit var btnSearch: Button
    private lateinit var btnGoto: Button
    private lateinit var btnModify: Button
    private lateinit var btnSave: Button
    private lateinit var etSearch: EditText
    private lateinit var tvCurrentOffset: TextView
    
    private var data: ByteArray = byteArrayOf()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hex_editor)
        
        data = intent.getByteArrayExtra("data") ?: byteArrayOf()
        
        initViews()
        setupRecyclerView()
    }
    
    private fun initViews() {
        recyclerView = findViewById(R.id.recyclerViewHex)
        btnBack = findViewById(R.id.btnBack)
        btnSearch = findViewById(R.id.btnSearch)
        btnGoto = findViewById(R.id.btnGoto)
        btnModify = findViewById(R.id.btnModify)
        btnSave = findViewById(R.id.btnSave)
        etSearch = findViewById(R.id.etSearch)
        tvCurrentOffset = findViewById(R.id.tvCurrentOffset)
        
        btnBack.setOnClickListener {
            finish()
        }
        
        btnSearch.setOnClickListener {
            searchHex()
        }
        
        btnGoto.setOnClickListener {
            showGotoDialog()
        }
        
        btnModify.setOnClickListener {
            showModifyDialog()
        }
        
        btnSave.setOnClickListener {
            saveAndReturn()
        }
    }
    
    private fun setupRecyclerView() {
        adapter = HexEditorAdapter(data) { offset, value ->
            tvCurrentOffset.text = String.format("偏移: 0x%08X (值: 0x%02X)", offset, value.toInt() and 0xFF)
        }
        
        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = adapter
    }
    
    private fun searchHex() {
        val searchText = etSearch.text.toString().trim()
        if (searchText.isEmpty()) {
            Toast.makeText(this, "请输入搜索值", Toast.LENGTH_SHORT).show()
            return
        }
        
        val offset = adapter.searchHex(searchText)
        if (offset >= 0) {
            val row = offset / 16
            recyclerView.scrollToPosition(row)
            tvCurrentOffset.text = String.format("偏移: 0x%08X", offset)
            Toast.makeText(this, "找到匹配项", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "未找到匹配项", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun showGotoDialog() {
        val editText = EditText(this)
        editText.hint = "输入偏移量 (十六进制，如: 1000)"
        
        AlertDialog.Builder(this)
            .setTitle("跳转到偏移")
            .setView(editText)
            .setPositiveButton("跳转") { _, _ ->
                val input = editText.text.toString().trim()
                try {
                    val offset = input.toInt(16)
                    if (offset in 0 until data.size) {
                        adapter.setSelectedOffset(offset)
                        val row = offset / 16
                        recyclerView.scrollToPosition(row)
                        tvCurrentOffset.text = String.format("偏移: 0x%08X", offset)
                    } else {
                        Toast.makeText(this, "偏移量超出范围", Toast.LENGTH_SHORT).show()
                    }
                } catch (e: NumberFormatException) {
                    Toast.makeText(this, "无效的十六进制值", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    private fun showModifyDialog() {
        val offset = adapter.getSelectedOffset()
        if (offset < 0) {
            Toast.makeText(this, "请先选择一个字节", Toast.LENGTH_SHORT).show()
            return
        }
        
        val layout = layoutInflater.inflate(R.layout.dialog_modify_value, null)
        val etOffset = layout.findViewById<EditText>(R.id.etOffset)
        val etValue = layout.findViewById<EditText>(R.id.etValue)
        val spinnerType = layout.findViewById<android.widget.Spinner>(R.id.spinnerType)
        
        etOffset.setText(String.format("%08X", offset))
        etValue.setText(String.format("%02X", data[offset].toInt() and 0xFF))
        
        // 设置类型选择器
        val types = arrayOf("8位", "16位", "32位")
        val typeAdapter = android.widget.ArrayAdapter(this, android.R.layout.simple_spinner_item, types)
        typeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinnerType.adapter = typeAdapter
        
        AlertDialog.Builder(this)
            .setTitle("修改数值")
            .setView(layout)
            .setPositiveButton("修改") { _, _ ->
                try {
                    val newOffset = etOffset.text.toString().trim().toInt(16)
                    val newValue = etValue.text.toString().trim().toInt(16)
                    val type = spinnerType.selectedItemPosition
                    
                    when (type) {
                        0 -> { // 8位
                            if (newOffset in data.indices) {
                                adapter.modifyByte(newOffset, newValue.toByte())
                                data = adapter.getData()
                            }
                        }
                        1 -> { // 16位
                            adapter.modifyInt32(newOffset, newValue and 0xFFFF)
                            data = adapter.getData()
                        }
                        2 -> { // 32位
                            adapter.modifyInt32(newOffset, newValue)
                            data = adapter.getData()
                        }
                    }
                    
                    Toast.makeText(this, "数值已修改", Toast.LENGTH_SHORT).show()
                } catch (e: Exception) {
                    Toast.makeText(this, "输入无效", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    private fun saveAndReturn() {
        data = adapter.getData()
        
        val resultIntent = Intent()
        resultIntent.putExtra("modifiedData", data)
        setResult(Activity.RESULT_OK, resultIntent)
        finish()
    }
}
