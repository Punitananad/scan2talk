# Admin User-Centric Redesign
## Scan2Talk Vehicle Contact Manager

---

## Core Philosophy

**Every person who can log in is a User. Period.**

No more "Registrations", "QR Wallets", "Categories" as separate dashboards. Everything flows from the User.

---

## 1. Admin Navigation Structure

```
Admin Dashboard
├── Users (Master List)
├── QR Inventory
├── System Settings
│   ├── Categories
│   ├── Plans
│   └── Configuration
└── Reports & Analytics
```

### Navigation Breakdown

**Users** - The single source of truth
- Master list of all users
- Click any user → Opens unified User Profile

**QR Inventory** - Unassigned QR codes only
- Available QR codes
- QR batches
- Generate new QR codes
- Once assigned to a user, QR appears in that User's profile

**System Settings** - Configuration only
- Categories (pricing tiers)
- Plans (recharge packages)
- System configuration

**Reports & Analytics** - System-wide metrics
- Revenue reports
- Usage analytics
- System health

---

## 2. User Profile Page (Tabbed Layout)

### URL Structure
```
/admin/users/                    → User list
/admin/users/{user_id}/          → User profile (Overview tab)
/admin/users/{user_id}/vehicles/ → Vehicles tab
/admin/users/{user_id}/qr-codes/ → QR Codes tab
/admin/users/{user_id}/wallet/   → Wallet tab
```


### Tab 1: Overview

**Account Information**
- User ID, Email, Phone (decrypted)
- Account Status: Active / Locked / Suspended
- Role: Individual / Business / Enterprise
- Created Date, Last Login, Last Login IP
- Failed Login Attempts

**Subscription & Plan**
- Current Plan: Free / Premium / Enterprise
- Category: (if assigned) - e.g., "Prepaid Vehicle", "Free Trial"
- Gateway Limit: 3/5 used
- Monthly Interaction Limit: 45/100 used

**Quick Stats**
- Total Vehicles: 3
- Total QR Codes: 3 (2 activated, 1 available)
- Wallet Balance: ₹150.00
- Call Credits: 150
- Total Orders: 2 (1 delivered, 1 shipped)


**Quick Actions**
- Edit Account Details
- Change Category/Plan
- Lock/Unlock Account
- Add Wallet Balance
- Send Notification
- View Activity Log

---

### Tab 2: Vehicles

**Vehicle List Table**
| Vehicle Number | QR Code | Status | Activated On | Last Access | Actions |
|----------------|---------|--------|--------------|-------------|---------|
| MH12AB1234 | QR-001 | Active | 2024-01-15 | 2 hours ago | View Details / Deactivate |
| DL01CD5678 | QR-002 | Active | 2024-01-20 | 1 day ago | View Details / Deactivate |
| KA03EF9012 | - | Pending | - | - | Assign QR |

**Actions**
- Assign QR Code to Vehicle
- Deactivate Vehicle
- View Vehicle Access History
- Download Vehicle QR

**Vehicle Details Modal**
- Vehicle Number
- Owner Name
- Contact Phone (decrypted)
- QR Code Assigned
- Activation Date
- Total Accesses
- Last Access Date & Time
- Access History (last 10)

---

### Tab 3: QR Codes

**QR Code List Table**
| QR Code | Batch | Status | Vehicle | Activated On | Actions |
|---------|-------|--------|---------|--------------|---------|
| QR-001 | Batch-A | Activated | MH12AB1234 | 2024-01-15 | View / Download / Deactivate |
| QR-002 | Batch-A | Activated | DL01CD5678 | 2024-01-20 | View / Download / Deactivate |
| QR-003 | Batch-B | Available | - | - | Assign / Download |

**Filters**
- Status: All / Available / Activated / Deactivated
- Batch: All / Batch-A / Batch-B / etc.

**Actions**
- Assign QR to Vehicle
- Download QR (PDF)
- Deactivate QR
- View QR Details
- Bulk Download (selected QRs)

**QR Details Modal**
- QR Code ID
- Batch Name
- Status
- Assigned Vehicle (if any)
- Activation Date
- Total Scans
- Last Scan Date
- Public URL
- Preview QR Image

---

### Tab 4: Wallet & Transactions

**Wallet Summary**
- Current Balance: ₹150.00
- Call Credits: 150 credits
- Total Recharged: ₹500.00
- Total Spent: ₹350.00

