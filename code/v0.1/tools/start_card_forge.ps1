param(
    [int]$Port = 8765,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$Root = Join-Path $PSScriptRoot "card_forge_web"
$Prefix = "KARDS-DIY-GENERATOR"

if (-not (Test-Path -LiteralPath (Join-Path $Root "$Prefix\index.html"))) {
    Write-Host "缺少网页副本: $Root" -ForegroundColor Red
    Read-Host "按回车退出"
    exit 1
}

$Mime = @{
    ".html" = "text/html; charset=utf-8"
    ".js"   = "text/javascript; charset=utf-8"
    ".css"  = "text/css; charset=utf-8"
    ".json" = "application/json; charset=utf-8"
    ".svg"  = "image/svg+xml"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".jpeg" = "image/jpeg"
    ".webp" = "image/webp"
    ".woff" = "font/woff"
    ".woff2"= "font/woff2"
    ".ttf"  = "font/ttf"
    ".ico"  = "image/x-icon"
}

function Send-Response {
    param(
        [System.Net.Sockets.NetworkStream]$Stream,
        [int]$Status,
        [string]$Reason,
        [byte[]]$Body,
        [string]$ContentType = "text/plain; charset=utf-8",
        [string]$Location = ""
    )
    $headerLines = @(
        "HTTP/1.1 $Status $Reason",
        "Content-Type: $ContentType",
        "Content-Length: $($Body.Length)",
        "Cache-Control: no-store",
        "Connection: close"
    )
    if ($Location) { $headerLines += "Location: $Location" }
    $header = ($headerLines -join "`r`n") + "`r`n`r`n"
    $headerBytes = [Text.Encoding]::UTF8.GetBytes($header)
    $Stream.Write($headerBytes, 0, $headerBytes.Length)
    if ($Body.Length -gt 0) { $Stream.Write($Body, 0, $Body.Length) }
    $Stream.Flush()
}

$listener = [System.Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $Port)
$listener.Start()
$url = "http://127.0.0.1:$Port/$Prefix/"

Write-Host ""
Write-Host "KARDS Card Forge 本地网页" -ForegroundColor Yellow
Write-Host $url -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor DarkGray
Write-Host ""

if (-not $NoBrowser) {
    $browser = @(
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    ) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if ($browser) {
        Start-Process -FilePath $browser -ArgumentList "--app=$url"
    } else {
        Start-Process $url
    }
}

try {
    while ($true) {
        $client = $listener.AcceptTcpClient()
        try {
            $stream = $client.GetStream()
            $reader = [System.IO.StreamReader]::new($stream, [Text.Encoding]::ASCII)
            $requestLine = $reader.ReadLine()
            if ([string]::IsNullOrWhiteSpace($requestLine)) {
                $client.Close()
                continue
            }
            while ($true) {
                $line = $reader.ReadLine()
                if ([string]::IsNullOrEmpty($line)) { break }
            }
            $parts = $requestLine -split " "
            if ($parts.Length -lt 2) {
                Send-Response $stream 400 "Bad Request" ([Text.Encoding]::UTF8.GetBytes("Bad Request"))
                $client.Close()
                continue
            }
            $path = [Uri]::UnescapeDataString($parts[1].Split("?")[0])
            if ($path -eq "/") {
                Send-Response $stream 302 "Found" ([byte[]]@()) "text/plain" "/$Prefix/"
                $client.Close()
                continue
            }
            $relative = $path.TrimStart("/")
            Write-Host "DEBUG path=[$path] relative=[$relative]"
            if ($relative -eq "$Prefix" -or $relative -eq "$Prefix/") { $relative = "$Prefix/index.html" }
            if (-not $relative.StartsWith("$Prefix/")) {
                Send-Response $stream 404 "Not Found" ([Text.Encoding]::UTF8.GetBytes("Not Found"))
                $client.Close()
                continue
            }
            $file = Join-Path $Root $relative
            $resolved = [System.IO.Path]::GetFullPath($file)
            Write-Host "DEBUG file=[$file] resolved=[$resolved]"
            $rootFull = [System.IO.Path]::GetFullPath($Root)
            if (-not $resolved.StartsWith($rootFull, [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
                Send-Response $stream 404 "Not Found" ([Text.Encoding]::UTF8.GetBytes("Not Found"))
                $client.Close()
                continue
            }
            $bytes = [System.IO.File]::ReadAllBytes($resolved)
            $ext = [System.IO.Path]::GetExtension($resolved).ToLowerInvariant()
            $contentType = if ($Mime.ContainsKey($ext)) { $Mime[$ext] } else { "application/octet-stream" }
            Send-Response $stream 200 "OK" $bytes $contentType
        } catch {
            Write-Host "请求失败: $($_.Exception.Message)" -ForegroundColor DarkYellow
        } finally {
            $client.Close()
        }
    }
} finally {
    $listener.Stop()
}
