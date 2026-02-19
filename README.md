# 智谱AI Token 使用量统计工具

一个简洁实用的 Web 工具，用于分析和统计智谱AI API 的 Token 使用情况。

## 功能特点

- 上传 Excel 账单文件，自动分析 Token 使用量
- 按API Key 分组展示使用详情
- 按日期和模型细分统计
- 显示每个 API Key 的使用占比（百分比 + 可视化进度条）
- 支持导出 CSV 和 Excel 格式报表
- 响应式设计，支持移动端访问

## 技术栈

- **后端**: Python Flask
- **数据处理**: Pandas、OpenPyXL
- **前端**: 原生 HTML/CSS/JavaScript

## 快速开始

### 环境要求

- Python 3.7+
- pip

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/你的用户名/zhipu-token-tracker.git
cd zhipu-token-tracker
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **启动应用**

Windows 用户：
```bash
双击运行 `启动Token统计工具.bat`
```

或使用命令行：
```bash
cd token_billing
python app.py
```

4. **访问应用**

打开浏览器访问：http://127.0.0.1:5000

## 使用方法

1. 进入 https://bigmodel.cn/finance-center/bill/expensebill/list
2. 点击费用明细，按天\按明细选择按明细，点击导出数据
3. 在左侧导出记录中下载数据Excel文件
4. 在网页中拖拽或点击上传 Excel 文件
5. 点击「分析数据」按钮
6. 查看按 API Key 分组的 Token 使用统计
7. 可选：导出 CSV 或 Excel 格式的报表

## 数据筛选

工具默认筛选指定的资源包数据进行统计。如需修改筛选条件，请编辑 `app.py` 中的 `TARGET_BUNDLE` 变量。

## 项目结构

```
zhipu-token-tracker/
├── token_billing/
│   ├── app.py              # Flask 后端应用
│   ├── templates/
│   │   └── index.html      # 前端页面模板
│   ├── static/
│   │   └── style.css       # 样式文件
│   └── uploads/            # 文件上传目录
├── requirements.txt        # Python 依赖
├── 启动Token统计工具.bat   # Windows 启动脚本
└── README.md              # 项目说明
```

## 截图
<img width="1619" height="2402" alt="fae1d99daddb86ced527cbea426c7784" src="https://github.com/user-attachments/assets/c0763809-e0a9-44b9-9911-9668b53675ed" />

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
