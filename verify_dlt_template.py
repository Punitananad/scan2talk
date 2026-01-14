"""
Verify DLT Template Text - Character by Character
This helps identify invisible character differences
"""

# Current template in code
CODE_TEMPLATE = "Your OTP for Scan2Talk website registration is {otp}. Do not share it with anyone. - Scan2Talk"

print("="*70)
print("🔍 DLT TEMPLATE VERIFICATION")
print("="*70)

print("\n📝 CURRENT TEMPLATE IN CODE:")
print(f'"{CODE_TEMPLATE}"')

print("\n📊 TEMPLATE ANALYSIS:")
print(f"Length: {len(CODE_TEMPLATE)} characters")
print(f"Has {otp}: {'Yes' if '{otp}' in CODE_TEMPLATE else 'No'}")

print("\n🔤 CHARACTER BREAKDOWN:")
for i, char in enumerate(CODE_TEMPLATE):
    if char == ' ':
        print(f"  [{i:3d}] SPACE (ASCII {ord(char)})")
    elif char == '{':
        print(f"  [{i:3d}] '{char}' (ASCII {ord(char)}) ← VARIABLE START")
    elif char == '}':
        print(f"  [{i:3d}] '{char}' (ASCII {ord(char)}) ← VARIABLE END")
    elif char == '.':
        print(f"  [{i:3d}] '{char}' (ASCII {ord(char)}) ← PERIOD")
    elif char == '-':
        print(f"  [{i:3d}] '{char}' (ASCII {ord(char)}) ← DASH")
    else:
        print(f"  [{i:3d}] '{char}' (ASCII {ord(char)})")

print("\n" + "="*70)
print("⚠️  COPY THIS TEMPLATE FROM DLT PORTAL:")
print("="*70)
print("\n1. Login to DLT portal")
print("2. Find template ID: 1707176830112398745")
print("3. Copy the EXACT text (Ctrl+C)")
print("4. Paste below and press Enter:")
print("5. Press Enter again on empty line to finish")
print()

dlt_lines = []
print("Paste DLT template (press Enter twice when done):")
while True:
    line = input()
    if line == "":
        break
    dlt_lines.append(line)

if dlt_lines:
    DLT_TEMPLATE = " ".join(dlt_lines)
    
    print("\n" + "="*70)
    print("🔍 COMPARISON")
    print("="*70)
    
    print(f"\nCode template length: {len(CODE_TEMPLATE)}")
    print(f"DLT template length:  {len(DLT_TEMPLATE)}")
    
    if CODE_TEMPLATE == DLT_TEMPLATE:
        print("\n✅ TEMPLATES MATCH EXACTLY!")
    else:
        print("\n❌ TEMPLATES DO NOT MATCH!")
        
        print("\n🔍 DIFFERENCES:")
        max_len = max(len(CODE_TEMPLATE), len(DLT_TEMPLATE))
        
        for i in range(max_len):
            code_char = CODE_TEMPLATE[i] if i < len(CODE_TEMPLATE) else "END"
            dlt_char = DLT_TEMPLATE[i] if i < len(DLT_TEMPLATE) else "END"
            
            if code_char != dlt_char:
                print(f"  Position {i}:")
                print(f"    Code: '{code_char}' (ASCII {ord(code_char) if code_char != 'END' else 'N/A'})")
                print(f"    DLT:  '{dlt_char}' (ASCII {ord(dlt_char) if dlt_char != 'END' else 'N/A'})")
        
        print("\n📝 CORRECT TEMPLATE TO USE:")
        print(f'MESSAGE_TEMPLATE = "{DLT_TEMPLATE}"')

print("\n" + "="*70)
print("✅ VERIFICATION COMPLETE")
print("="*70)
