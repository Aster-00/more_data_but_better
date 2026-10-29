# Write Windows crash dumps to F: (HDD) instead of C: (the NVMe SSD suspected in the crashes, decisions.md D-009).
# Until now every crash failed to save its dump (volmgr event 161), so the faulting driver is unknown.
# Run once in an ADMINISTRATOR PowerShell, then reboot (not while a GPU queue is running):
#   powershell -ExecutionPolicy Bypass -File F:\Thesis\code\scripts\pc_crashdump_to_F.ps1
# Undo: run with -Undo (restores the values printed below), then reboot.
param([switch]$Undo)

# HKLM can only be changed from an elevated shell; stop before touching anything otherwise.
$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Not an administrator shell: nothing changed. Start menu -> type PowerShell -> 'Run as administrator', then run this again."
    exit 1
}

$key = 'HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl'
$dir = 'F:\CrashDumps'

if ($Undo) {
    # Original values on 2026-10-13: DumpFile C:\WINDOWS\MEMORY.DMP, MinidumpDir C:\WINDOWS\Minidumps,
    # no DedicatedDumpFile / DumpFileSize, CrashDumpEnabled 3 (small memory dump).
    Remove-ItemProperty $key -Name DedicatedDumpFile, DumpFileSize -ErrorAction SilentlyContinue
    Set-ItemProperty $key -Name DumpFile -Value 'C:\WINDOWS\MEMORY.DMP' -Type ExpandString
    Set-ItemProperty $key -Name MinidumpDir -Value 'C:\WINDOWS\Minidumps' -Type ExpandString
} else {
    "Before:"; Get-ItemProperty $key | Select-Object CrashDumpEnabled, DumpFile, MinidumpDir, DedicatedDumpFile, DumpFileSize | Format-List
    New-Item -ItemType Directory -Force $dir | Out-Null
    # The dump is first written to this dedicated file on F: (instead of the pagefile on C:),
    # then copied to MinidumpDir after the reboot. 2048 MB is plenty for a small memory dump.
    Set-ItemProperty $key -Name DedicatedDumpFile -Value "$dir\DedicatedDump.sys" -Type String
    Set-ItemProperty $key -Name DumpFileSize -Value 2048 -Type DWord
    Set-ItemProperty $key -Name DumpFile -Value "$dir\MEMORY.DMP" -Type ExpandString
    Set-ItemProperty $key -Name MinidumpDir -Value "$dir\Minidump" -Type ExpandString
}
"After:"; Get-ItemProperty $key | Select-Object CrashDumpEnabled, DumpFile, MinidumpDir, DedicatedDumpFile, DumpFileSize | Format-List
"Reboot for the change to take effect."
