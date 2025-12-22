$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Join-Path $root ".."
Set-Location $project

if (-not (Test-Path "node_modules")) {
  npm install
}

$port = $env:PORT
if (-not $port) { $port = 3000 }

$process = Start-Process npm -ArgumentList "run", "dev", "--", "--hostname", "0.0.0.0", "--port", $port -PassThru
Start-Sleep -Seconds 3
Start-Process "http://localhost:$port"
Wait-Process -Id $process.Id
