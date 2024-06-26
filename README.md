# GEE数据查询和下载API文档

本文档提供了GEE数据查询和下载API的详细信息和使用方法。

## API概述

本API提供了以下功能：

- 根据指定的数据集、日期范围、云覆盖度和地理位置，查询GEE中的影像数据。
- 根据影像ID和指定的波段，下载GEE中的影像数据。

请注意，本API仅支持LANDSAT和COPERNICUS系列数据。

## API接口

### 1. 查询接口

#### 1.1 根据点坐标查询GEE数据

##### 请求URL：

- `/searchByPoint`

##### 请求方式：

GET

##### 参数：

| 参数名          | 必选 | 类型   | 说明                                                        |
| --------------- | ---- | ------ | ----------------------------------------------------------- |
| dataset         | 是   | string | 要查询的数据集名称。目前仅支持LANDSAT和COPERNICUS系列数据。 |
| start_date      | 是   | string | 查询的开始日期，格式为"YYYY-MM-DD"。                        |
| end_date        | 是   | string | 查询的结束日期，格式为"YYYY-MM-DD"。                        |
| max_cloud_cover | 否   | int    | 查询的最大云覆盖度，取值范围为0-100。                       |
| latitude        | 是   | float  | 查询点的纬度。                                              |
| longitude       | 是   | float  | 查询点的经度。                                              |

#### 1.2 根据边界框坐标查询GEE数据

##### 请求URL：

- `/searchByBbox`

##### 请求方式：

GET

##### 参数：

| 参数名          | 必选 | 类型   | 说明                                                        |
| --------------- | ---- | ------ | ----------------------------------------------------------- |
| dataset         | 是   | string | 要查询的数据集名称。目前仅支持LANDSAT和COPERNICUS系列数据。 |
| start_date      | 是   | string | 查询的开始日期，格式为"YYYY-MM-DD"。                        |
| end_date        | 是   | string | 查询的结束日期，格式为"YYYY-MM-DD"。                        |
| max_cloud_cover | 否   | int    | 查询的最大云覆盖度，取值范围为0-100。                       |
| xmin            | 是   | float  | 查询边界框的最小x坐标。                                     |
| ymin            | 是   | float  | 查询边界框的最小y坐标。                                     |
| xmax            | 是   | float  | 查询边界框的最大x坐标。                                     |
| ymax            | 是   | float  | 查询边界框的最大y坐标。                                     |

#### 返回示例：

```json
{
    "code": 200,
    "message": "查询成功",
    "data": [
        {
            "type": "Image",
            "bands": [...],
            "id": "COPERNICUS/S2/20190603T022559_20190603T024403_T49QFE",
            "version": 1561434784303000,
            "properties": {...}
        },
        ...
    ]
}
```

### 2. 下载接口

#### 2.1 下载GEE数据（WebSocket接口）

##### 请求URL：

- `/download`

##### 请求方式：

WebSocket

##### 参数：

| 参数名   | 必选 | 类型   | 说明                           |
| -------- | ---- | ------ | ------------------------------ |
| image_id | 是   | string | 要下载的影像ID。               |
| bands    | 否   | string | 要下载的影像波段，用逗号分隔。 |

在请求完成后，将在服务器的指定目录下生成下载的影像文件。

##### 注意事项：

如果WebSocket连接被关闭，且返回的关闭代码为4999，那么将取消下载，并删除已下载的文件。

#### 2.2 下载GEE数据（HTTP接口）

##### 请求URL：

- `/download`

##### 请求方式：

GET

##### 参数：

| 参数名   | 必选 | 类型   | 说明                           |
| -------- | ---- | ------ | ------------------------------ |
| image_id | 是   | string | 要下载的影像ID。               |
| bands    | 否   | string | 要下载的影像波段，用逗号分隔。 |

在请求完成后，将在服务器的指定目录下生成下载的影像文件。

### 3. 从服务器下载文件接口

#### 请求URL：

- `/{image_id}.tif?t={timestamp}`

其中，`{image_id}`需要将影像ID中的`/`替换为`_`，`{timestamp}`是当前时间戳。

#### 请求方式：

GET

#### 返回：

下载指定影像ID的文件。

## 注意事项

- 查询接口中的日期参数需遵循"YYYY-MM-DD"的格式。
- 查询接口中的云覆盖度参数需在0-100之间。
- 查询接口中的经纬度参数需在合理的范围内，即纬度在-90到90之间，经度在-180到180之间。
- 下载接口中的影像ID需为存在的影像ID。
- 下载接口中的波段需为存在的波段，多个波段用逗号分隔。