# Part A Environment Check Script
# Run this to verify Windows setup for VirtualBox

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "O-RAN xApp Project - Environment Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# A1. Check Virtualization
Write-Host "[A1] Checking CPU Virtualization..." -ForegroundColor Yellow
$cpu = Get-CimInstance -ClassName Win32_Processor | Select-Object -First 1
$vmEnabled = $cpu.VirtualizationFirmwareEnabled

if ($vmEnabled) {
    Write-Host "  ✓ Virtualization: ENABLED" -ForegroundColor Green
} else {
    Write-Host "  ✗ Virtualization: DISABLED" -ForegroundColor Red
    Write-Host "    ACTION REQUIRED: Enable VT-x/AMD-V in BIOS" -ForegroundColor Red
}
Write-Host ""

# A2. Check Hyper-V and WSL
Write-Host "[A2] Checking Windows Features..." -ForegroundColor Yellow
$features = @(
    "Microsoft-Hyper-V",
    "VirtualMachinePlatform",
    "HypervisorPlatform",
    "Microsoft-Windows-Subsystem-Linux"
)

$conflicts = @()
foreach ($feature in $features) {
    $state = Get-WindowsOptionalFeature -Online -FeatureName $feature -ErrorAction SilentlyContinue
    if ($state -and $state.State -eq "Enabled") {
        $conflicts += $feature
    }
}

if ($conflicts.Count -eq 0) {
    Write-Host "  ✓ No conflicting features enabled" -ForegroundColor Green
} else {
    Write-Host "  ✗ Conflicting features found:" -ForegroundColor Red
    foreach ($c in $conflicts) {
        Write-Host "    - $c" -ForegroundColor Red
    }
    Write-Host "    ACTION REQUIRED: Disable these in 'Turn Windows features on or off'" -ForegroundColor Red
}
Write-Host ""

# A3. Check Visual C++ Redistributable
Write-Host "[A3] Checking Visual C++ Redistributable..." -ForegroundColor Yellow
$vcRedist = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" -ErrorAction SilentlyContinue
if ($vcRedist) {
    Write-Host "  ✓ Visual C++ Redistributable installed (version $($vcRedist.Version))" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Visual C++ Redistributable not detected" -ForegroundColor Yellow
    Write-Host "    Download: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
}
Write-Host ""

# A4. Check VirtualBox
Write-Host "[A4] Checking VirtualBox installation..." -ForegroundColor Yellow
$vboxPath = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
if (Test-Path $vboxPath) {
    $vboxVersion = & $vboxPath --version
    Write-Host "  ✓ VirtualBox installed: $vboxVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ VirtualBox not found" -ForegroundColor Red
    Write-Host "    Download: https://www.virtualbox.org/wiki/Downloads" -ForegroundColor Red
}
Write-Host ""

# A5. Check Ubuntu ISO
Write-Host "[A5] Checking for Ubuntu 22.04 ISO..." -ForegroundColor Yellow
$possiblePaths = @(
    "$env:USERPROFILE\Downloads\ubuntu-22.04*.iso",
    "C:\College\Project\5G\ubuntu-22.04*.iso"
)

$isoFound = $false
foreach ($path in $possiblePaths) {
    $files = Get-Item $path -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "  ✓ Found: $($files[0].FullName)" -ForegroundColor Green
        Write-Host "    Size: $([math]::Round($files[0].Length/1GB, 2)) GB" -ForegroundColor Green
        $isoFound = $true
        break
    }
}

if (-not $isoFound) {
    Write-Host "  ⚠ Ubuntu 22.04 ISO not found" -ForegroundColor Yellow
    Write-Host "    Download: https://releases.ubuntu.com/22.04/" -ForegroundColor Yellow
    Write-Host "    Select: 64-bit PC (AMD64) desktop image" -ForegroundColor Yellow
}
Write-Host ""

# System Resources
Write-Host "[SYSTEM] Resource Check..." -ForegroundColor Yellow
$ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB, 1)
$cores = (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors

Write-Host "  Total RAM: $ram GB" -ForegroundColor $(if ($ram -ge 16) {"Green"} else {"Red"})
if ($ram -lt 16) {
    Write-Host "    ⚠ WARNING: 16GB+ recommended, you have $ram GB" -ForegroundColor Yellow
}

Write-Host "  CPU Cores: $cores" -ForegroundColor $(if ($cores -ge 4) {"Green"} else {"Red"})
if ($cores -lt 4) {
    Write-Host "    ⚠ WARNING: 4+ cores recommended, you have $cores" -ForegroundColor Yellow
}

$disk = Get-PSDrive C | Select-Object -ExpandProperty Free
$diskGB = [math]::Round($disk/1GB, 1)
Write-Host "  Free Disk Space: $diskGB GB" -ForegroundColor $(if ($diskGB -ge 100) {"Green"} else {"Red"})
if ($diskGB -lt 100) {
    Write-Host "    ⚠ WARNING: 100GB+ recommended, you have $diskGB GB" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$allGood = $vmEnabled -and ($conflicts.Count -eq 0) -and (Test-Path $vboxPath) -and $isoFound

if ($allGood) {
    Write-Host "✓ ALL CHECKS PASSED - Ready for Part B (VM Creation)" -ForegroundColor Green
} else {
    Write-Host "⚠ ACTION REQUIRED - Complete the items marked above" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    if (-not $vmEnabled) {
        Write-Host "  1. Reboot and enter BIOS to enable VT-x/AMD-V" -ForegroundColor White
    }
    if ($conflicts.Count -gt 0) {
        Write-Host "  2. Start → 'Turn Windows features on or off' → Disable Hyper-V/WSL" -ForegroundColor White
        Write-Host "     Then restart Windows" -ForegroundColor White
    }
    if (-not (Test-Path $vboxPath)) {
        Write-Host "  3. Download and install VirtualBox (run as administrator)" -ForegroundColor White
    }
    if (-not $isoFound) {
        Write-Host "  4. Download Ubuntu 22.04 ISO (64-bit desktop)" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
