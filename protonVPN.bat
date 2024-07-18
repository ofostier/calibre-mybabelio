@echo off
SET csv="C:\Users\trisula\Projects_dev\calibre-mybabelio\stop-vpn.txt"
IF EXIST %csv% (
    echo "file found"
    rem taskkill /F /IM ProtonVPN.exe /T
    timeout 10
    rem Start "&" "C:\Program Files\Proton\VPN\ProtonVPN.Launcher.exe"
    del %csv%
) else (
    echo "Not found"
    exit
)


