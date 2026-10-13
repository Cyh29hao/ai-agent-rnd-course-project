param([Parameter(Mandatory=$true)][string]$VideoPath,[Parameter(Mandatory=$true)][string]$OutDir)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
function Pump-Dispatcher([int]$Milliseconds) {
    $taskFrame = New-Object System.Windows.Threading.DispatcherFrame
    $taskTimer = New-Object System.Windows.Threading.DispatcherTimer
    $taskTimer.Interval = [TimeSpan]::FromMilliseconds($Milliseconds)
    $taskTimer.Tag = $taskFrame
    $taskTimer.Add_Tick({ param($sender,$eventArgs) $sender.Stop(); $sender.Tag.Continue = $false })
    $taskTimer.Start()
    [System.Windows.Threading.Dispatcher]::PushFrame($taskFrame)
}
$mediaPlayer = New-Object System.Windows.Media.MediaPlayer
$mediaPlayer.ScrubbingEnabled = $true
$mediaPlayer.Open([Uri]::new([IO.Path]::GetFullPath($VideoPath)))
$mediaPlayer.Play()
Pump-Dispatcher 1500
$mediaPlayer.Pause()
if ($mediaPlayer.NaturalVideoWidth -eq 0 -or -not $mediaPlayer.NaturalDuration.HasTimeSpan) { throw 'Windows MediaPlayer did not decode video.' }
[IO.Directory]::CreateDirectory($OutDir) | Out-Null
$taskDuration = $mediaPlayer.NaturalDuration.TimeSpan.TotalSeconds
$taskWidth = $mediaPlayer.NaturalVideoWidth
$taskHeight = $mediaPlayer.NaturalVideoHeight
$taskTimes = @(0.1,($taskDuration / 2),($taskDuration - 0.5))
for ($taskIndex=0; $taskIndex -lt $taskTimes.Count; $taskIndex++) {
    $mediaPlayer.Position = [TimeSpan]::FromSeconds($taskTimes[$taskIndex])
    Pump-Dispatcher 800
    $taskVisual = New-Object System.Windows.Media.DrawingVisual
    $taskContext = $taskVisual.RenderOpen()
    $taskContext.DrawVideo($mediaPlayer,[System.Windows.Rect]::new(0,0,$taskWidth,$taskHeight))
    $taskContext.Close()
    $taskBitmap = [System.Windows.Media.Imaging.RenderTargetBitmap]::new($taskWidth,$taskHeight,96,96,[System.Windows.Media.PixelFormats]::Pbgra32)
    $taskBitmap.Render($taskVisual)
    $taskEncoder = New-Object System.Windows.Media.Imaging.PngBitmapEncoder
    $taskEncoder.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($taskBitmap))
    $taskStream = [IO.File]::Create((Join-Path $OutDir ('decoded_{0:00}.png' -f ($taskIndex+1))))
    try { $taskEncoder.Save($taskStream) } finally { $taskStream.Dispose() }
}
$mediaPlayer.Close()
@{decoded=$true;duration=$taskDuration;width=$taskWidth;height=$taskHeight;samples=$taskTimes;decoder='Windows WPF MediaPlayer'} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $OutDir 'decode.json') -Encoding UTF8
Write-Output ('DECODED seconds={0} size={1}x{2}' -f $taskDuration,$taskWidth,$taskHeight)
