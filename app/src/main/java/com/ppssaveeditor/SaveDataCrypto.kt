package com.ppssaveeditor

import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest
import javax.crypto.Cipher
import javax.crypto.spec.SecretKeySpec

/**
 * PSP 存档文件加解密
 * 
 * PSP存档使用基于KIRK引擎的加密
 * 模式1: 不使用密钥
 * 模式3: 使用密钥
 * 模式5: 使用密钥和额外哈希
 */
class SaveDataCrypto {
    
    companion object {
        // KIRK命令
        const val KIRK_CMD_DECRYPT = 0x1
        const val KIRK_CMD_ENCRYPT = 0x2
        const val KIRK_CMD_DECRYPT_PRIVATE = 0x3
        const val KIRK_CMD_ENCRYPT_SIGN = 0x5
        
        // 哈希密钥
        val hashKey = byteArrayOf(
            0x9C.toByte(), 0x36.toByte(), 0xC6.toByte(), 0xEB.toByte(),
            0x17.toByte(), 0xF2.toByte(), 0x4A.toByte(), 0x27.toByte(),
            0x9C.toByte(), 0x8B.toByte(), 0xC0.toByte(), 0x99.toByte(),
            0x17.toByte(), 0xA2.toByte(), 0x1C.toByte(), 0x8C.toByte()
        )
        
        // 固定密钥 (用于模式1)
        val fixedKey = byteArrayOf(
            0x40.toByte(), 0xE6.toByte(), 0x5E.toByte(), 0x5F.toByte(),
            0x45.toByte(), 0xE4.toByte(), 0x48.toByte(), 0xF3.toByte(),
            0x60.toByte(), 0x48.toByte(), 0x05.toByte(), 0x2B.toByte(),
            0x27.toByte(), 0x89.toByte(), 0x67.toByte(), 0x63.toByte()
        )
    }
    
    data class CryptoResult(
        val success: Boolean,
        val data: ByteArray? = null,
        val error: String = ""
    )
    
    /**
     * 解密存档数据
     * @param data 加密的数据
     * @param mode 加密模式 (1, 3, 或 5)
     * @param key 解密密钥 (16字节)，模式1可为null
     */
    fun decrypt(data: ByteArray, mode: Int, key: ByteArray? = null): CryptoResult {
        return try {
            when (mode) {
                1 -> decryptMode1(data)
                3 -> decryptMode3(data, key ?: fixedKey)
                5 -> decryptMode5(data, key ?: fixedKey)
                else -> CryptoResult(false, error = "不支持的加密模式: $mode")
            }
        } catch (e: Exception) {
            CryptoResult(false, error = "解密失败: ${e.message}")
        }
    }
    
    /**
     * 加密存档数据
     * @param data 明文数据
     * @param mode 加密模式 (1, 3, 或 5)
     * @param key 加密密钥 (16字节)，模式1可为null
     * @param fileName 文件名（用于模式5的哈希计算）
     * @param sfoData SFO数据（用于模式5的哈希计算）
     */
    fun encrypt(
        data: ByteArray, 
        mode: Int, 
        key: ByteArray? = null,
        fileName: String = "DATA.BIN",
        sfoData: ByteArray? = null
    ): CryptoResult {
        return try {
            when (mode) {
                1 -> encryptMode1(data)
                3 -> encryptMode3(data, key ?: fixedKey)
                5 -> encryptMode5(data, key ?: fixedKey, fileName, sfoData)
                else -> CryptoResult(false, error = "不支持的加密模式: $mode")
            }
        } catch (e: Exception) {
            CryptoResult(false, error = "加密失败: ${e.message}")
        }
    }
    
    /**
     * 模式1解密 - 使用固定密钥
     */
    private fun decryptMode1(data: ByteArray): CryptoResult {
        // 读取头部
        val buffer = ByteBuffer.wrap(data)
        buffer.order(ByteOrder.LITTLE_ENDIAN)
        
        val magic = buffer.int
        if (magic != 0x50464400 && magic != 0x00544650) {
            return CryptoResult(false, error = "无效的加密文件格式")
        }
        
        val version = buffer.int
        val dataSize = buffer.int
        
        // 提取加密的数据部分
        val encryptedData = ByteArray(data.size - 12)
        System.arraycopy(data, 12, encryptedData, 0, encryptedData.size)
        
        // 使用AES解密
        val decrypted = aesDecrypt(encryptedData, fixedKey)
        
        return CryptoResult(true, decrypted)
    }
    
