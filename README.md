# 天天基金分析系统

天天基金理财相关代码，数据获取、数据分析、投资建议、理财分析。

## 项目简介

这是一个完整的基金分析系统，包含以下功能：

1. **后台数据库** - 存储基金数据，支持每日自动更新
2. **前端可视化** - Web界面展示基金数据和分析结果
3. **量化策略** - 多种交易策略分析和回测功能

## 系统架构

```
tiantianjijin/
├── backend/                 # 后端代码
│   ├── models/             # 数据模型
│   │   └── database.py     # 数据库模型定义
│   ├── scrapers/           # 数据爬虫
│   │   └── fund_scraper.py # 基金数据爬取
│   ├── strategies/         # 量化策略
│   │   └── trading_strategies.py # 交易策略
│   └── update_data.py      # 数据更新调度器
├── frontend/               # 前端代码
│   ├── templates/          # HTML模板
│   │   └── index.html      # 主页面
│   └── static/             # 静态资源
│       ├── css/
│       │   └── style.css   # 样式表
│       └── js/
│           └── main.js     # JavaScript
├── data/                   # 数据存储目录
├── app.py                  # Flask Web应用
├── init_system.py          # 系统初始化脚本
└── requirements.txt        # Python依赖

```

## 功能特性

### 1. 数据管理
- ✅ 基金基本信息存储
- ✅ 历史净值数据
- ✅ 业绩指标统计
- ✅ 每日自动更新

### 2. 可视化分析
- ✅ 基金搜索和查询
- ✅ 净值走势图表
- ✅ 业绩排行榜
- ✅ 多维度数据对比

### 3. 量化策略
- ✅ 移动平均线策略
- ✅ 动量策略
- ✅ 价值策略
- ✅ 策略回测功能
- ✅ 综合信号分析

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化系统

```bash
python init_system.py
```

这将：
- 创建数据库
- 加载初始基金数据
- 获取历史数据

### 3. 启动Web服务

```bash
python app.py
```

访问 http://localhost:5000 查看系统

### 4. 数据更新

#### 一次性更新
```bash
python backend/update_data.py
```

#### 定时更新（推荐）
系统会在每天18:00自动更新数据：

```bash
# 在后台运行
nohup python backend/update_data.py &
```

或使用系统cron：
```bash
# 添加到crontab
0 18 * * * cd /path/to/tiantianjijin && python backend/update_data.py
```

## API接口

系统提供以下REST API：

- `GET /api/funds` - 获取所有基金列表
- `GET /api/fund/<code>` - 获取基金详情
- `GET /api/fund/<code>/values` - 获取历史净值
- `GET /api/fund/<code>/performance` - 获取业绩指标
- `GET /api/fund/<code>/analysis` - 获取量化分析
- `GET /api/fund/<code>/backtest` - 获取回测结果
- `GET /api/top-performers` - 获取业绩排行

## 技术栈

- **后端**: Python 3.12, Flask, SQLAlchemy
- **数据库**: SQLite
- **数据分析**: Pandas, NumPy, Scikit-learn
- **可视化**: Plotly, Matplotlib
- **前端**: HTML, CSS, JavaScript

## 量化策略说明

### 移动平均线策略 (Moving Average)
基于短期和长期移动平均线的交叉信号：
- 金叉（短期MA上穿长期MA）：买入信号
- 死叉（短期MA下穿长期MA）：卖出信号

### 动量策略 (Momentum)
基于价格趋势的策略：
- 正动量：价格持续上涨，买入信号
- 负动量：价格持续下跌，卖出信号

### 价值策略 (Value)
基于估值的策略：
- 低估：买入信号
- 高估：卖出信号

## 注意事项

⚠️ **风险提示**
- 本系统仅供学习和研究使用
- 所有数据和策略建议仅供参考
- 投资有风险，决策需谨慎
- 实际投资请咨询专业理财顾问

## 开发计划

- [ ] 增加更多数据源
- [ ] 实现AI模型预测
- [ ] 添加实时数据推送
- [ ] 增强回测功能
- [ ] 添加用户系统

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
