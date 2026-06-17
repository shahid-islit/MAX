Set WShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get the folder where this script lives
ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' Start FastAPI silently
WShell.Run "cmd /c cd /d """ & ScriptDir & """ && venv\Scripts\activate && uvicorn api:app --port 8000", 0, False

' Wait 3 seconds for FastAPI
WScript.Sleep 3000

' Start Express silently  
WShell.Run "cmd /c cd /d """ & ScriptDir & "\server"" && node index.js", 0, False

' Wait 2 seconds for Express
WScript.Sleep 2000

' Start Electron (this one is visible — it's the HUD)
WShell.Run "cmd /c cd /d """ & ScriptDir & "\electron"" && npm start", 0, False