import argparse
import ee
import json
ee.Authenticate()

# 添加一个函数来读取JSON文件
def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

# 从JSON文件中获取项目名
project = read_json_file('config.json')['project']

# 使用从JSON文件中获取的项目名初始化Earth Engine
ee.Initialize(project=project)


def search(dataset, xmin, ymin, xmax, ymax, start_date, end_date, max_cloud_cover=None):
    # 定义空间范围
    area = ee.Geometry.Rectangle([xmin, ymin, xmax, ymax])

    # 搜索指定的数据集
    collection = (ee.ImageCollection(dataset)
                  .filterDate(start_date, end_date)
                  .filterBounds(area))
    
    # 如果提供了 max_cloud_cover 参数，添加云覆盖过滤器
    if max_cloud_cover is not None:
        # 判断数据集的名称，根据名称选择不同的云覆盖字段
        if 'COPERNICUS' in dataset:
            cloud_cover_field = 'CLOUDY_PIXEL_PERCENTAGE'
        elif 'LANDSAT' in dataset:
            cloud_cover_field = 'CLOUD_COVER'
        else:
            raise ValueError('Unsupported dataset. The cloud cover field cannot be determined.')
        
        collection = collection.filter(ee.Filter.lt(cloud_cover_field, max_cloud_cover))

    # 获取集合中的图像数
    count = collection.size().getInfo()
    
    # 创建一个空列表来保存结果
    results = []
    
    # 如果集合中有图像，获取每个图像的信息并添加到结果列表中
    if count > 0:
        images = collection.toList(count)
        for i in range(count):
            image = ee.Image(images.get(i))
            info = image.getInfo()
            results.append(info)

    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for GEE scenes.')
    parser.add_argument('--dataset', required=True, help='Dataset to search')
    parser.add_argument('--xmin', type=float, required=True, help='Minimum x coordinate for bounding box')
    parser.add_argument('--ymin', type=float, required=True, help='Minimum y coordinate for bounding box')
    parser.add_argument('--xmax', type=float, required=True, help='Maximum x coordinate for bounding box')
    parser.add_argument('--ymax', type=float, required=True, help='Maximum y coordinate for bounding box')
    parser.add_argument('--start_date', required=True, help='Start date for search')
    parser.add_argument('--end_date', required=True, help='End date for search')
    parser.add_argument('--max_cloud_cover', type=int, required=False, default=None, help='Max cloud cover for search')

    args = parser.parse_args()

    results = search(args.dataset, args.xmin, args.ymin, args.xmax, args.ymax, args.start_date, args.end_date, args.max_cloud_cover)
    print(json.dumps(results, indent=4))
