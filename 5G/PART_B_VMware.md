# Part B: Create VM in VMware Workstation Pro

## Step-by-Step VM Creation

### 1. Open VMware Workstation Pro
- Click **"Create a New Virtual Machine"**

### 2. Configuration Type
- Select **"Custom (advanced)"** → Next

### 3. Hardware Compatibility
- Keep default (latest Workstation version) → Next

### 4. Guest Operating System Installation
- Select **"Installer disc image file (iso)"**
- Click **Browse** → Select your `ubuntu-22.04.x-desktop-amd64.iso`
- Next

### 5. Easy Install Information
- **Full name:** Your name (e.g., "Student")
- **Username:** lowercase, no spaces (e.g., "student" or "oran")
- **Password:** Create a password (WRITE IT DOWN!)
- Next

### 6. Virtual Machine Name
- **Name:** `ORAN-Ubuntu`
- **Location:** Keep default or choose location with enough space
- Next

### 7. Processor Configuration
- **Number of processors:** 1
- **Number of cores per processor:** 8 (half of your 16 cores)
- Next

### 8. Memory for Virtual Machine
- **Memory:** `8192` MB (8 GB)
- Next

### 9. Network Type
- Select **"Use network address translation (NAT)"**
- Next

### 10. I/O Controller Type
- Keep default **"LSI Logic (Recommended)"**
- Next

### 11. Virtual Disk Type
- Keep default **"SCSI (Recommended)"**
- Next

### 12. Disk
- Select **"Create a new virtual disk"**
- Next

### 13. Disk Size
- **Maximum disk size:** `80` GB
- Select **"Store virtual disk as a single file"**
- Next

### 14. Disk File
- Keep default name
- Next

### 15. Ready to Create
- Click **"Customize Hardware..."**

#### In Hardware Settings:
- **Display:**
  - **3D graphics:** Uncheck "Accelerate 3D graphics"
  - **Graphics memory:** 2 GB is fine (VMware auto-manages this)
  
- **USB Controller:** Can keep enabled
- **Sound Card:** Can remove (not needed)
- **Printer:** Remove (not needed)

- Click **OK**
- Click **Finish**

### 16. First Boot
- The VM will start automatically
- Ubuntu installation will begin (Easy Install does most work automatically)
- **Wait 20-30 minutes** for automatic installation to complete
- VM will reboot automatically when done

---

## Post-Installation (After VM Reboots)

### 1. Login
- Use the username and password you set during creation

### 2. Install VMware Tools
VMware Tools should install automatically. If not:

```bash
# In the VM terminal
sudo apt update
sudo apt install -y open-vm-tools open-vm-tools-desktop
sudo reboot
```

After reboot, you should be able to:
- Resize the window (auto-resize display)
- Copy/paste between host and VM
- Drag & drop files

### 3. Verify Installation

Open Terminal in Ubuntu (Ctrl+Alt+T) and run:

```bash
lsb_release -a
# Should show: Ubuntu 22.04.x LTS

nproc
# Should show: 8

free -h
# Should show: ~8GB total

df -h ~
# Should show plenty of free space

vmware-toolbox-cmd -v
# Should show VMware Tools version
```

---

## VM Settings Checklist

✓ **8 GB RAM**  
✓ **8 CPU cores**  
✓ **80 GB disk**  
✓ **NAT networking**  
✓ **3D acceleration OFF**  
✓ **Ubuntu 22.04 LTS**  
✓ **VMware Tools installed**  

---

## Troubleshooting

### VM is slow during installation
- Normal for first boot
- Give it 30 minutes
- Check Task Manager on Windows - VM should be using CPU

### Can't resize window
- Install VMware Tools (see Post-Installation step 2)
- VM → Install VMware Tools (from menu)

### Black screen after installation
- Wait 2 minutes
- Press Enter
- If still black, restart VM

---

## Next: Once Ubuntu is Ready

After Ubuntu is fully installed and you can login:

✓ Mark Part B complete  
→ Proceed to **Part C: Install Dependencies and Docker**

Save a snapshot before proceeding:
- VM → Snapshot → Take Snapshot
- Name: "Fresh Ubuntu 22.04 Install"

This lets you restore if anything goes wrong later.