**Quick Actions**
- Add Balance (Manual)
- Deduct Balance
- Add Call Credits
- View Full Transaction History

**Recent Transactions Table**
| Date | Type | Amount | Credits | Balance After | Status | Reference |
|------|------|--------|---------|---------------|--------|-----------|
| 2024-01-25 | Recharge | +₹200 | +200 | ₹150 | Success | TXN123456 |
| 2024-01-24 | Call Usage | -₹50 | -50 | ₹100 | Completed | CALL789 |
| 2024-01-20 | Recharge | +₹300 | +300 | ₹150 | Success | TXN123455 |

**Filters**
- Type: All / Recharge / Usage / Refund / Adjustment
- Date Range: Last 7 days / Last 30 days / Custom
- Status: All / Success / Failed / Pending

**Recharge Orders Table**
| Order ID | Date | Amount | Gateway | Status | Actions |
|----------|------|--------|---------|--------|---------|
| ORD-001 | 2024-01-25 | ₹200 | PhonePe | Delivered | View Details |
| ORD-002 | 2024-01-20 | ₹300 | PhonePe | Delivered | View Details |

---

### Tab 5: Activity Log

**Activity Timeline**
- Login/Logout events
- QR Code activations
- Vehicle registrations
- Wallet transactions
- Profile updates
- Failed login attempts
- API calls (if applicable)

**Log Entry Format**
```
[2024-01-25 14:30:45] User logged in from IP 192.168.1.100
[2024-01-25 14:32:10] Activated QR-003 for vehicle KA03EF9012
[2024-01-25 14:35:20] Recharged wallet: ₹200 (Order: ORD-001)
[2024-01-24 09:15:30] Vehicle MH12AB1234 accessed via QR-001
```

**Filters**
- Event Type: All / Login / QR Activity / Wallet / Profile
- Date Range: Today / Last 7 days / Last 30 days / Custom
- IP Address filter

---

## 3. Users Master List Page

### URL: `/admin/users/`

**Page Layout**

**Search & Filters**
- Search: Email, Phone, User ID, Vehicle Number
- Status: All / Active / Locked / Suspended
- Category: All / Free / Prepaid / Premium / Enterprise
- Registration Date: Last 7 days / Last 30 days / Custom
- Has Vehicles: Yes / No / All
- Wallet Balance: > ₹0 / = ₹0 / All

**User List Table**
| User ID | Email | Phone | Category | Vehicles | QR Codes | Wallet | Status | Registered | Actions |
|---------|-------|-------|----------|----------|----------|--------|--------|------------|---------|
| U-001 | user1@example.com | +91-98765-43210 | Prepaid | 3 | 3 | ₹150 | Active | 2024-01-10 | View Profile |
| U-002 | user2@example.com | +91-98765-43211 | Free | 1 | 1 | ₹0 | Active | 2024-01-15 | View Profile |
| U-003 | user3@example.com | +91-98765-43212 | Premium | 5 | 5 | ₹500 | Active | 2024-01-20 | View Profile |

**Bulk Actions**
- Export Selected (CSV/Excel)
- Send Notification to Selected
- Change Category (Bulk)
- Lock/Unlock Accounts (Bulk)

**Pagination**
- Show: 25 / 50 / 100 per page
- Total: 1,234 users

---

## 4. QR Inventory Page

### URL: `/admin/qr-inventory/`

**Purpose**: Manage unassigned QR codes and batches

**Page Sections**

### Available QR Codes

**Filters**
- Batch: All / Batch-A / Batch-B / etc.
- Status: Available / Reserved
- Generated Date: Last 7 days / Last 30 days / Custom

**QR List Table**
| QR Code | Batch | Generated On | Status | Actions |
|---------|-------|--------------|--------|---------|
| QR-100 | Batch-C | 2024-01-25 | Available | Download / Assign to User |
| QR-101 | Batch-C | 2024-01-25 | Available | Download / Assign to User |
| QR-102 | Batch-D | 2024-01-26 | Available | Download / Assign to User |

**Bulk Actions**
- Download Selected (PDF)
- Assign to User (Bulk)
- Delete Selected

---

### QR Batches

**Batch List Table**
| Batch Name | Total QR | Available | Assigned | Generated On | Actions |
|------------|----------|-----------|----------|--------------|---------|
| Batch-A | 100 | 20 | 80 | 2024-01-10 | View / Download All |
| Batch-B | 50 | 35 | 15 | 2024-01-15 | View / Download All |
| Batch-C | 200 | 198 | 2 | 2024-01-25 | View / Download All |

