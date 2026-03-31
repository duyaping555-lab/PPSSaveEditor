package com.ppssaveeditor

/**
 * CWCheat 补丁代码应用器
 * 
 * CWCheat代码格式:
 * _L 0x2XXXXXXX 0xYYYYYYYY - 32位写入
 * _L 0x1XXXXXXX 0x0000YYYY - 16位写入
 * _L 0x0XXXXXXX 0x000000YY - 8位写入
 */
class CheatCodeApplier {
    
    data class CheatResult(
        val success: Boolean,
        val message: String,
        val modifiedOffsets: List<Int> = emptyList()
    )
    
    data class CheatCode(
        val address: Int,
        val value: Int,
        val type: Int // 0=8bit, 1=16bit, 2=32bit
    )
    
    /**
     * 解析CWCheat代码行
     */
    fun parseCodeLine(line: String): CheatCode? {
        val trimmed = line.trim()
        
        // 支持多种格式:
        // _L 0x2XXXXXXX 0xYYYYYYYY
        // _L 0x1XXXXXXX 0x0000YYYY
        // _L 0x0XXXXXXX 0x000000YY
        
        if (!trimmed.startsWith("_L")) return null
        
        val parts = trimmed.split(Regex("\\s+"))
        if (parts.size < 3) return null
        
        return try {
            val addressStr = parts[1]
            val valueStr = parts[2]
            
            // 解析地址
            val address = if (addressStr.startsWith("0x") || addressStr.startsWith("0X")) {
                addressStr.substring(2).toInt(16)
            } else {
                addressStr.toInt(16)
            }
            
            // 解析值
            val value = if (valueStr.startsWith("0x") || valueStr.startsWith("0X")) {
                valueStr.substring(2).toInt(16)
            } else {
                valueStr.toInt(16)
            }
            
            // 根据地址前缀确定类型
            val type = when {
                addressStr.startsWith("0x0") || addressStr.startsWith("0X0") -> 0 // 8bit
                addressStr.startsWith("0x1") || addressStr.startsWith("0X1") -> 1 // 16bit
                addressStr.startsWith("0x2") || addressStr.startsWith("0X2") -> 2 // 32bit
                else -> 2 // 默认为32bit
            }
            
            CheatCode(address and 0x0FFFFFFF, value, type)
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * 应用多个CWCheat代码
     */
    fun applyCodes(data: ByteArray, codeLines: List<String>): CheatResult {
        val modifiedOffsets = mutableListOf<Int>()
        val failedCodes = mutableListOf<String>()
        
        for (line in codeLines) {
            val code = parseCodeLine(line)
            if (code != null) {
                val result = applyCode(data, code)
                if (result) {
                    modifiedOffsets.add(code.address)
                } else {
                    failedCodes.add(line)
                }
            } else if (line.trim().isNotEmpty() && !line.trim().startsWith("//") && !line.trim().startsWith(";")) {
                // 非空行且不是注释，但解析失败
                failedCodes.add(line)
            }
        }
        
        return CheatResult(
            success = failedCodes.isEmpty() || modifiedOffsets.isNotEmpty(),
            message = if (failedCodes.isEmpty()) {
                "成功应用 ${modifiedOffsets.size} 个代码"
            } else {
                "成功应用 ${modifiedOffsets.size} 个代码，失败 ${failedCodes.size} 个"
            },
            modifiedOffsets = modifiedOffsets
        )
    }
    
    /**
     * 应用单个CheatCode
     */
    private fun applyCode(data: ByteArray, code: CheatCode): Boolean {
        return when (code.type) {
            0 -> write8(data, code.address, code.value)
            1 -> write16(data, code.address, code.value)
            2 -> write32(data, code.address, code.value)
            else -> false
        }
    }
    
    /**
     * 写入8位值
     */
    private fun write8(data: ByteArray, address: Int, value: Int): Boolean {
        return if (address in data.indices) {
            data[address] = (value and 0xFF).toByte()
            true
        } else {
            false
        }
    }
    
    /**
     * 写入16位值（小端序）
     */
    private fun write16(data: ByteArray, address: Int, value: Int): Boolean {
        return if (address + 1 < data.size) {
            data[address] = (value and 0xFF).toByte()
            data[address + 1] = ((value shr 8) and 0xFF).toByte()
            true
        } else {
            false
        }
    }
    
    /**
     * 写入32位值（小端序）
     */
    private fun write32(data: ByteArray, address: Int, value: Int): Boolean {
        return if (address + 3 < data.size) {
            data[address] = (value and 0xFF).toByte()
            data[address + 1] = ((value shr 8) and 0xFF).toByte()
            data[address + 2] = ((value shr 16) and 0xFF).toByte()
            data[address + 3] = ((value shr 24) and 0xFF).toByte()
            true
        } else {
            false
        }
    }
    
    /**
     * 从文本解析多个代码
     */
    fun parseCodesFromText(text: String): List<CheatCode> {
        val codes = mutableListOf<CheatCode>()
        val lines = text.lines()
        
        for (line in lines) {
            parseCodeLine(line)?.let { codes.add(it) }
        }
        
        return codes
    }
    
    /**
     * 生成CWCheat代码文本
     */
    fun generateCodeText(codes: List<CheatCode>, description: String = ""): String {
        val sb = StringBuilder()
        
        if (description.isNotEmpty()) {
            sb.append("// $description\n")
        }
        
        for (code in codes) {
            val prefix = when (code.type) {
                0 -> "0x0"
                1 -> "0x1"
                else -> "0x2"
            }
            sb.append("_L ${prefix}%07X 0x%08X\n".format(code.address, code.value))
        }
        
        return sb.toString()
    }
    
    /**
     * 创建金钱修改代码（通用格式，需要根据具体游戏调整地址）
     */
    fun createMoneyCheat(address: Int, amount: Int): String {
        return "_L 0x2%07X 0x%08X".format(address, amount)
    }
    
    /**
     * 创建HP修改代码
     */
    fun createHPCheat(address: Int, hp: Int): String {
        return "_L 0x1%07X 0x%04X".format(address, hp)
    }
    
    /**
     * 创建物品数量修改代码
     */
    fun createItemCheat(address: Int, count: Int): String {
        return "_L 0x0%07X 0x%02X".format(address, count)
    }
}
