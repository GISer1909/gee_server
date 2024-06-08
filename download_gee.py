import argparse
import ee
import json
import geemap
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

default_output_dir = './public'

def main(image_id, output_dir, bands):
    try:
        # 获取图像
        image = ee.Image(image_id)
        # if image does not exist,
        if image is None:
            print(f'Image {image_id} not found.')
            # throw an exception
            raise ValueError(f'Image {image_id} not found.')

        # 如果提供了波段列表，选择指定的波段
        if bands:
            image = image.select(bands)

        # 下载图像
        file_name = image_id.replace('/', '_')
        geemap.download_ee_image(image, output_dir +'/' + file_name + '.tif')
    except Exception as e:
        print(f"download_gee_Error: {e}")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Download GEE data.')
        parser.add_argument('--image_id', type=str, required=True, help='Image ID to download')
        parser.add_argument('--output_dir', type=str, default=default_output_dir, help='Output directory for downloaded data')
        parser.add_argument('--bands', type=lambda s: s.split(','), default=None, help='Comma-separated list of bands to download')
        
        args = parser.parse_args()
        main(args.image_id, args.output_dir, args.bands)
    except Exception as e:
        print(f"download_gee_Error: {e}")