**Actions**
- View Batch Details
- Download Batch (PDF)
- Delete Batch (if all QR codes are unassigned)

---

### Generate New QR Codes

**Form**
- Batch Name: [Text Input]
- Number of QR Codes: [Number Input]
- Category (Optional): [Dropdown]
- Generate Button

**After Generation**
- Success message with batch details
- Option to download immediately
- Batch appears in QR Batches list

---

## 5. System Settings

### URL: `/admin/settings/`

**Tabbed Layout**

---

### Tab 1: Categories

**Purpose**: Manage pricing tiers and user categories

**Category List Table**
| Category Name | Type | Price/Credit | Gateway Limit | Monthly Limit | Users | Actions |
|---------------|------|--------------|---------------|---------------|-------|---------|
| Free Trial | Free | ₹0 | 1 | 10 | 45 | Edit / Delete |
| Prepaid Vehicle | Prepaid | ₹1/call | 5 | 100 | 120 | Edit / Delete |
| Premium | Subscription | ₹500/month | 10 | Unlimited | 30 | Edit / Delete |
| Enterprise | Custom | Custom | Unlimited | Unlimited | 5 | Edit / Delete |

**Actions**
- Add New Category
- Edit Category
- Delete Category (if no users assigned)
- View Users in Category

**Add/Edit Category Form**
- Category Name
- Type: Free / Prepaid / Subscription / Custom
- Price per Credit (for Prepaid)
- Monthly Fee (for Subscription)
- Gateway Limit
- Monthly Interaction Limit
- Features (checkboxes)
  - Call Masking
  - WhatsApp Integration
  - Email Notifications
  - SMS Notifications
  - IVR Support
  - Priority Support

---

### Tab 2: Plans

**Purpose**: Manage recharge packages

**Plan List Table**
| Plan Name | Amount | Credits | Bonus | Validity | Active | Actions |
|-----------|--------|---------|-------|----------|--------|---------|
| Starter | ₹100 | 100 | 0 | 30 days | Yes | Edit / Deactivate |
| Basic | ₹200 | 200 | 20 | 60 days | Yes | Edit / Deactivate |
| Pro | ₹500 | 500 | 100 | 90 days | Yes | Edit / Deactivate |
| Enterprise | ₹1000 | 1000 | 300 | 180 days | Yes | Edit / Deactivate |

**Actions**
- Add New Plan
- Edit Plan
- Activate/Deactivate Plan
- Delete Plan (if never used)

**Add/Edit Plan Form**
- Plan Name
- Amount (₹)
- Credits
- Bonus Credits
- Validity (days)
- Active Status
- Description

---

### Tab 3: Configuration

**System Configuration**

**General Settings**
- Site Name
- Support Email
- Support Phone
- Default Category for New Users
- Auto-assign QR on Registration: Yes / No

**Payment Gateway**
- PhonePe Merchant ID
- PhonePe Salt Key
- PhonePe Salt Index
- Test Mode: Enabled / Disabled

**Communication Settings**
- SMS Provider: [Dropdown]
- SMS API Key
- WhatsApp Provider: [Dropdown]
- WhatsApp API Key
- Email Provider: [Dropdown]
- Email API Key
- Call Masking Provider: [Dropdown]
- Call Masking API Key

**Security Settings**
- Max Failed Login Attempts
- Account Lock Duration (minutes)
- Session Timeout (minutes)
- OTP Validity (minutes)
- Require Email Verification: Yes / No
- Require Phone Verification: Yes / No

**Save Configuration Button**

---

## 6. Reports & Analytics

### URL: `/admin/reports/`

**Dashboard Widgets**

### Revenue Overview
- Today's Revenue: ₹5,420
- This Week: ₹32,150
- This Month: ₹1,24,500
- Total Revenue: ₹8,45,230

**Chart**: Revenue trend (last 30 days)

---

### User Statistics
- Total Users: 1,234
- Active Users (last 7 days): 856
- New Users (this month): 45
- Users with Vehicles: 980
- Users with Wallet Balance: 654

**Chart**: User growth (last 6 months)

---

### QR Code Statistics
- Total QR Codes Generated: 5,000
- Assigned QR Codes: 3,200
- Available QR Codes: 1,800
- Total Scans (all time): 45,678
- Scans (this month): 3,456

**Chart**: QR scan activity (last 30 days)

---

