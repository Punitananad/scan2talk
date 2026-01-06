# Mobile Access Guide

## ✅ Setup Complete!

Your Django server is now configured to be accessible from your mobile device on the same WiFi network.

## 📱 How to Access from Mobile

### Your Computer's IP Address
**192.168.1.75**

### Access URLs from Mobile

1. **Homepage**
   ```
   http://192.168.1.75:8000/
   ```

2. **Admin Panel**
   ```
   http://192.168.1.75:8000/admin/
   ```

3. **QR Generation (Admin)**
   ```
   http://192.168.1.75:8000/gateways/gqr/
   ```

4. **QR Dashboard**
   ```
   http://192.168.1.75:8000/gateways/qr/dashboard/
   ```

5. **QR Activation (Example)**
   ```
   http://192.168.1.75:8000/gateways/activate/ABC12XYZ/
   ```

## 🚀 Start the Server

Run this command to start the server accessible on your network:

```bash
python manage.py runserver 0.0.0.0:8000
```

**Important:** Use `0.0.0.0:8000` instead of just `runserver` to bind to all network interfaces.

## 📋 Testing Steps

### 1. Start Server on Computer
```bash
python manage.py runserver 0.0.0.0:8000
```

### 2. Generate QR Code
- On computer, visit: http://192.168.1.75:8000/gateways/gqr/
- Generate 1 QR code
- Click "View" or "Download" to see the QR image

### 3. Scan from Mobile
- Open mobile camera or QR scanner app
- Scan the QR code from your computer screen
- Should open: http://192.168.1.75:8000/gateways/activate/[CODE]/
- Complete the 3-step activation process

### 4. Test Activation Flow
1. **Step 1:** Enter your mobile number
2. **Step 2:** Check terminal on computer for OTP
3. **Step 3:** Enter OTP on mobile
4. **Step 4:** Fill vehicle details
5. **Success:** QR activated!

## 🔧 Troubleshooting

### Can't Access from Mobile?

**Check WiFi Connection:**
- Ensure mobile and computer are on SAME WiFi network
- Not on mobile data

**Check Firewall:**
```bash
# Windows: Allow port 8000
# Go to Windows Firewall → Allow an app
# Or temporarily disable firewall for testing
```

**Verify IP Address:**
```bash
ipconfig
# Look for IPv4 Address under your WiFi adapter
```

**Test Connection:**
- On mobile browser, visit: http://192.168.1.75:8000
- Should see homepage

### Server Not Starting?

**Port Already in Use:**
```bash
# Use different port
python manage.py runserver 0.0.0.0:8001
# Then access: http://192.168.1.75:8001
```

**Permission Error:**
```bash
# Run as administrator (Windows)
# Or use port above 1024
```

## 📱 Mobile Browser Tips

### Best Browsers for Testing
- Chrome (Android/iOS)
- Safari (iOS)
- Firefox (Android)

### Enable Developer Mode
- Chrome: Settings → Developer options
- Safari: Settings → Advanced → Web Inspector

### Clear Cache
- If pages don't load correctly
- Clear browser cache and cookies
- Force refresh (Ctrl+F5 equivalent)

## 🎯 Real QR Code Testing

### Print QR Code
1. Download QR image from dashboard
2. Print on paper or display on another screen
3. Scan with mobile camera
4. Should open activation page

### QR Code Apps
- **Android:** Google Lens, QR Scanner
- **iOS:** Built-in Camera app
- **Both:** Any QR code reader app

## 🔐 Security Notes

### Development Only
- This setup is for LOCAL TESTING only
- NOT for production use
- Only accessible on your local network

### Production Setup
For production, you'll need:
- Proper domain name
- HTTPS/SSL certificate
- Firewall configuration
- Load balancer
- Production server (not runserver)

## 📊 Network Info

### Your Setup
- **Computer IP:** 192.168.1.75
- **Server Port:** 8000
- **Access URL:** http://192.168.1.75:8000
- **Network:** Local WiFi

### Check if Server is Running
On mobile browser, visit:
```
http://192.168.1.75:8000
```

Should see the homepage with:
- "Connect With Vehicle Owners"
- "Without Sharing Numbers"
- Blue gradient header

## ✅ Quick Checklist

Before testing from mobile:

- [ ] Computer and mobile on same WiFi
- [ ] Server running with `0.0.0.0:8000`
- [ ] Firewall allows port 8000
- [ ] Can access http://192.168.1.75:8000 from mobile browser
- [ ] QR code generated and visible
- [ ] Mobile camera/QR app ready

## 🎉 You're Ready!

Start the server with:
```bash
python manage.py runserver 0.0.0.0:8000
```

Then on your mobile:
1. Open browser
2. Visit: http://192.168.1.75:8000
3. Or scan QR code to test activation

Happy testing! 📱✨
