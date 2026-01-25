# Distributor Revoke System (Soft Delete)

## Overview
Distributors can now be revoked (soft deleted) instead of permanently removed. Revoked distributors are marked as "Revoked" and can be restored later if needed.

## Features

### 1. Soft Delete (Revoke)
✅ Mark distributor as revoked instead of deleting  
✅ Add reason for revocation (optional)  
✅ Track who revoked and when  
✅ Distributor data is preserved  
✅ Can be undone/restored later

### 2. Revoked Status Display
✅ Shows "❌ Revoked" badge in status column  
✅ Displays revoke information:
- Who revoked
- When revoked
- Reason (if provided)

### 3. Restore Functionality
✅ "Restore Distributor" button for revoked distributors  
✅ One-click restore with confirmation  
✅ Clears all revoke data  
✅ Distributor returns to active status

### 4. Filtering
✅ Filter by status:
- Active (all non-revoked)
- Pending Verification
- Verified
- Revoked
- All Status

### 5. Statistics
✅ New "Revoked" count in stats cards  
✅ Shows total revoked distributors

## Database Changes

### New Fields in `User` Model:

```python
distributor_revoked = BooleanField(default=False)
# Has distributor status been revoked?

distributor_revoked_at = DateTimeField(null=True, blank=True)
# When was distributor status revoked?

distributor_revoked_by = ForeignKey(User)
# Admin who revoked distributor status

distributor_revoke_reason = TextField(blank=True)
# Reason for revoking distributor status
```

## How It Works

### Revoke Flow:

```
Step 1: Admin Views Distributor
├─ Go to Manage Distributors page
├─ Find distributor to revoke
└─ Click "Revoke" button

Step 2: Enter Revoke Reason
├─ Modal opens
├─ Enter reason (optional)
└─ Click "Revoke Distributor"

Step 3: Distributor Revoked
├─ distributor_revoked = True
├─ distributor_revoked_at = now()
├─ distributor_revoked_by = admin user
├─ distributor_revoke_reason = reason
└─ Status badge shows "❌ Revoked"

Step 4: Revoked Distributor Display
├─ Shows revoke information
├─ Shows "Restore Distributor" button
└─ No other actions available
```

### Restore Flow:

```
Step 1: Admin Views Revoked Distributor
├─ Filter by "Revoked" status
├─ Find distributor to restore
└─ Click "↻ Restore Distributor"

Step 2: Confirm Restore
├─ Confirmation dialog
└─ Click "OK"

Step 3: Distributor Restored
├─ distributor_revoked = False
├─ distributor_revoked_at = None
├─ distributor_revoked_by = None
├─ distributor_revoke_reason = ''
└─ Returns to active status
```

## UI Changes

### Before (Old System):
- Revoke button permanently removed distributor
- No way to undo
- Distributor data lost

### After (New System):
- Revoke button marks as revoked
- Shows revoke information
- Restore button available
- All data preserved

## Status Badge Colors

| Status | Badge | Color |
|--------|-------|-------|
| Pending | ⏳ Pending | Yellow |
| Verified | ✓ Verified | Green |
| Revoked | ❌ Revoked | Red |

## Admin Interface

### Distributor List View

**Active Distributor:**
```
Name: John Doe
Phone: 9876543210
Status: ✓ Verified
Actions: [Edit Details] [Reset Password] [Revoke]
```

**Revoked Distributor:**
```
Name: John Doe
Phone: 9876543210
Status: ❌ Revoked

Revoked by Admin
Jan 25, 2026
Reason: Fraudulent activity

Actions: [↻ Restore Distributor]
```

### Filter Options

```
Status Filter:
- Active (All Non-Revoked) ← Default
- Pending Verification
- Verified
- Revoked
- All Status
```

### Statistics Cards

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│  Total   │  Active  │ Pending  │ Revoked  │ Total QR │Activated │
│    10    │    8     │    2     │    2     │   100    │    50    │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

## API Endpoints

### Revoke Distributor
```http
POST /accounts/admin/distributors/<user_id>/revoke/
Content-Type: application/x-www-form-urlencoded

reason=Fraudulent activity
```

### Restore Distributor
```http
POST /accounts/admin/distributors/<user_id>/unrevoke/
```

## Use Cases

### Use Case 1: Revoke for Fraud
```
Admin discovers fraudulent activity

1. Go to Manage Distributors
2. Find the distributor
3. Click "Revoke"
4. Enter reason: "Fraudulent activity detected"
5. Confirm revocation
6. Distributor marked as revoked
7. Can investigate and restore if mistake
```

### Use Case 2: Temporary Suspension
```
Admin needs to temporarily suspend distributor

1. Revoke distributor with reason: "Temporary suspension - under review"
2. Distributor cannot login or earn commissions
3. After review, restore distributor
4. Distributor can resume operations
```

### Use Case 3: Accidental Revoke
```
Admin revokes wrong distributor by mistake

1. Go to Manage Distributors
2. Filter by "Revoked"
3. Find the distributor
4. Click "Restore Distributor"
5. Confirm restore
6. Distributor back to active status
```

### Use Case 4: View Revoked History
```
Admin wants to see all revoked distributors

1. Go to Manage Distributors
2. Filter by "Revoked"
3. See list of all revoked distributors
4. View revoke reasons and dates
5. Restore if needed
```

## Files Modified

### Backend:
1. **`apps/accounts/models.py`** - Modified
   - Added 4 new fields to User model

2. **`apps/accounts/admin_views.py`** - Modified
   - Updated `revoke_distributor()` to mark as revoked
   - Added `unrevoke_distributor()` to restore
   - Updated `manage_distributors()` to filter revoked

3. **`apps/accounts/urls.py`** - Modified
   - Added unrevoke route

### Frontend:
4. **`templates/admin/manage_distributors.html`** - Modified
   - Updated status badge to show revoked
   - Added revoke information display
   - Added restore button
   - Added revoke modal with reason field
   - Updated filter options
   - Updated statistics cards
   - Added JavaScript functions

### Database:
5. **`apps/accounts/migrations/0010_add_distributor_revoke_fields.py`** - Created
   - Migration for new fields

## Benefits

✅ **Reversible**: Can undo revocation if needed  
✅ **Audit Trail**: Complete record of who revoked and why  
✅ **Data Preservation**: All distributor data is kept  
✅ **Flexible**: Can revoke temporarily or permanently  
✅ **Transparent**: Clear display of revoke status  
✅ **Safe**: No accidental data loss

## Important Notes

1. **Revoked distributors cannot login** - They are effectively suspended
2. **Commissions are preserved** - Past earnings are not affected
3. **QR codes remain** - QR codes assigned to revoked distributors are not deleted
4. **Can be restored anytime** - No time limit on restoration
5. **Reason is optional** - But recommended for record keeping

## Testing Checklist

- [x] Migration runs successfully
- [x] Revoke button shows modal
- [x] Revoke reason is saved
- [x] Revoked status displays correctly
- [x] Revoke information shows who/when/why
- [x] Restore button appears for revoked distributors
- [x] Restore works correctly
- [x] Filter by revoked status works
- [x] Statistics show revoked count
- [x] Revoked distributors cannot login

## Future Enhancements

1. **Email Notifications**
   - Notify distributor when revoked
   - Notify when restored

2. **Revoke History**
   - Track multiple revoke/restore cycles
   - Show history of revocations

3. **Auto-revoke**
   - Automatically revoke after X failed payments
   - Auto-revoke for inactivity

4. **Bulk Revoke**
   - Select multiple distributors
   - Revoke in bulk

---

**Date**: January 25, 2026  
**Status**: ✅ Complete  
**Version**: 1.0
