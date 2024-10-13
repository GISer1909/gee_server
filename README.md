# Google Earth Engine Data Download API

本项目是一个基于 Node.js 的 API，旨在通过 Google Earth Engine (GEE) 下载遥感数据。项目包含多个 API 路由，用于根据坐标点和包围盒搜索图像，以及根据图像 ID 下载图像。

## 特性

- 支持通过点坐标和包围盒搜索指定时间范围内的遥感图像。
- 提供 WebSocket 支持，允许用户通过连接实时下载数据。
- 下载时支持指定波段，用户可以根据需求选择特定波段下载。
- 支持将 GEE 的结果以 JSON 格式返回，便于前端处理。

## 安装

确保您已安装 Node.js 和 Python（推荐版本为 Python 3.6 及以上）。

1. **克隆项目**

   ```bash
   git clone https://github.com/GISer1909/gee_server.git
   cd gee_server
   ```

2. **安装依赖**

   ```bash
   npm install
   ```

3. **安装 Python 依赖**

   确保您已安装 `earthengine-api` 和 `geemap`：

   ```bash
   pip install -r requirements.txt
   ```

4. **配置项目**

   在项目根目录下创建一个 `config.json` 文件，并添加您的 GEE 项目信息：

   ```json
   {
       "project": "your-google-earth-engine-project-id",
       "port": 1337
   }
   ```

## 使用

1. **启动服务器**

   ```bash
   node index.js
   ```

   服务器启动后，您会在控制台看到：

   ```
   Server is running on port 1337
   ```

2. **API 路由**

   - **根路由**

     - `GET /`：返回服务器运行状态。

   - **点搜索**

     - `GET /searchByPoint`：通过点坐标搜索图像。

       **请求参数**：

       - `dataset`：数据集名称
       - `latitude`：纬度
       - `longitude`：经度
       - `start_date`：开始日期（格式：YYYY-MM-DD）
       - `end_date`：结束日期（格式：YYYY-MM-DD）
       - `max_cloud_cover`：最大云覆盖率（可选）

   - **包围盒搜索**

     - `GET /searchByBbox`：通过包围盒搜索图像。

       **请求参数**：

       - `dataset`：数据集名称
       - `xmin`：最小经度
       - `ymin`：最小纬度
       - `xmax`：最大经度
       - `ymax`：最大纬度
       - `start_date`：开始日期（格式：YYYY-MM-DD）
       - `end_date`：结束日期（格式：YYYY-MM-DD）
       - `max_cloud_cover`：最大云覆盖率（可选）

   - **下载图像**

     - **WebSocket 下载**：通过 WebSocket 连接下载图像。

       - `GET /download?image_id=<image_id>&bands=<band_list>`：实时下载指定图像 ID 的波段。

     - **HTTP 下载**：通过 HTTP 请求下载图像。

       - `GET /download?image_id=<image_id>&bands=<band_list>`：下载指定图像 ID 的波段。

   - **高级下载**

     - `POST /download2`：通过指定数据集、日期和坐标字符串下载图像。

       **请求体**：

       ```json
       {
           "dataset": "your-dataset-name",
           "day": 5,
           "coord_str": "[[[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin], [xmin, ymin]]]",
           "band_index_exp": "your-band-index-expression"  // 可选
       }
       ```

## 注意事项

- 确保在使用 GEE API 时遵循相关的使用政策。
- 由于图像数据下载可能会受到网络和 GEE 处理速度的影响，建议在使用前做好相应的错误处理。
- 可以运行test.py检查是否正确登录GEE。

## 贡献

欢迎提出问题或提交 Pull Request。请在提交之前确保遵循项目的贡献指南。

## 许可证

本项目使用 MIT 许可证，详细信息请查看 [LICENSE](LICENSE) 文件。
