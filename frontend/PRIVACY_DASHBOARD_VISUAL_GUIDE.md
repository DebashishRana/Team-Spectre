# Seva Setu Privacy Dashboard - Visual Guide

## 📸 Component Layout Overview

### Full Page Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                      HEADER (Blue Gradient)                      │
│                                                                   │
│  Privacy & Security Controls          🔒 Secure (Badge)         │
│  Manage your personal data, permissions, and privacy settings    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 1: YOUR PERMISSIONS                                      │
├─────────────────────────────────────────────────────────────────┤
│ Control what Seva Setu can do with your data                     │
│                                                                   │
│ ┌─ Permission Item ─────────────────────────────────────────┐   │
│ │                                                             │   │
│ │ Allow Secure Document Storage            [●━━━] (ON)      │   │
│ │ Store your documents safely in encrypted...               │   │
│                                                             │
│ ├─ Permission Item ─────────────────────────────────────────┤   │
│ │ Allow Autofill Across Government Forms   [●━━━] (ON)      │   │
│ │ Auto-populate your data in eligible...                     │   │
│                                                             │
│ ├─ Permission Item ─────────────────────────────────────────┤   │
│ │ Allow Scheme Recommendations              [━━━●] (OFF)    │   │
│ │ Receive personalized government scheme...                  │   │
│                                                             │
│ └─ Permission Item ─────────────────────────────────────────┘   │
│   Allow Data Sharing with Gov Portals      [━━━●] (OFF)        │
│   Share verified data with authorized...                     │   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 2: RECENT DATA USAGE                                     │
├─────────────────────────────────────────────────────────────────┤
│ See how your data has been accessed and used                     │
│                                                                   │
│ 📋 Scholarship Application Autofill      ⏰ Today, 2:45 PM       │
│                                          [View Details →]        │
│                                                                   │
│ ✓ KYC Verification                       ⏰ Yesterday, 11:20 AM  │
│                                          [View Details →]        │
│                                                                   │
│ 🔍 Scheme Eligibility Check               ⏰ 2 days ago, 3:15 PM │
│                                          [View Details →]        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 3: PROTECTED INFORMATION                                 │
├─────────────────────────────────────────────────────────────────┤
│ Your most sensitive data is masked for security                  │
│                                                                   │
│ ┌─────────────────────────┐  ┌─────────────────────────┐          │
│ │ Aadhaar Number          │  │ Phone Number            │          │
│ │ [⚠️ Reveal]             │  │ [⚠️ Reveal]             │          │
│ │ XXXX XXXX 9123          │  │ XXXXXXX890              │          │
│ └─────────────────────────┘  └─────────────────────────┘          │
│                                                                   │
│ ┌─────────────────────────────────────────┐                      │
│ │ Email Address                           │                      │
│ │ [⚠️ Reveal]                             │                      │
│ │ user.n****@email.com                    │                      │
│ └─────────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 4: MANAGE YOUR DATA                                      │
├─────────────────────────────────────────────────────────────────┤
│ Take full control of your personal information                   │
│                                                                   │
│  [⬇️ Download My Data ]     [🗑️ Delete All Data ]               │
│   (Blue Button)              (Red Button)                         │
│                                                                   │
│ ┌─────────────────────────────────────────┐                      │
│ │ Auto Delete After 30 Days  [●━━━] (ON)  │                      │
│ │ Auto-clear processor data after 30 days │                      │
│ └─────────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 5: ADVANCED PRIVACY MODE                                 │
├─────────────────────────────────────────────────────────────────┤
│ Enhanced privacy for temporary document processing               │
│                                                                   │
│ ┌─────────────────────────────────────────┐                      │
│ │ Process Without Saving  [●━━━] (ON)    │                      │
│ │                                          │                      │
│ │ Your documents will be processed temp   │                      │
│ │ and deleted immediately after use...    │                      │
│ │                                          │                      │
│ │ ✨ Advanced Privacy Mode is active      │                      │
│ └─────────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 6: CONTROL SPECIFIC DATA FIELDS                          │
├─────────────────────────────────────────────────────────────────┤
│ Choose which personal data can be used in autofill               │
│                                                                   │
│ ☑ Full Name                              ✓ Enabled              │
│   Your legal name                                                │
│                                                                   │
│ ☑ Date of Birth                          ✓ Enabled              │
│   Your date of birth                                             │
│                                                                   │
│ ☐ Aadhaar Number                         ✗ Disabled             │
│   Your Aadhaar ID                                                │
│                                                                   │
│ ☑ Address                                ✓ Enabled              │
│   Your residential address                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SECTION 7: SECURITY OVERVIEW                                     │
├─────────────────────────────────────────────────────────────────┤
│ Your security status and protections                             │
│                                                                   │
│ ┌─────────────────────────────────────┐                          │
│ │ ✓ End-to-End Encryption             │                          │
│ │   All data is encrypted in transit   │                          │
│ │   and at rest                        │                          │
│ └─────────────────────────────────────┘                          │
│                                                                   │
│ ┌─────────────────────────────────────┐                          │
│ │ ✓ Secure Storage Active             │                          │
│ │   Your documents are stored in       │                          │
│ │   secure servers                     │                          │
│ └─────────────────────────────────────┘                          │
│                                                                   │
│ ┌─────────────────────────────────────┐                          │
│ │ ✓ Last Security Check               │                          │
│ │   Today at 10:30 AM - All systems    │                          │
│ │   nominal                            │                          │
│ └─────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Component States

