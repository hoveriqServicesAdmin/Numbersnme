# 📋 Admin Dashboard - Quick Reference Card

## 🎯 At a Glance

| Feature | Details |
|---------|---------|
| **Admin Button Location** | Top-right corner of header |
| **Modal Animation** | Slides in from right (300ms) |
| **Modal Width** | 450px (desktop) / 100% (mobile) |
| **Background Color** | #0c2022 (Dark Teal) |
| **Accent Color** | #d4af37 (Gold) |
| **Default Username** | Sangitha |
| **Default Password** | numbersnme2026 |
| **Session Type** | Browser session (HTTPONLY cookie) |
| **API Port** | 6000 |

---

## 🔐 Credentials

```
Username: Sangitha
Password: numbersnme2026
```

**To change**: Edit `main.py` → `ADMIN_USERNAME` and `ADMIN_PASSWORD`

---

## 📄 Files Modified/Created

| File | Action | Lines |
|------|--------|-------|
| `admin-modal.js` | CREATE | ~700 |
| `index.html` | MODIFY | +1 |
| `products.html` | MODIFY | +1 |
| `purchase.html` | MODIFY | +1 |

---

## 🔗 API Endpoints

### Login
```
POST /api/admin/login
Content-Type: application/json

{
  "username": "Sangitha",
  "password": "numbersnme2026"
}

Response:
{
  "success": true,
  "username": "Sangitha"
}
```

### Get Appointments
```
GET /api/admin/appointments
Authorization: Session (Cookie)

Response:
{
  "success": true,
  "appointments": [...],
  "summary": {
    "total": 45,
    "upcoming": 12,
    "today": 3,
    "completed_or_old": 30
  },
  "username": "Sangitha"
}
```

### Logout
```
POST /api/admin/logout

Response:
{
  "success": true
}
```

---

## 🎨 CSS Classes

| Class | Purpose |
|-------|---------|
| `.admin-modal-overlay` | Backdrop overlay |
| `.admin-modal-container` | Main panel |
| `.admin-modal-header` | Title bar |
| `.admin-login-form` | Login form |
| `.admin-dashboard-section` | Dashboard view |
| `.admin-btn` | Primary button |
| `.admin-ghost-btn` | Secondary button |
| `.admin-login-btn` | Header button |

---

## 🔧 JavaScript Methods

```javascript
// Open modal
AdminModal.open()

// Close modal
AdminModal.close()

// Login
AdminModal.handleLogin()

// Logout
AdminModal.handleLogout()

// Load appointments
AdminModal.loadAppointments(showSuccess)

// Switch view
AdminModal.switchView('login' | 'dashboard')

// Show status
AdminModal.showStatus(elementId, type, message)
```

---

## 📱 Breakpoints

| Device | Width | Behavior |
|--------|-------|----------|
| Desktop | >900px | 450px panel |
| Tablet | 600-900px | 450px panel |
| Mobile | <600px | 100% panel |

---

## 🔒 Security Checklist

