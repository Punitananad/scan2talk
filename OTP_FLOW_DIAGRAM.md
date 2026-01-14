# OTP Verification Flow Diagram

## Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER SCANS QR CODE                           │
│                           ↓                                      │
│              /gateways/activate/{qr_code}/                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: ENTER PHONE NUMBER                                     │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  📱 Enter 10-digit mobile number                      │     │
│  │  [__________]                                         │     │
│  │  [Continue Button]                                    │     │
│  └───────────────────────────────────────────────────────┘     │
│                           ↓                                      │
│  Validation: Must be exactly 10 digits                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND: GENERATE & SEND OTP                                   │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  1. Generate 6-digit random OTP                       │     │
│  │  2. Hash OTP (SHA-256)                                │     │
│  │  3. Store in cache (5 min expiry)                     │     │
│  │  4. Prepare SMS message                               │     │
│  │  5. Send via SMSCountry API                           │     │
│  └───────────────────────────────────────────────────────┘     │
│                           ↓                                      │
│  POST https://restapi.smscountry.com/v0.1/SMSes/               │
│  Authorization: Basic base64(AuthKey:AuthToken)                 │
│  Body: {                                                        │
│    "Text": "Your OTP for Scan2Talk website registration        │
│             is 123456. Do not share it with anyone.             │
│             - Scan2Talk",                                       │
│    "Number": "919876543210",                                    │
│    "SenderId": "SCNTLK",                                        │
│    "DLTTemplateId": "1707176830112398745",                      │
│    "Tool": "API"                                                │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  USER RECEIVES SMS                                              │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  📱 SMS from SCNTLK:                                  │     │
│  │  "Your OTP for Scan2Talk website registration        │     │
│  │   is 123456. Do not share it with anyone.            │     │
│  │   - Scan2Talk"                                        │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: VERIFY OTP                                             │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  🔐 Enter 6-digit OTP                                 │     │
│  │  [______]                                             │     │
│  │  [Verify Button]                                      │     │
│  │                                                       │     │
│  │  ← Change phone number                                │     │
│  │  Didn't receive OTP? [Resend]                        │     │
│  │                                                       │     │
│  │  ℹ️ OTP valid for 5 minutes. 3 attempts allowed.     │     │
│  └───────────────────────────────────────────────────────┘     │
│                           ↓                                      │
│  User enters OTP                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND: VERIFY OTP                                            │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  1. Retrieve stored OTP data from cache              │     │
│  │  2. Check if OTP expired (> 5 min)                   │     │
│  │  3. Check remaining attempts (max 3)                 │     │
│  │  4. Hash entered OTP                                 │     │
│  │  5. Compare hashes                                   │     │
│  │  6. If match: Delete OTP, mark verified ✅           │     │
│  │  7. If no match: Decrement attempts ❌               │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
              ✅ SUCCESS            ❌ FAILURE
                    │                   │
                    ↓                   ↓
    ┌───────────────────────┐  ┌──────────────────────┐
    │ Mark phone verified   │  │ Show error message   │
    │ Proceed to Step 3     │  │ Decrement attempts   │
    └───────────────────────┘  │ Allow retry          │
                               └──────────────────────┘
                                        ↓
                            ┌───────────┴───────────┐
                            │                       │
                    Attempts > 0            Attempts = 0
                            │                       │
                            ↓                       ↓
                    Stay on Step 2      Delete OTP, request new
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: ENTER VEHICLE DETAILS                                  │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  👤 Name: [________________]                          │     │
│  │  🚗 Vehicle Type: [Car ▼]                            │     │
│  │  🔢 Vehicle Number: [__________]                      │     │
│  │  📝 Vehicle Model: [________________]                 │     │
│  │  [Activate Button]                                    │     │
│  └───────────────────────────────────────────────────────┘     │
│                           ↓                                      │
│  Validation: Name and vehicle number required                   │
│  Check: Vehicle number not already registered                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  BACKEND: ACTIVATE TAG                                          │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  1. Get or create user by phone                       │     │
│  │  2. Create gateway for vehicle                        │     │
│  │  3. Activate QR code                                  │     │
│  │  4. Create QR wallet (if prepaid category)            │     │
│  │  5. Auto-login user                                   │     │
│  │  6. Clear session data                                │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  ✅ ACTIVATION SUCCESS                                          │
│  ┌───────────────────────────────────────────────────────┐     │
│  │  🎉 Activation successful! Welcome {name}!            │     │
│  │                                                       │     │
│  │  Your tag is now active and ready to use.            │     │
│  │                                                       │     │
│  │  [Go to Dashboard]                                    │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Security Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  OTP SECURITY MEASURES                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. GENERATION                                                  │
│     • 6-digit random number (000000-999999)                     │
│     • Cryptographically secure random                           │
│     • Unique per request                                        │
│                                                                 │
│  2. HASHING                                                     │
│     • Algorithm: SHA-256                                        │
│     • Plain OTP never stored                                    │
│     • Hash stored in cache                                      │
│                                                                 │
│  3. STORAGE                                                     │
│     • Location: Django cache (in-memory/Redis)                  │
│     • Format: {                                                 │
│         'otp_hash': 'sha256_hash',                              │
│         'attempts': 3,                                          │
│         'created_at': 'timestamp'                               │
│       }                                                         │
│     • Expiry: 5 minutes (300 seconds)                           │
│                                                                 │
│  4. VERIFICATION                                                │
│     • Hash entered OTP                                          │
│     • Compare with stored hash                                  │
│     • Constant-time comparison                                  │
│     • Decrement attempts on failure                             │
│                                                                 │
│  5. ATTEMPT LIMITING                                            │
│     • Maximum: 3 attempts                                       │
│     • Counter decremented on each failure                       │
│     • OTP deleted after max attempts                            │
│     • User must request new OTP                                 │
│                                                                 │
│  6. EXPIRY                                                      │
│     • Time limit: 5 minutes                                     │
│     • Automatic deletion after expiry                           │
│     • No grace period                                           │
│                                                                 │
│  7. INVALIDATION                                                │
│     • On successful verification                                │
│     • On max attempts exceeded                                  │
│     • On expiry                                                 │
│     • On resend request                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## API Communication Flow

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│          │                │          │                │          │
│  Client  │                │  Django  │                │SMSCountry│
│ (Browser)│                │  Server  │                │   API    │
│          │                │          │                │          │
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ 1. Enter phone number     │                           │
     ├──────────────────────────>│                           │
     │                           │                           │
     │                           │ 2. Generate OTP           │
     │                           │    (6-digit random)       │
     │                           │                           │
     │                           │ 3. Hash OTP (SHA-256)     │
     │                           │                           │
     │                           │ 4. Store in cache         │
     │                           │    (5 min expiry)         │
     │                           │                           │
     │                           │ 5. POST /SMSes/           │
     │                           ├──────────────────────────>│
     │                           │    Headers:               │
     │                           │    - Content-Type: json   │
     │                           │    - Authorization: Basic │
     │                           │    Body:                  │
     │                           │    - Text: OTP message    │
     │                           │    - Number: 91XXXXXXXXXX │
     │                           │    - SenderId: SCNTLK     │
     │                           │    - DLTTemplateId        │
     │                           │    - Tool: API            │
     │                           │                           │
     │                           │ 6. Response (200 OK)      │
     │                           │<──────────────────────────┤
     │                           │    {                      │
     │                           │      "Success": true,     │
     │                           │      "MessageId": "..."   │
     │                           │    }                      │
     │                           │                           │
     │ 7. OTP sent successfully  │                           │
     │<──────────────────────────┤                           │
     │                           │                           │
     │                           │                      8. SMS sent
     │                           │                      to user's phone
     │                           │                           │
     │ 9. User receives SMS      │                           │
     │    (OTP: 123456)          │                           │
     │                           │                           │
     │ 10. Enter OTP             │                           │
     ├──────────────────────────>│                           │
     │                           │                           │
     │                           │ 11. Hash entered OTP      │
     │                           │                           │
     │                           │ 12. Retrieve from cache   │
     │                           │                           │
     │                           │ 13. Compare hashes        │
     │                           │                           │
     │                           │ 14. If match: Delete OTP  │
     │                           │     Mark verified         │
     │                           │                           │
     │ 15. Verification success  │                           │
     │<──────────────────────────┤                           │
     │                           │                           │
     │ 16. Proceed to Step 3     │                           │
     │                           │                           │
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  ERROR SCENARIOS & HANDLING                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. INVALID PHONE NUMBER                                        │
│     Input: "123" or "abc123" or "12345678901"                  │
│     ↓                                                           │
│     Validation fails                                            │
│     ↓                                                           │
│     Error: "Invalid phone number format. Must be 10 digits."   │
│     ↓                                                           │
│     Stay on Step 1, allow retry                                 │
│                                                                 │
│  2. SMS SENDING FAILURE                                         │
│     API returns error or timeout                                │
│     ↓                                                           │
│     Log error details                                           │
│     ↓                                                           │
│     If DEBUG=True: Generate OTP anyway (dev mode)               │
│     If DEBUG=False: Show error, allow retry                     │
│                                                                 │
│  3. WRONG OTP ENTERED                                           │
│     User enters incorrect OTP                                   │
│     ↓                                                           │
│     Hash doesn't match                                          │
│     ↓                                                           │
│     Decrement attempts (3 → 2 → 1 → 0)                         │
│     ↓                                                           │
│     Error: "Invalid OTP. X attempt(s) remaining."              │
│     ↓                                                           │
│     If attempts > 0: Allow retry                                │
│     If attempts = 0: Delete OTP, request new                    │
│                                                                 │
│  4. OTP EXPIRED                                                 │
│     User enters OTP after 5 minutes                             │
│     ↓                                                           │
│     OTP not found in cache                                      │
│     ↓                                                           │
│     Error: "OTP expired or not found. Please request new OTP." │
│     ↓                                                           │
│     Redirect to Step 1 or show resend button                    │
│                                                                 │
│  5. SESSION EXPIRED                                             │
│     User returns after session timeout                          │
│     ↓                                                           │
│     Phone number not in session                                 │
│     ↓                                                           │
│     Error: "Session expired. Please start again."              │
│     ↓                                                           │
│     Redirect to Step 1                                          │
│                                                                 │
│  6. VEHICLE ALREADY REGISTERED                                  │
│     Vehicle number exists in database                           │
│     ↓                                                           │
│     Show detailed error page                                    │
│     ↓                                                           │
│     Display: Vehicle number, existing owner                     │
│     ↓                                                           │
│     Provide support contact                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Development vs Production Mode

```
┌─────────────────────────────────────────────────────────────────┐
│  DEVELOPMENT MODE (DEBUG=True)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • Credentials not required                                     │
│  • OTP printed to console                                       │
│  • No actual SMS sent                                           │
│  • API errors ignored                                           │
│  • Full flow testable                                           │
│  • Faster testing                                               │
│                                                                 │
│  Console Output:                                                │
│  ==================================================             │
│  📱 OTP for 9876543210: 123456                                  │
│  ==================================================             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION MODE (DEBUG=False)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • Credentials required                                         │
│  • Real SMS sent via SMSCountry                                 │
│  • DLT compliance enforced                                      │
│  • API errors reported                                          │
│  • Full error handling                                          │
│  • Monitoring and logging                                       │
│                                                                 │
│  SMS Sent:                                                      │
│  From: SCNTLK                                                   │
│  To: +91 9876543210                                             │
│  Message: "Your OTP for Scan2Talk website registration         │
│            is 123456. Do not share it with anyone.              │
│            - Scan2Talk"                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

**Visual Flow Complete** ✅

This diagram shows the complete OTP verification flow from user scan to tag activation, including all security measures, error handling, and API communication.
