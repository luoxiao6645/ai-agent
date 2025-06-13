@echo off
echo 🚀 GitHub仓库设置脚本
echo.

echo 请先在GitHub上创建仓库 'multimodal-ai-agent'
echo 然后输入您的GitHub用户名:
set /p username="GitHub用户名: "

echo.
echo 正在连接到GitHub仓库...

git remote add origin https://github.com/%username%/multimodal-ai-agent.git
git branch -M main
git push -u origin main

echo.
echo ✅ 代码已推送到GitHub!
echo 🌐 仓库地址: https://github.com/%username%/multimodal-ai-agent
echo.
echo 下一步: 访问 https://share.streamlit.io/ 进行部署
pause
