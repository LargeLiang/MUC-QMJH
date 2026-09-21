$ErrorActionPreference = 'Stop'
$revisionRoot = Split-Path -Parent $PSScriptRoot
$docPath = Join-Path $revisionRoot 'output/doc/数学的实践与认识_审稿修订_v3.docx'
$qaPath = Join-Path $revisionRoot 'output/qa_v3/word'
New-Item -ItemType Directory -Force -Path $qaPath | Out-Null
$wordApp = New-Object -ComObject Word.Application
$wordApp.Visible = $false
$wordApp.DisplayAlerts = 0
$wordDoc = $null
try {
    $wordDoc = $wordApp.Documents.Open($docPath, $false, $true)
    $wordDoc.Repaginate()
    $wordDoc.ExportAsFixedFormat((Join-Path $qaPath 'word_render.pdf'), 17)
    Write-Output ('Pages: ' + $wordDoc.ComputeStatistics(2))
} finally {
    if ($null -ne $wordDoc) { $wordDoc.Close(0) }
    $wordApp.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) | Out-Null
}