### Wallet Statistics
- Total Wallet Balance (all users): ₹1,24,500
- Total Credits Available: 1,24,500
- Average Wallet Balance: ₹101
- Total Recharges (this month): ₹2,45,000
- Total Usage (this month): ₹1,20,500

**Chart**: Wallet recharge vs usage (last 30 days)

---

### Communication Statistics
- Total Calls Made: 12,345
- Total SMS Sent: 8,765
- Total WhatsApp Messages: 5,432
- Total Emails Sent: 3,210

**Chart**: Communication channel usage (last 30 days)

---

### Top Users
| User | Vehicles | QR Scans | Wallet Balance | Total Spent |
|------|----------|----------|----------------|-------------|
| user1@example.com | 10 | 1,234 | ₹500 | ₹5,000 |
| user2@example.com | 8 | 987 | ₹300 | ₹3,500 |
| user3@example.com | 7 | 876 | ₹200 | ₹2,800 |

---

### Export Reports
- Date Range: [Date Picker]
- Report Type: Revenue / Users / QR Activity / Wallet / Communications
- Format: CSV / Excel / PDF
- Generate Report Button

---

## 7. Implementation Plan

### Phase 1: Backend Restructuring
1. Update `admin_views.py` to support new URL structure
2. Create user profile view with tab support
3. Consolidate QR wallet, registration, and category data into user profile
4. Add filtering and search capabilities to user list
5. Create QR inventory management views
6. Update system settings views

### Phase 2: Frontend Templates
1. Create new admin base template with updated navigation
2. Build user list page with filters and search
3. Build user profile page with tabbed interface
4. Build QR inventory page
5. Build system settings page with tabs
6. Build reports & analytics dashboard

### Phase 3: Data Migration
1. Ensure all existing data is accessible through new structure
2. No data model changes required (just view layer changes)
3. Test all existing functionality works with new interface

### Phase 4: Testing & Deployment
1. Test all admin workflows
2. Verify data integrity
3. User acceptance testing
4. Deploy to production

---

## 8. Key Benefits

**For Admins**
- Single source of truth: Everything about a user in one place
- Faster navigation: No more jumping between multiple dashboards
- Better context: See complete user picture at a glance
- Easier troubleshooting: All user data and activity in one view

**For System**
- Cleaner architecture: User-centric design is more maintainable
- Better scalability: Easier to add new user-related features
- Improved performance: Fewer database queries with consolidated views
- Better UX: Intuitive navigation follows mental model

---

## 9. URL Mapping (Complete)

```
# Admin URLs
/admin/                              → Admin Dashboard (redirect to /admin/users/)
/admin/users/                        → User Master List
/admin/users/{user_id}/              → User Profile (Overview tab)
/admin/users/{user_id}/vehicles/     → User Profile (Vehicles tab)
/admin/users/{user_id}/qr-codes/     → User Profile (QR Codes tab)
/admin/users/{user_id}/wallet/       → User Profile (Wallet tab)
/admin/users/{user_id}/activity/     → User Profile (Activity Log tab)

/admin/qr-inventory/                 → QR Inventory (Available QR codes)
/admin/qr-inventory/batches/         → QR Batches
/admin/qr-inventory/generate/        → Generate New QR Codes

/admin/settings/                     → System Settings (Categories tab)
/admin/settings/categories/          → Categories Management
/admin/settings/plans/               → Plans Management
/admin/settings/configuration/       → System Configuration

/admin/reports/                      → Reports & Analytics Dashboard
/admin/reports/export/               → Export Reports

# API Endpoints (for AJAX operations)
/api/admin/users/{user_id}/update/           → Update user details
/api/admin/users/{user_id}/lock/             → Lock/Unlock user
/api/admin/users/{user_id}/wallet/add/       → Add wallet balance
/api/admin/users/{user_id}/qr/assign/        → Assign QR to user
/api/admin/qr/{qr_id}/assign/                → Assign QR to vehicle
/api/admin/qr/{qr_id}/deactivate/            → Deactivate QR
/api/admin/categories/create/                → Create category
/api/admin/plans/create/                     → Create plan
```

---

## 10. Next Steps

1. **Review this design** with stakeholders
2. **Approve the user-centric approach**
3. **Begin Phase 1 implementation** (Backend restructuring)
4. **Create wireframes/mockups** for key pages (optional)
5. **Set timeline** for each phase

---

**Document Status**: Complete Design Specification
**Last Updated**: 2024-01-26
**Version**: 1.0
