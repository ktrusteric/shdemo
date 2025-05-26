#!/bin/bash

echo "========================================"
echo "能源交易一体化系统启动脚本"
echo "========================================"

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查MongoDB服务
echo "检查MongoDB服务..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "MongoDB未运行，尝试启动MongoDB..."
    sudo systemctl start mongodb || sudo service mongodb start
    sleep 2
fi

# 检查MongoDB连接
if ! mongo --eval "db.version()" > /dev/null 2>&1; then
    echo "警告: 无法连接到MongoDB，请确保MongoDB已正确安装并运行"
fi

# 进入backend目录
cd backend

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r ../requirements.txt

# 初始化示例数据
echo "是否要初始化示例数据？(y/n)"
read -r init_data
if [[ $init_data == "y" || $init_data == "Y" ]]; then
    echo "初始化示例数据..."
    python3 init_data.py
fi

# 启动后端服务
echo "启动后端服务..."
echo "服务将在 http://localhost:5000 运行"
echo "前端页面请在浏览器中打开 frontend/index.html"
echo "按 Ctrl+C 停止服务"
echo "========================================"

# 启动Flask应用
python3 app.py 