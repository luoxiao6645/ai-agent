@echo off
echo 🔧 Git网络问题诊断和修复工具
echo ================================

echo.
echo 1. 测试网络连接...
ping -n 2 github.com

echo.
echo 2. 检查当前Git配置...
git config --list | findstr proxy
git config --list | findstr url

echo.
echo 3. 尝试不同的解决方案...
echo.

echo 方案A: 清除所有代理设置
git config --global --unset http.proxy 2>nul
git config --global --unset https.proxy 2>nul
git config --global --unset http.sslVerify 2>nul

echo 方案B: 设置DNS
git config --global http.postBuffer 1048576000
git config --global core.compression 0

echo 方案C: 使用IPv4
git config --global http.version HTTP/1.1

echo.
echo 4. 尝试推送...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ❌ 推送失败，尝试备用方案...
    echo.
    
    echo 方案D: 使用系统代理
    git config --global http.proxy http://127.0.0.1:7890
    git config --global https.proxy http://127.0.0.1:7890
    
    echo 再次尝试推送...
    git push -u origin main
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ 仍然失败，尝试最后方案...
        
        echo 方案E: 手动上传
        echo 请手动将以下文件上传到GitHub:
        echo - app.py
        echo - simple_streamlit_app.py  
        echo - requirements.txt
        echo - .streamlit/config.toml
        echo - DEPLOYMENT.md
        echo.
        echo 或者使用GitHub Desktop客户端进行推送
    ) else (
        echo ✅ 推送成功！
    )
) else (
    echo ✅ 推送成功！
)

echo.
echo 5. 显示仓库信息...
echo 仓库地址: https://github.com/luoxiao6645/ai-agent
echo 下一步: 访问 https://share.streamlit.io/ 进行部署

pause
