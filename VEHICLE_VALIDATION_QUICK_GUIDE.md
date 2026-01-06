# Vehicle Number Validation - Quick Guide

## The Rule (Simple)

```
ONE VEHICLE NUMBER = ONE QR CODE
```

## Examples

### ✅ ALLOWED

**Example 1: First Registration**
```
User: John
Vehicle: DL-01-AB-1234
QR: ZQ0VCCEZ
Status: ✓ Activated
```

**Example 2: Same User, Different Vehicles**
```
User: John
Vehicle 1: DL-01-AB-1234 → QR: ZQ0VCCEZ ✓
Vehicle 2: DL-02-CD-5678 → QR: G9ZXLBC3 ✓
Status: Both allowed (different vehicles)
```

**Example 3: Different Users, Different Vehicles**
```
User 1: John → Vehicle: DL-01-AB-1234 ✓
User 2: Sarah → Vehicle: HR-12-XY-9876 ✓
Status: Both allowed (different vehicles)
```

### ❌ NOT ALLOWED

**Example 1: Duplicate Vehicle Number**
```
User: John
Vehicle: DL-01-AB-1234 → QR: ZQ0VCCEZ ✓ (First)
Vehicle: DL-01-AB-1234 → QR: G9ZXLBC3 ✗ (Rejected)
Reason: Vehicle already registered
```

**Example 2: Different User, Same Vehicle**
```
User 1: John → Vehicle: DL-01-AB-1234 ✓ (First)
User 2: Sarah → Vehicle: DL-01-AB-1234 ✗ (Rejected)
Reason: Vehicle already registered by John
```

**Example 3: Case Variations (Still Duplicate)**
```
First: "dl01ab1234" ✓
Second: "DL01AB1234" ✗ (Rejected - same number)
Second: "DL-01-AB-1234" ✗ (Rejected - same number)
Reason: Case insensitive check
```

## What Happens

### When Activating QR

```
Step 1: Enter Phone → ✓
Step 2: Verify OTP → ✓
Step 3: Enter Details
  ↓
  Name: John Doe
  Vehicle Type: Car
  Vehicle Number: DL-01-AB-1234
  ↓
  System checks: Is this number already used?
  ↓
  ┌─────────────────────────────────┐
  │ YES → Show Error Page           │
  │ NO → Activate QR Successfully   │
  └─────────────────────────────────┘
```

### Error Page Shows

```
┌─────────────────────────────────────────┐
│ ⚠️ Vehicle Already Registered           │
├─────────────────────────────────────────┤
│ Vehicle number DL-01-AB-1234 is         │
│ already registered with another QR code │
│                                         │
│ What can you do?                        │
│ 1. Use different vehicle number         │
│ 2. Check if you already registered      │
│ 3. Contact support                      │
│                                         │
│ [Try Different Number] [Go Home]        │
└─────────────────────────────────────────┘
```

## Your Current Data

You have 3 QRs with the same vehicle number:
```
Vehicle: HR12AM7522
QR 1: fa9a1d9c... (No name)
QR 2: 3449b60f... (punit Anand again)
QR 3: bdd465a1... (punit Anand)
```

**Going forward:** New activations with "HR12AM7522" will be rejected.

**Existing QRs:** Will continue to work (no changes to existing data).

## Testing

### Test 1: Try Duplicate
1. Go to: http://localhost:8000/gateways/activate/[QR-CODE]/
2. Complete steps 1 & 2
3. Enter vehicle number: **HR12AM7522**
4. Submit
5. **Result:** Error page shown ✗

### Test 2: Try New Vehicle
1. Go to: http://localhost:8000/gateways/activate/[QR-CODE]/
2. Complete steps 1 & 2
3. Enter vehicle number: **NEW-123-XYZ**
4. Submit
5. **Result:** QR activated ✓

## Key Points

1. **One vehicle = One QR** (strict rule)
2. **Case insensitive** (DL01 = dl01 = DL-01)
3. **Active gateways only** (deactivated don't count)
4. **Clear error messages** (user knows why it failed)
5. **Fast validation** (database indexed)

## Summary

✅ Prevents duplicate vehicle registrations
✅ Maintains data integrity
✅ Clear user feedback
✅ Fast performance
✅ Easy to understand

**Bottom line:** Each vehicle number can only be used once!
