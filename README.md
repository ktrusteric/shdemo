# 能源交易一体化系统 Demo

## 项目概述
这是一个能源交易一体化系统的演示环境，主要包含以下功能模块：

- 用户管理系统（注册、登录、付费服务）
- 能源信息服务（资讯、报价、成交数据、研报、指数）
- AI智能助手（客服助手、资讯助手、交易助手）
- 个性化推荐系统
- 数据管理系统

## 技术栈
- **前端**: HTML5, CSS3, JavaScript, Bootstrap
- **后端**: Python, Flask
- **数据库**: MongoDB
- **AI服务**: 集成外部AI助手API

## 系统架构
```
energy-trading-system/
├── backend/          # 后端服务
│   ├── api/         # API接口
│   ├── models/      # 数据模型
│   ├── services/    # 业务逻辑
│   └── utils/       # 工具函数
├── frontend/        # 前端界面
│   ├── css/        # 样式文件
│   ├── js/         # JavaScript文件
│   ├── images/     # 图片资源
│   └── pages/      # HTML页面
├── database/       # 数据库脚本
└── docs/          # 项目文档
```

## 快速开始

### 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装并启动MongoDB
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb
```

### 运行系统
```bash
# 启动后端服务
cd backend
python app.py

# 前端直接在浏览器中打开 frontend/index.html
```

## 功能说明

### 1. 用户系统
- 用户注册：收集注册地和交易品种信息
- 用户登录：身份验证
- 付费服务：区分免费用户和付费用户权限

### 2. 能源信息服务
- 实时资讯：天然气行业新闻和动态
- 报价数据：实时和历史报价信息
- 成交数据：交易成交信息统计
- 研究报告：行业研报管理
- 指数数据：价格指数等关键指标

### 3. AI助手
- 客服助手：解答用户问题
- 资讯助手：提供个性化资讯
- 交易助手：辅助交易决策

### 4. 个性化推荐
- 基于用户标签的内容推荐
- "猜你喜欢"功能
- 行为数据分析

## 开发团队
能源交易一体化系统开发团队

## 许可证
MIT License 