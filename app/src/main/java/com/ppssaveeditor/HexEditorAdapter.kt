package com.ppssaveeditor

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

/**
 * 十六进制编辑器RecyclerView适配器
 */
class HexEditorAdapter(
    private var data: ByteArray,
    private val onByteClick: (offset: Int, value: Byte) -> Unit
) : RecyclerView.Adapter<HexEditorAdapter.HexViewHolder>() {
    
    private var selectedOffset = -1
    private val bytesPerRow = 16
    
    inner class HexViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvOffset: TextView = itemView.findViewById(R.id.tvOffset)
        val hexContainer: LinearLayout = itemView.findViewById(R.id.hexContainer)
        val tvAscii: TextView = itemView.findViewById(R.id.tvAscii)
    }
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): HexViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_hex_row, parent, false)
        return HexViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: HexViewHolder, position: Int) {
        val offset = position * bytesPerRow
        
        // 设置偏移量显示
        holder.tvOffset.text = String.format("%08X", offset)
        
        // 清空并重建hex容器
        holder.hexContainer.removeAllViews()
        
        val asciiBuilder = StringBuilder()
        
        for (i in 0 until bytesPerRow) {
            val byteOffset = offset + i
            
            if (byteOffset < data.size) {
                val byteValue = data[byteOffset]
                
                // 创建hex文本视图
                val hexText = TextView(holder.itemView.context)
                hexText.text = String.format("%02X ", byteValue.toInt() and 0xFF)
                hexText.setTextColor(Color.parseColor("#00FF00"))
                hexText.textSize = 12f
                hexText.setPadding(2, 0, 2, 0)
                hexText.typeface = android.graphics.Typeface.MONOSPACE
                
                // 高亮选中的字节
                if (byteOffset == selectedOffset) {
                    hexText.setBackgroundColor(Color.parseColor("#444444"))
                }
                
                // 点击事件
                hexText.setOnClickListener {
                    selectedOffset = byteOffset
                    notifyDataSetChanged()
                    onByteClick(byteOffset, byteValue)
                }
                
                holder.hexContainer.addView(hexText)
                
                // 构建ASCII表示
                val charValue = byteValue.toInt() and 0xFF
                if (charValue in 32..126) {
                    asciiBuilder.append(charValue.toChar())
                } else {
                    asciiBuilder.append('.')
                }
            } else {
                // 超出数据范围，显示空格
                val hexText = TextView(holder.itemView.context)
                hexText.text = "   "
                hexText.textSize = 12f
                holder.hexContainer.addView(hexText)
                asciiBuilder.append(' ')
            }
        }
        
        holder.tvAscii.text = asciiBuilder.toString()
    }
    
    override fun getItemCount(): Int {
        return (data.size + bytesPerRow - 1) / bytesPerRow
    }
    
    fun updateData(newData: ByteArray) {
        data = newData
        notifyDataSetChanged()
    }
    
    fun getData(): ByteArray = data
    
    fun setSelectedOffset(offset: Int) {
        selectedOffset = offset
        notifyDataSetChanged()
    }
    
    fun getSelectedOffset(): Int = selectedOffset
    
    /**
     * 修改指定偏移处的字节值
     */
    fun modifyByte(offset: Int, newValue: Byte) {
        if (offset in data.indices) {
            data[offset] = newValue
            notifyDataSetChanged()
        }
    }
    
    /**
     * 修改指定偏移处的32位整数（小端序）
     */
    fun modifyInt32(offset: Int, value: Int) {
        if (offset + 3 < data.size) {
            data[offset] = (value and 0xFF).toByte()
            data[offset + 1] = ((value shr 8) and 0xFF).toByte()
            data[offset + 2] = ((value shr 16) and 0xFF).toByte()
            data[offset + 3] = ((value shr 24) and 0xFF).toByte()
            notifyDataSetChanged()
        }
    }
    
    /**
     * 搜索十六进制值
     */
    fun searchHex(searchValue: String): Int {
        val cleanSearch = searchValue.replace(" ", "")
        if (cleanSearch.length % 2 != 0) return -1
        
        val searchBytes = mutableListOf<Byte>()
        for (i in cleanSearch.indices step 2) {
            val byteStr = cleanSearch.substring(i, i + 2)
            try {
                searchBytes.add(byteStr.toInt(16).toByte())
            } catch (e: NumberFormatException) {
                return -1
            }
        }
        
        val searchArray = searchBytes.toByteArray()
        
        for (i in 0..data.size - searchArray.size) {
            var match = true
            for (j in searchArray.indices) {
                if (data[i + j] != searchArray[j]) {
                    match = false
                    break
                }
            }
            if (match) {
                selectedOffset = i
                notifyDataSetChanged()
                return i
            }
        }
        
        return -1
    }
}
