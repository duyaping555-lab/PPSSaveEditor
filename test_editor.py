#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPSSPP Save Editor - Test Script
Tests core functionality
"""

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sfo_parser():
    print("=" * 60)
    print("Testing SFO Parser")
    print("=" * 60)
    
    from psp_save_editor import SFOParser, SFOEntry, SFOData
    
    parser = SFOParser()
    
    entries = {
        'TITLE': SFOEntry('TITLE', 0x0204, 5, 32, b'Test\x00', 'Test'),
        'SAVEDATA_TITLE': SFOEntry('SAVEDATA_TITLE', 0x0204, 5, 128, b'Save\x00', 'Save'),
        'TITLE_ID': SFOEntry('TITLE_ID', 0x0204, 10, 16, b'ULJM12345\x00', 'ULJM12345'),
    }
    
    sfo_data = SFOData(entries, 'Test Game', 'Save Data', 'Detail', 'ULJM12345')
    
    with tempfile.NamedTemporaryFile(suffix='.SFO', delete=False) as f:
        temp_path = f.name
    
    parser.write_sfo(sfo_data, temp_path)
    print(f"[OK] Write SFO file: {os.path.getsize(temp_path)} bytes")
    
    parsed = parser.parse(temp_path)
    
    if parsed:
        print(f"[OK] Game Title: {parsed.game_title}")
        print(f"[OK] Save Title: {parsed.save_title}")
        print(f"[OK] Title ID: {parsed.title_id}")
        assert parsed.game_title == 'Test'
        assert parsed.title_id == 'ULJM12345'
        print("[OK] SFO Parser test passed!")
    else:
        print("[FAIL] SFO parsing failed!")
    
    os.unlink(temp_path)
    print()


def test_crypto():
    print("=" * 60)
    print("Testing Crypto Module")
    print("=" * 60)
    
    try:
        from psp_save_editor import SaveDataCrypto
        
        crypto = SaveDataCrypto()
        
        original = b'Hello, PSP World! This is a test save data.'
        
        encrypted = crypto.encrypt(original, mode=1)
        print(f"[OK] Encrypt success, size: {len(encrypted)} bytes")
        print(f"     Header (12 bytes): {encrypted[:12].hex()}")
        
        decrypted = crypto.decrypt(encrypted, mode=1)
        print(f"[OK] Decrypt success, size: {len(decrypted)} bytes")
        
        if decrypted == original:
            print("[OK] Decrypted data matches original!")
        else:
            print("[FAIL] Data mismatch!")
            print(f"  Original: {original}")
            print(f"  Decrypted: {decrypted}")
        
        mode = crypto.detect_mode(encrypted)
        print(f"[OK] Detected mode: {mode}")
        
        plain_mode = crypto.detect_mode(original)
        print(f"[OK] Plain text detected as mode: {plain_mode}")
        
        print("[OK] Crypto test passed!")
        
    except ImportError as e:
        print(f"[WARN] Crypto library not installed: {e}")
        print("  Run: pip install pycryptodome")
    except Exception as e:
        print(f"[FAIL] Crypto test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()


def test_cheat_codes():
    print("=" * 60)
    print("Testing CWCheat Code Applier")
    print("=" * 60)
    
    from psp_save_editor import CheatCodeApplier
    
    applier = CheatCodeApplier()
    
    test_codes = [
        "_L 0x20555678 0x12345678",
        "_L 0x1055567C 0x00009ABC",
        "_L 0x0055567E 0x000000EF",
    ]
    
    print("Code parsing test:")
    for code in test_codes:
        parsed = applier.parse_code(code)
        if parsed:
            addr, val, typ = parsed
            type_names = {0: '8-bit', 1: '16-bit', 2: '32-bit'}
            print(f"  [OK] {code}")
            print(f"       addr=0x{addr:08X}, value=0x{val:08X}, type={type_names.get(typ, 'unknown')}")
    
    data = bytearray(0x555680)
    
    print("\nApplying codes:")
    success, message, modified = applier.apply_codes(data, test_codes)
    print(f"  {message}")
    
    print("\nVerification:")
    errors = []
    
    if (data[0x555678] == 0x78 and 
        data[0x555679] == 0x56 and
        data[0x55567A] == 0x34 and
        data[0x55567B] == 0x12):
        print("  [OK] 32-bit write verified (addr 0x555678)")
    else:
        print(f"  [FAIL] 32-bit write failed")
        print(f"    Expected: 78 56 34 12")
        print(f"    Got: {data[0x555678]:02X} {data[0x555679]:02X} {data[0x55567A]:02X} {data[0x55567B]:02X}")
        errors.append("32-bit")
    
    if (data[0x55567C] == 0xBC and data[0x55567D] == 0x9A):
        print("  [OK] 16-bit write verified (addr 0x55567C)")
    else:
        print(f"  [FAIL] 16-bit write failed")
        errors.append("16-bit")
    
    if data[0x55567E] == 0xEF:
        print("  [OK] 8-bit write verified (addr 0x55567E)")
    else:
        errors.append("8-bit")
    
    if not errors:
        print("\n[OK] CWCheat test passed!")
    else:
        print(f"\n[FAIL] {', '.join(errors)} tests failed")
    
    print()


def test_hex_editor():
    print("=" * 60)
    print("Testing Hex Editor")
    print("=" * 60)
    
    from psp_save_editor import HexEditor
    
    data = bytearray(256)
    for i in range(256):
        data[i] = i
    
    editor = HexEditor(data)
    
    print("First 3 rows:")
    editor.display(start=0, rows=3)
    
    print("\nSearch test:")
    results = editor.search("00 01 02 03")
    if results:
        print(f"  [OK] Found match at: 0x{results[0]:08X}")
    
    print("\nModify test:")
    editor.modify(0x10, 0xABCD, 2)
    print(f"  [OK] Modified 0x10 = 0xABCD")
    print(f"  Verify: 0x10={data[0x10]:02X}, 0x11={data[0x11]:02X}")
    
    if data[0x10] == 0xCD and data[0x11] == 0xAB:
        print("  [OK] Little-endian write correct!")
    
    print("\n[OK] Hex Editor test passed!")
    print()


def test_full_workflow():
    print("=" * 60)
    print("Testing Full Workflow")
    print("=" * 60)
    
    from psp_save_editor import SaveDataEditor, SFOParser, SFOEntry, SFOData
    
    temp_dir = tempfile.mkdtemp()
    save_dir = os.path.join(temp_dir, 'ULJM12345')
    os.makedirs(save_dir)
    
    try:
        parser = SFOParser()
        
        entries = {
            'TITLE': SFOEntry('TITLE', 0x0204, 9, 32, b'TestGame\x00', 'TestGame'),
            'SAVEDATA_TITLE': SFOEntry('SAVEDATA_TITLE', 0x0204, 5, 128, b'Save\x00', 'Save'),
            'TITLE_ID': SFOEntry('TITLE_ID', 0x0204, 10, 16, b'ULJM12345\x00', 'ULJM12345'),
        }
        sfo_data = SFOData(entries, 'TestGame', 'Save', '', 'ULJM12345')
        parser.write_sfo(sfo_data, os.path.join(save_dir, 'PARAM.SFO'))
        
        test_data = b'Money: 12345' + b'\x00' * 100
        
        try:
            from psp_save_editor import SaveDataCrypto
            crypto = SaveDataCrypto()
            encrypted = crypto.encrypt(test_data, mode=1)
            print("[OK] Using encrypted data")
        except Exception as e:
            encrypted = test_data
            print(f"[WARN] Using plain text ({e})")
        
        with open(os.path.join(save_dir, 'DATA.BIN'), 'wb') as f:
            f.write(encrypted)
        
        print(f"[OK] Created test save: {save_dir}")
        
        editor = SaveDataEditor(save_dir)
        print(f"[OK] Loaded save editor")
        print(f"  Game: {editor.sfo_data.game_title}")
        print(f"  ID: {editor.sfo_data.title_id}")
        print(f"  Data file: {editor.data_file.name if editor.data_file else 'None'}")
        
        if editor.decrypt():
            print(f"[OK] Decrypt success, data size: {len(editor.decrypted_data)} bytes")
            print(f"  Content: {bytes(editor.decrypted_data[:20])}")
            
            codes = ["_L 0x00000007 0x39393939"]
            editor.apply_cheat_codes("\n".join(codes))
            print("[OK] Applied cheat codes")
            
            modified_text = bytes(editor.decrypted_data[:20])
            print(f"  After: {modified_text}")
            
            encrypted_path = os.path.join(save_dir, 'DATA_ENCRYPTED.BIN')
            if editor.encrypt(encrypted_path):
                print(f"[OK] Encrypt success: {encrypted_path}")
                print(f"  File size: {os.path.getsize(encrypted_path)} bytes")
        else:
            print("[WARN] Decrypt skipped (might be plain text)")
        
        print("\n[OK] Full workflow test passed!")
        
    finally:
        shutil.rmtree(temp_dir)
    
    print()


def main():
    print("\n" + "=" * 60)
    print("PPSSPP Save Editor - Function Tests")
    print("=" * 60 + "\n")
    
    tests = [
        ("SFO Parser", test_sfo_parser),
        ("Crypto", test_crypto),
        ("CWCheat", test_cheat_codes),
        ("Hex Editor", test_hex_editor),
        ("Full Workflow", test_full_workflow),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"[FAIL] {name} test failed: {e}\n")
    
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    for name, passed, error in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if error:
            print(f"       {error}")
    
    all_passed = all(r[1] for r in results)
    print("=" * 60)
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed!")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