### Toggle Switch States

```
OFF State (Gray):              ON State (Green):
┌─────────────────┐            ┌─────────────────┐
│ [━━━●]          │            │ [●━━━]  ✓       │
│ Inactive        │            │ Active          │
└─────────────────┘            └─────────────────┘

Hover OFF:                      Hover ON:
┌─────────────────┐            ┌─────────────────┐
│ [━━━●] (darker) │            │ [●━━━] (lighter)│
│ Slightly darker │            │ Slightly lighter│
└─────────────────┘            └─────────────────┘
```

### Button States

#### Primary Button (Download)
```
Default:                       Hover:
┌──────────────────┐          ┌──────────────────┐
│ ⬇️ Download My  │          │ ⬇️ Download My  │ (elevated)
│ Data             │          │ Data             │
│                  │          │   + shadow       │
│  (Blue)          │          │  (Darker Blue)   │
└──────────────────┘          └──────────────────┘
```

#### Danger Button (Delete)
```
Default:                       Hover:
┌──────────────────┐          ┌──────────────────┐
│ 🗑️ Delete All   │          │ 🗑️ Delete All   │ (elevated)
│ Data             │          │ Data             │
│                  │          │                  │
│ (Light Red)      │          │  (Dark Red)      │
└──────────────────┘          └──────────────────┘
```

### Modal Dialog

```
┌─────────────────────────────────────┐
│ ⚠️ Delete All Data         [✕]      │
├─────────────────────────────────────┤
│                                      │
│ Are you sure you want to            │
│ permanently delete all your data?   │
│                                      │
│ ⚠️ This action cannot be undone.    │
│ All documents, preferences, and     │
│ history will be deleted.             │
│                                      │
├─────────────────────────────────────┤
│                                     │
│  [Cancel]      [Permanently Delete] │
│  (Gray)        (Red)                │
│                                     │
└─────────────────────────────────────┘
```

---

## 📱 Responsive Layouts

### Desktop (1200px+)
```
┌──────────────────────────────────────────────┐
│ HEADER - Full width blue gradient            │
└──────────────────────────────────────────────┘
┌──────────────────────────────────────────────┐
│ SECTION - Full width card                    │
│ - 2 column grids where applicable            │
└──────────────────────────────────────────────┘
```

### Tablet (768px - 1024px)
```
┌──────────────────────────────────────────┐
│ HEADER - Reduced padding                 │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│ SECTION - Full width                     │
│ - Single column lists                    │
└──────────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌────────────────────┐
│ HEADER             │
│ (Stacked Content)  │
└────────────────────┘
┌────────────────────┐
│ PERMISSION         │
│ (Single Column)    │
└────────────────────┘
┌────────────────────┐
│ [Download]         │
│ [Delete]           │
│ (Full Width)       │
└────────────────────┘
```

---

## 🎯 Color Reference

### Primary Colors
```
Primary Blue (Buttons, Active States)
Color: #0066cc
RGB: (0, 102, 204)
Use: CTAs, toggles (ON), primary elements
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Success Green (Enabled, OK states)
Color: #10b981
RGB: (16, 185, 129)
Use: Active toggles, enabled fields, success badges
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Danger Red (Delete, Warning states)
Color: #ef4444
RGB: (239, 68, 68)
Use: Delete buttons, warnings, disabled states
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Neutral Gray (Backgrounds, Cards)
Color: #f3f4f6
RGB: (243, 244, 246)
Use: Card backgrounds, inactive elements
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Text Primary (Main text)
Color: #1f2937
RGB: (31, 41, 55)
Use: Headings, titles, primary text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Text Secondary (Supporting text)
Color: #6b7280
RGB: (107, 114, 128)
Use: Descriptions, labels, secondary text
```

---

## 🎬 Animation Timings

```
Property              Duration    Timing Function
─────────────────────────────────────────────────
Toggle Slider         400ms       cubic-bezier(0.4, 0, 0.2, 1)
Page Load (Slide In)  300ms       ease-out
Modal Open (Fade)     300ms       ease
Button Hover          300ms       ease
All Transitions       300ms       ease (default)
```

---

## 📐 Spacing Scale

```
0.25rem = 4px   (xs - micro spacing)
0.5rem  = 8px   (sm - small)
0.75rem = 12px  (md - medium)
1rem    = 16px  (lg - standard)
1.5rem  = 24px  (xl - large)
2rem    = 32px  (2xl - extra large)
2.5rem  = 40px  (3xl - heading padding)
3rem    = 48px  (4xl - section padding)
```

