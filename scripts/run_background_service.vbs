' ==============================================================================
' HH LOANHUB - Windows Silent Background Service Runner
' Phase 0: Hybrid Deployment Architecture
'
' Silently executes start_local_engine.bat and start_remote_tunnel.bat
' with zero visible command prompt windows (Window Style = 0, SW_HIDE).
'
' You can create a shortcut to this .vbs file and place it in your
' Windows Startup folder (Win+R -> shell:startup) to automatically start
' your core engine on boot.
' ==============================================================================

Option Explicit

Dim fso, shell, scriptDir, engineBat, tunnelBat

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

' Resolve absolute path to the scripts directory
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

engineBat = """" & scriptDir & "\start_local_engine.bat"""
tunnelBat = """" & scriptDir & "\start_remote_tunnel.bat"""

' 1. Silently launch Local FastAPI Core Engine
' Run(command, windowStyle, waitOnReturn) -> 0 = Hidden window, False = Do not wait
shell.Run "cmd.exe /c " & engineBat, 0, False

' 2. Pause 2.5 seconds to let the FastAPI server bind port 8000
WScript.Sleep 2500

' 3. Silently launch Cloudflare Remote Tunnel
shell.Run "cmd.exe /c " & tunnelBat, 0, False

' Clean up COM objects
Set fso = Nothing
Set shell = Nothing