- ✅ HTTPONLY cookies (can't access via JS)
- ✅ SAMESITE=Lax (CSRF protection)
- ✅ Backend validation (server-side checks)
- ✅ Session-based auth (not token-based)
- ✅ HTTPS recommended (production)
- ✅ Password hashing (werkzeug)
- ✅ Input validation (client + server)

---

## 🚀 Deployment Checklist

- [ ] Upload `admin-modal.js` to server
- [ ] Verify script tags in HTML files
- [ ] Set environment variables (if needed)
- [ ] Verify database connection
- [ ] Test login locally
- [ ] Test on production
- [ ] Monitor server logs
- [ ] Verify API endpoints

---

## 📊 Expected UI Elements

### Header
```
[Logo] [Nav Items] ... [Admin Button]
                              ↑
                         Top-Right
```

### Modal (Closed)
```
Not visible - click Admin button to open
```

### Modal (Login View)
```
┌─────────────────────────┐
│ Admin Panel          ✕ │
├─────────────────────────┤
│                         │
│ ○ Error/Success Message │
│                         │
│ Username:               │
│ [___________________]   │
│                         │
│ Password:               │
│ [___________________]   │
│                         │
│   [Sign In Button]      │
│                         │
└─────────────────────────┘
```

### Modal (Dashboard View)
```
┌──────────────────────────┐
│ Admin Panel           ✕  │
├──────────────────────────┤
│                          │
│ Signed in as Sangitha    │
│                          │
│ ┌──────────────────────┐ │
│ │ Total: 45            │ │
│ ├──────────────────────┤ │
│ │ Upcoming: 12         │ │
│ ├──────────────────────┤ │
│ │ Today: 3             │ │
│ └──────────────────────┘ │
│                          │
│ [Refresh] [Logout]       │
│                          │
│ Recent Appointments      │
│ ┌──────────────────────┐ │
│ │ NM123456             │ │
│ │ John Doe             │ │
│ │ 2025-04-30           │ │
│ │ +91 9999999999       │ │
│ └──────────────────────┘ │
│ ... (more items)         │
│                          │
└──────────────────────────┘
```

---

## 🧪 Testing Commands

```bash
# Check if server running
curl -I http://localhost:6000

# Test login endpoint
curl -X POST http://localhost:6000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"Sangitha","password":"numbersnme2026"}'

# Check database
sqlite3 numbersnme.db "SELECT COUNT(*) FROM appointments;"

# View recent appointments
sqlite3 numbersnme.db "SELECT booking_ref, appointment_date FROM appointments LIMIT 5;"
```

---

## 📈 Performance Metrics

| Metric | Expected |
|--------|----------|
| Script Load | <100ms |
| Modal Open | 300ms |
| Login API | 100-200ms |
| Dashboard Load | 100-300ms |
| Memory (JS) | ~2-3MB |

---

## 🎓 Common Tasks

### Add Admin to New Page
```html
<!-- Before </body> -->
<script src="admin-modal.js"></script>
```

### Change Admin Password
```python
# In main.py
ADMIN_PASSWORD = generate_password_hash('NewPassword123')
```

### Change Modal Color
```javascript
// In admin-modal.js, in createStyles() method
--admin-bg: #YOURCOLOR;
--admin-accent: #YOURCOLOR;
```

### Customize Modal Width
```javascript
// In admin-modal.js, in createStyles() method
.admin-modal-container {
    width: min(500px, 100%);  // Change 500px
}
```

---

## ❌ Troubleshooting

| Issue | Solution |
|-------|----------|
| Admin button missing | Check if `admin-modal.js` is loaded |
| Login fails | Verify credentials and server running |
| No appointments show | Check if appointments exist in DB |
| Modal doesn't close | Click overlay or X button |
| Session lost | Enable cookies in browser |

---

## 📞 Important Files

| File | Purpose |
|------|---------|
| `admin-modal.js` | Complete admin system |
| `main.py` | Backend APIs |
| `numbersnme.db` | Database |
| `ADMIN_QUICK_START.md` | Quick guide |
| `ADMIN_INTEGRATION_GUIDE.md` | Full docs |
| `IMPLEMENTATION_SUMMARY.md` | Overview |
| `ARCHITECTURE_DIAGRAM.md` | Visual diagrams |

---

## 🎉 Success Indicators

✅ Admin button visible in header  
✅ Modal slides in smoothly  
✅ Login accepts valid credentials  
✅ Dashboard shows appointment data  
✅ Refresh button updates data  
✅ Logout clears session  
✅ Works on all pages  
✅ Responsive on mobile  
✅ No console errors  
✅ Session persists across pages  

---

## 📚 Documentation Map

```
Quick Reference (this file)
    ↓
ADMIN_QUICK_START.md ........... For getting started
    ↓
ADMIN_INTEGRATION_GUIDE.md ..... For detailed info
    ↓
IMPLEMENTATION_SUMMARY.md ...... For overview
    ↓
ARCHITECTURE_DIAGRAM.md ........ For system design
```

---

**Created**: April 25, 2026  
**Version**: 1.0  
**Status**: ✅ Production Ready

