$src  = "$PSScriptRoot\slice_sage_1.json"
$dest = "$PSScriptRoot\04_abstracts\slices_round2\slice_sage_1.json"
New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
Copy-Item -Path $src -Destination $dest -Force
Write-Host "Copied to $dest"
