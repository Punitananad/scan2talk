# QR Code Activation Rules

## Core Principle
**Activation is a one-time setup, not a recurring state check.**

Once a QR code is activated, it becomes a permanent public contact point. No repeated activation, no owner-side control prompts, no confusion.

---

## Rules (Strict)

### 1. Single Activation Only
- A QR code can be activated **only once** by the owner
- After first activation, the system permanently marks it as `ACTIVE`
- One QR code per vehicle number (enforced at activation)

### 2. No "Already Activated" Message
- **Never** show messages like "This QR code is already activated by you"
- This message is not needed, not useful, and creates confusion
- **Removed completely** from UI and logic

### 3. Post-Activation Behavior
Once activated:
- The QR code becomes **public-facing**
- It is **no longer owner-controlled**
- It exists **only for users who scan it**

### 4. Scan Flow (After Activation)
Any scan (2nd, 3rd, 100th time):
- **Must directly redirect** to the owner's contact page
- No checks
- No activation validation
- No owner dashboard logic
- No authentication required

### 5. Owner Experience
Owner should **never see activation-related messages again**.

Dashboard should simply show:
- QR is active
- Usage / contacts (if applicable)

### 6. User Experience (Scanner)
Scanner sees only:
- Contact page of the owner
- Call / message / reach options
- **Zero friction. Zero system messages.**

---

## Implementation Details

### Routes
- `/gateways/activate/<qr_code>/` - Activation page (only for unactivated QR)
- `/gateways/g/<qr_code>/` - Public access (always redirects to contact page if activated)

### Logic Flow
```
User scans QR code
    ↓
Is QR activated?
    ↓ YES → Redirect to contact page (ALWAYS)
    ↓ NO  → Show activation form
```

### Vehicle Number Validation
- Each vehicle number can only be registered once
- Prevents duplicate registrations
- Shows clear error if vehicle already registered

---

## What Changed

### Before (Bad UX)
- Owner scanning their own QR → "Already activated by you" message
- Confusion about what to do next
- Unnecessary state checks

### After (Good UX)
- **Anyone** scanning activated QR → Direct to contact page
- No messages, no confusion
- Pure public access behavior

---

## Key Takeaway
**Showing "already activated" is bad UX. It solves no problem. It has been removed entirely, not hidden.**
