# GEE Server 项目

## 项目概述
本项目通过整合 Google Earth Engine (GEE) 的能力，提供基于 Web 的影像数据查询与下载服务。后端使用 Node.js 与 Express 实现 REST API 和 WebSocket 通信，前端（静态）资源放置于 `public` 目录下。

## 文件结构
- **server.js**: 服务端入口，定义各 API 接口及 WebSocket 下载服务。
- **search_gee_point.py** & **search_gee_bbox.py**: 分别提供基于点和边界框的遥感影像数据搜索功能。
- **download_gee.py**: 根据指定图像 ID 与波段列表下载 GEE 图像数据。
- **download2.py**: 根据指定参数（如数据集、日期、坐标与波段表达式）下载并处理图像数据，同时计算云覆盖率。
- **config.json**: 存储项目配置，如 Earth Engine 项目名称和服务器端口。
- **public/**: 存放下载的影像数据和其他静态资源。

## 环境与依赖
- Node.js 与 npm（安装 Express、body-parser、express-ws 等依赖）
- Python 3.x（安装 ee、geemap 等库）
- Google Earth Engine Python API

## 安装与配置
1. 克隆代码库至本地：
   ```bash
   git clone https://github.com/GISer1909/gee_server.git
   ```
2. 安装 Node.js 依赖：
   ```bash
   npm install
   ```
3. 安装 Python 依赖（建议使用虚拟环境）：
   ```bash
   pip install -r requirements.txt
   ```
4. 修改 `config.json` 文件，配置正确的项目（project）名称和服务器端口。

## 运行服务
启动 Node.js 服务：
```bash
node server.js
```
默认服务运行于 `config.json` 指定端口（如 1337）。

## API 接口说明

### 1. 搜索接口
- **GET /searchByPoint**
  - 参数：`dataset`、`start_date`、`end_date`、`max_cloud_cover`、`latitude`、`longitude`
  - 功能：基于指定地理坐标搜索影像，返回符合条件的影像列表。

- **GET /searchByBbox**
  - 参数：`dataset`、`start_date`、`end_date`、`max_cloud_cover`、`xmin`、`ymin`、`xmax`、`ymax`
  - 功能：基于指定边界框搜索影像数据，返回符合要求的影像列表。

### 2. 下载接口
- **WebSocket /download**
  - 参数（查询字符串）：`image_id`、`bands`
  - 功能：通过 WebSocket 实时传输影像下载日志，下载完成后自动关闭连接，并在特定条件下删除生成的文件。

- **GET /download**
  - 参数（查询字符串）：`image_id`、`bands`
  - 功能：通过 HTTP 响应流方式下载影像，实现服务器推送。

- **POST /download2**
  - 请求体参数：
    - `dataset`: 数据集名称（默认 COPERNICUS/S2_SR_HARMONIZED）
    - `day`: 往前推算的天数（用于计算日期范围）
    - `coord_str`: JSON 格式的坐标字符串，用于定义多边形搜索区域
    - `band_index_exp`: 波段指数表达式（如 `(B8 - B4) / (B8 + B4)`），或使用 `all` 表示下载所有波段
  - 功能：下载指定区域内最新的影像并计算云覆盖率，根据表达式进行波段处理。

## 使用示例
例如，使用 curl 搜索点影像：
```bash
curl "http://localhost:1337/searchByPoint?dataset=COPERNICUS/S2_SR_HARMONIZED&start_date=2023-01-01&end_date=2023-01-31&max_cloud_cover=20&latitude=39.90&longitude=116.40"
```
使用 curl 下载图像：
```bash
curl "http://localhost:1337/download?image_id=COPERNICUS_S2_SR_HARMONIZED_XXXXX&bands=B4,B8"
```
使用 POST 请求下载处理后的影像：
```bash
curl -X POST "http://localhost:1337/download2" -H "Content-Type: application/json" -d '{
    "dataset": "COPERNICUS/S2_SR_HARMONIZED",
    "day": 10,
    "coord_str": "[[[111.3583,39.8671], [111.3622,39.8803], [111.3479,39.8826], [111.3583,39.8671]]]",
    "band_index_exp": "(b(\'B8\') - b(\'B4\')) / (b(\'B8\') + b(\'B4\'))"
}'
```

## 注意事项
- 确保 Earth Engine 已经正确认证并初始化。
- 下载的影像默认保存在 `./public` 目录。
- API 请求若缺少必要参数，将返回错误提示“参数不全”。
- 针对不同数据集，云覆盖率计算可能存在差异。

## 许可证
MIT 许可证

## 联系方式
如有问题，请联系项目维护者。
