# 简单启动脚本 - PowerShell版本
Write-Host "Starting Multimodal AI Agent System..." -ForegroundColor Green

# 检查是否有运行中的Streamlit进程
$streamlitProcess = Get-Process -Name "streamlit" -ErrorAction SilentlyContinue
if ($streamlitProcess) {
    Write-Host "Stopping existing Streamlit process..." -ForegroundColor Yellow
    Stop-Process -Name "streamlit" -Force
    Start-Sleep -Seconds 2
}

# 检查环境文件
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env file and set your API key" -ForegroundColor Red
    Write-Host "Then run this script again" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit
}

# 创建必要目录
$directories = @("logs", "chroma_db", "data", "temp")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    }
}

# 启动简化版应用
Write-Host "Starting Streamlit application..." -ForegroundColor Green
Write-Host "Access URL: http://localhost:8502" -ForegroundColor Cyan

try {
    # 启动Streamlit应用
    Start-Process -FilePath "python" -ArgumentList "-m", "streamlit", "run", "simple_streamlit_app.py", "--server.port=8502", "--server.address=localhost" -NoNewWindow
    
    Write-Host "Application started successfully!" -ForegroundColor Green
    Write-Host "Opening browser..." -ForegroundColor Yellow
    
    # 等待2秒后打开浏览器
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8502"
    
    Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
    
} catch {
    Write-Host "Failed to start application: $_" -ForegroundColor Red
}

Read-Host "Press Enter to exit"
