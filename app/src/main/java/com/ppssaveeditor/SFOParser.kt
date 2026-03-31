package com.ppssaveeditor

import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * PSP PARAM.SFO 文件解析器
 * SFO文件包含存档的元数据信息
 */
class SFOParser {
    
    data class SFOEntry(
        val key: String,
        val format: Int,
        val length: Int,
        val maxLength: Int,
        val data: ByteArray,
        val stringValue: String = ""
    )
    
    data class SFOData(
        val entries: Map<String, SFOEntry>,
        val gameTitle: String = "",
        val saveTitle: String = "",
        val saveDetail: String = "",
        val titleId: String = ""
    )
    
    companion object {
        const val FORMAT_UTF8 = 0x0204
        const val FORMAT_INT = 0x0404
    }
    
    fun parse(file: File): SFOData? {
        return try {
            val bytes = file.readBytes()
            parse(bytes)
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    fun parse(bytes: ByteArray): SFOData? {
        return try {
            val buffer = ByteBuffer.wrap(bytes)
            buffer.order(ByteOrder.LITTLE_ENDIAN)
            
            // 读取头部
            val magic = buffer.int
            if (magic != 0x46535000) { // "PSP\0"
                println("Invalid SFO magic: ${magic.toString(16)}")
                return null
            }
            
            val version = buffer.int
            val keyTableOffset = buffer.int
            val dataTableOffset = buffer.int
            val entryCount = buffer.int
            
            val entries = mutableMapOf<String, SFOEntry>()
            
            for (i in 0 until entryCount) {
                val keyOffset = buffer.short.toInt()
                val format = buffer.short.toInt()
                val length = buffer.int
                val maxLength = buffer.int
                val dataOffset = buffer.int
                
                // 读取key
                val key = readNullTerminatedString(bytes, keyTableOffset + keyOffset)
                
                // 读取data
                val data = ByteArray(length)
                System.arraycopy(bytes, dataTableOffset + dataOffset, data, 0, length)
                
                val stringValue = if (format == FORMAT_UTF8) {
                    String(data).trimEnd('\u0000')
                } else ""
                
                val entry = SFOEntry(key, format, length, maxLength, data, stringValue)
                entries[key] = entry
            }
            
            SFOData(
                entries = entries,
                gameTitle = entries["TITLE"]?.stringValue ?: "",
                saveTitle = entries["SAVEDATA_TITLE"]?.stringValue ?: "",
                saveDetail = entries["SAVEDATA_DETAIL"]?.stringValue ?: "",
                titleId = entries["TITLE_ID"]?.stringValue ?: ""
            )
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    private fun readNullTerminatedString(bytes: ByteArray, offset: Int): String {
        val sb = StringBuilder()
        var i = offset
        while (i < bytes.size && bytes[i].toInt() != 0) {
            sb.append(bytes[i].toInt().toChar())
            i++
        }
        return sb.toString()
    }
    
    /**
     * 修改SFO中的字符串值
     */
    fun modifyStringEntry(sfoData: SFOData, key: String, newValue: String): SFOData {
        val entry = sfoData.entries[key] ?: return sfoData
        
        if (entry.format != FORMAT_UTF8) return sfoData
        
        val newData = newValue.toByteArray().copyOf(entry.maxLength)
        val newEntry = entry.copy(data = newData, stringValue = newValue)
        
        val newEntries = sfoData.entries.toMutableMap()
        newEntries[key] = newEntry
        
        return sfoData.copy(entries = newEntries)
    }
    
    /**
     * 将SFO数据写回文件
     */
    fun writeSFO(sfoData: SFOData, outputFile: File) {
        // 计算各部分大小
        val entries = sfoData.entries.values.toList()
        
        var keyTableSize = 0
        val keyOffsets = mutableMapOf<String, Int>()
        
        for (entry in entries) {
            keyOffsets[entry.key] = keyTableSize
            keyTableSize += entry.key.length + 1
        }
        
        // 对齐到4字节
        keyTableSize = (keyTableSize + 3) and 0x7FFFFFFC
        
        var dataTableSize = 0
        val dataOffsets = mutableMapOf<String, Int>()
        
        for (entry in entries) {
            dataOffsets[entry.key] = dataTableSize
            dataTableSize += entry.maxLength
        }
        
        // 对齐到4字节
        dataTableSize = (dataTableSize + 3) and 0x7FFFFFFC
        
        val headerSize = 20
        val indexSize = entries.size * 16
        val totalSize = headerSize + indexSize + keyTableSize + dataTableSize
        
        val buffer = ByteBuffer.allocate(totalSize)
        buffer.order(ByteOrder.LITTLE_ENDIAN)
        
        // 写入头部
        buffer.putInt(0x46535000) // magic
        buffer.putInt(0x00010100) // version
        buffer.putInt(headerSize + indexSize) // key table offset
        buffer.putInt(headerSize + indexSize + keyTableSize) // data table offset
        buffer.putInt(entries.size) // entry count
        
        // 写入索引表
        for (entry in entries) {
            buffer.putShort(keyOffsets[entry.key]!!.toShort())
            buffer.putShort(entry.format.toShort())
            buffer.putInt(entry.length)
            buffer.putInt(entry.maxLength)
            buffer.putInt(dataOffsets[entry.key]!!)
        }
        
        // 写入key表
        for (entry in entries) {
            for (c in entry.key) {
                buffer.put(c.code.toByte())
            }
            buffer.put(0)
        }
        
        // 填充对齐
        while (buffer.position() < headerSize + indexSize + keyTableSize) {
            buffer.put(0)
        }
        
        // 写入data表
        for (entry in entries) {
            buffer.put(entry.data.copyOf(entry.maxLength))
        }
        
        // 填充对齐
        while (buffer.position() < totalSize) {
            buffer.put(0)
        }
        
        outputFile.writeBytes(buffer.array())
    }
}
