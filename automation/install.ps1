$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskConfig = Get-Content -LiteralPath (Join-Path $taskRoot 'config.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$taskPython = (Get-Command python.exe).Source
$taskPythonWindowless = Join-Path (Split-Path -Parent $taskPython) 'pythonw.exe'
if (!(Test-Path -LiteralPath $taskPythonWindowless)) { throw 'pythonw.exe missing' }
$taskRunner = Join-Path $taskRoot 'runner.py'
$taskAction = New-ScheduledTaskAction -Execute $taskPythonWindowless -Argument ('"' + $taskRunner + '" --dispatch') -WorkingDirectory $taskRoot
$taskTime = [DateTimeOffset]::Parse($taskConfig.not_before).LocalDateTime
$taskTrigger = New-ScheduledTaskTrigger -Once -At $taskTime
$taskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 4)
$taskUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $taskUser -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskConfig.task_name -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Principal $taskPrincipal -Description 'One-shot AI R&D course presentation after quota reset, with real preflight and independent Codex session.' -Force | Out-Null
Export-ScheduledTask -TaskName $taskConfig.task_name | Set-Content -LiteralPath (Join-Path $taskRoot 'task.xml') -Encoding UTF8
$taskInfo = Get-ScheduledTaskInfo -TaskName $taskConfig.task_name
$taskInstalled = Get-ScheduledTask -TaskName $taskConfig.task_name
[pscustomobject]@{TaskName=$taskConfig.task_name; NextRunTime=$taskInfo.NextRunTime.ToString('o'); State=$taskInstalled.State.ToString(); Python=$taskPythonWindowless} | ConvertTo-Json -Compress | Set-Content -LiteralPath (Join-Path $taskRoot 'setup_status.json') -Encoding UTF8
Start-ScheduledTask -TaskName $taskConfig.task_name
Get-Content -LiteralPath (Join-Path $taskRoot 'setup_status.json') -Encoding UTF8