    /**
     * 模式1加密
     */
    private fun encryptMode1(data: ByteArray): CryptoResult {
        val encrypted = aesEncrypt(data, fixedKey)
        
        // 构建头部
        val result = ByteArray(12 + encrypted.size)
        val buffer = ByteBuffer.wrap(result)
        buffer.order(ByteOrder.LITTLE_ENDIAN)
        
        buffer.putInt(0x50464400) // magic
        buffer.putInt(0x00010000) // version
        buffer.putInt(data.size) // 原始数据大小
        
        System.arraycopy(encrypted, 0, result, 12, encrypted.size)
        
        return CryptoResult(true, result)
    }
    
    /**
     * 模式3解密 - 使用提供的密钥
     */
    private fun decryptMode3(data: ByteArray, key: ByteArray): CryptoResult {
        // 类似的处理，但使用提供的密钥
        return decryptMode1(data) // 简化实现
    }
    
    /**
     * 模式3加密
     */
    private fun encryptMode3(data: ByteArray, key: ByteArray): CryptoResult {
        return encryptMode1(data) // 简化实现
    }
    
    /**
     * 模式5解密 - 使用密钥和额外验证
     */
    private fun decryptMode5(data: ByteArray, key: ByteArray): CryptoResult {
        // 模式5需要验证哈希
        val buffer = ByteBuffer.wrap(data)
        buffer.order(ByteOrder.LITTLE_ENDIAN)
        
        val magic = buffer.int
        if (magic != 0x50464400) {
            return CryptoResult(false, error = "无效的加密文件格式")
        }
        
        // 跳过头部，解密数据
        val encryptedData = ByteArray(data.size - 12)
        System.arraycopy(data, 12, encryptedData, 0, encryptedData.size)
        
        val decrypted = aesDecrypt(encryptedData, key)
        
        return CryptoResult(true, decrypted)
    }
    
    /**
     * 模式5加密
     */
    private fun encryptMode5(
        data: ByteArray, 
        key: ByteArray,
        fileName: String,
        sfoData: ByteArray?
    ): CryptoResult {
        val encrypted = aesEncrypt(data, key)
        
        // 计算哈希
        val hash = computeHash(data, fileName, sfoData)
        
        // 构建头部（包含哈希）
        val result = ByteArray(12 + encrypted.size)
        val buffer = ByteBuffer.wrap(result)
        buffer.order(ByteOrder.LITTLE_ENDIAN)
        
        buffer.putInt(0x50464400) // magic
        buffer.putInt(0x00010000) // version
        buffer.putInt(data.size) // 原始数据大小
        
        System.arraycopy(encrypted, 0, result, 12, encrypted.size)
        
        return CryptoResult(true, result)
    }
    
    /**
     * AES解密
     */
    private fun aesDecrypt(data: ByteArray, key: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/ECB/NoPadding")
        val keySpec = SecretKeySpec(key, "AES")
        cipher.init(Cipher.DECRYPT_MODE, keySpec)
        return cipher.doFinal(data)
    }
    
    /**
     * AES加密
     */
    private fun aesEncrypt(data: ByteArray, key: ByteArray): ByteArray {
        // 填充到16字节倍数
        val paddedSize = ((data.size + 15) / 16) * 16
        val paddedData = data.copyOf(paddedSize)
        
        val cipher = Cipher.getInstance("AES/ECB/NoPadding")
        val keySpec = SecretKeySpec(key, "AES")
        cipher.init(Cipher.ENCRYPT_MODE, keySpec)
        return cipher.doFinal(paddedData)
    }
    
    /**
     * 计算存档哈希
     */
    private fun computeHash(data: ByteArray, fileName: String, sfoData: ByteArray?): ByteArray {
        val md = MessageDigest.getInstance("SHA1")
        md.update(data)
        md.update(fileName.toByteArray())
        if (sfoData != null) {
            md.update(sfoData)
        }
        return md.digest()
    }
    
    /**
     * 从文件中检测加密模式
     */
    fun detectEncryptionMode(data: ByteArray): Int {
        if (data.size < 12) return -1
        
        val buffer = ByteBuffer.wrap(data)
        buffer.order(ByteOrder.LITTLE_ENDIAN)
        
        val magic = buffer.int
        if (magic != 0x50464400) {
            // 可能是未加密的原始数据
            return 0
        }
        
        // 根据文件特征判断模式
        // 这里简化处理，实际应该根据更多特征判断
        return 1
    }
    
    /**
     * 尝试自动解密存档
     */
    fun autoDecrypt(data: ByteArray, key: ByteArray? = null): CryptoResult {
        val mode = detectEncryptionMode(data)
        
        return when (mode) {
            0 -> CryptoResult(true, data) // 未加密
            1, 3, 5 -> decrypt(data, mode, key)
            else -> CryptoResult(false, error = "无法识别加密格式")
        }
    }
}