---

## 🎨 Typography Scale

```
H1:      2.5rem (40px) - Page Title
         font-weight: 700
         
H2:      1.5rem (24px) - Section Titles
         font-weight: 700
         
H3:      1rem - 1.05rem - Card Titles
         font-weight: 600
         
H4:      0.95rem - 1rem - Subsection titles
         font-weight: 600
         
Body:    0.9rem - 1rem - Main text
         font-weight: 400
         
Small:   0.85rem - 0.95rem - Labels, descriptions
         font-weight: 400
         
Tiny:    0.8rem - 0.85rem - Timestamps, status
         font-weight: 500
         
Code:    vary - Monospace font
         ('Monaco', 'Courier New')
         letter-spacing: 2px (for masked data)
```

---

## 🔍 Focus States (Accessibility)

```
Unfocused Button:          Focused Button:
┌──────────────┐          ┌──────────────┐
│ Click Me     │          │ Click Me     │
│              │          │              │
│              │          │ (2px blue outline)
└──────────────┘          └──────────────┘

Unfocused Toggle:          Focused Toggle:
[━━━●]                    [━━━●]
                          (Blue outline)

Unfocused Field:           Focused Field:
☐ Field Name              ☐ Field Name
                          (Blue outline)
```

---

## 📊 Icon Reference

```
Icon              Unicode   Use Case
──────────────────────────────────────────
🎯                         Section headers (goals)
📊                         Data/analytics
🔐                         Locked/secure
🛡️                         Protection/privacy
🔒                         Secure state
⚙️                         Settings/controls
⏰                         Time/timestamps
✓/✔️  / ☑                  Success/enabled/checked
✗/❌/☐                     Error/disabled/unchecked
📋                         Documents
🗑️                         Delete
⬇️                         Download
📝                         Logs/history
ℹ️                         Information
⚠️                         Warning/caution
👤                         User/profile
🔍                         Search/explore
```

---

## 🎯 User Flow Diagram

```
┌─────────────┐
│ User Opens  │
│ Privacy Pg  │
└──────┬──────┘
       │
       ├──→ ┌──────────────────┐
       │    │ View Permissions │ ← Toggle ON/OFF
       │    └──────────────────┘
       │
       ├──→ ┌──────────────────┐
       │    │ Check Data Usage │ ← View Details
       │    └──────────────────┘
       │
       ├──→ ┌──────────────────┐
       │    │ Reveal Sensitive │ ← Click Reveal
       │    │ Data             │   See Warning
       │    └──────────────────┘   Click Hide
       │
       ├──→ ┌──────────────────┐
       │    │ Private Mode     │ ← Toggle ON/OFF
       │    └──────────────────┘
       │
       ├──→ ┌──────────────────┐
       │    │ Field Controls   │ ← Check/Uncheck
       │    └──────────────────┘
       │
       └──→ ┌──────────────────┐
            │ Delete Data      │ ← Click Delete
            │ (Confirmation)   │   Modal Opens
            └──────────────────┘   Confirm/Cancel
```

---

## 🚀 Quick Reference - Feature Summary

| Feature | Location | Interaction | State |
|---------|----------|-------------|-------|
| Permission Toggles | Section 1 | Click to flip | ON/OFF |
| Data Usage Log | Section 2 | View Details | Read-only |
| Reveal Sensitive | Section 3 | Click Reveal | Masked/Shown |
| Download Data | Section 4 | Click button | API call |
| Delete Data | Section 4 | Click button | Modal confirm |
| Auto-Delete | Section 4 | Toggle | ON/OFF |
| Privacy Mode | Section 5 | Toggle | ON/OFF |
| Field Perms | Section 6 | Checkbox | Enabled/Disabled |
| Security Status | Section 7 | Display | Read-only |

---

## ✨ Animation & Transition Examples

### Permission Card Hover
```
Before:  Normal card with gray background
         └─ Smooth transition (0.3s)
After:   Light blue background + darker border
         └─ Subtle elevation effect
```

### Toggle Switch Activation
```
Before:  Gray slider [━━━●]
         └─ 400ms smooth transition
After:   Green slider [●━━━]
         └─ Plus color change + position change
```

### Modal Appearance
```
Before:  Hidden (opacity: 0)
         └─ 300ms ease fade-in
After:   Visible + slide-up from below
         └─ Semi-transparent dark overlay
```

---

## 🎯 Pro Tips for Demo

1. **Toggle all permissions** to show state changes
2. **Hover over cards** to show animation effects
3. **Click Reveal** to show sensitive data masking
4. **Resize browser** to show responsive design
5. **Click Delete** to show confirmation modal
6. **Open DevTools** to show clean CSS structure

---

✨ **This visual guide provides a complete reference for the Privacy Dashboard UI!**
