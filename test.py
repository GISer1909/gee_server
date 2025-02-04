import ee
import json
ee.Authenticate()

# 添加一个函数来读取JSON文件
def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

ee.Authenticate()
# 从JSON文件中获取项目名
project = read_json_file('config.json')['project']

# 使用从JSON文件中获取的项目名初始化Earth Engine
ee.Initialize(project=project)

#搜索指定的数据集
info = ee.ImageCollection('COPERNICUS/S2_HARMONIZED').filterDate('2020-01-01', '2020-12-31').filterBounds(ee.Geometry.Point(116.38, 39.92)).size().getInfo()
print(info)


