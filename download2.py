import argparse
import ee
import json
import geemap
import datetime
from ee.ee_exception import EEException


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

def get_image_metadata(image, image_id, geom,image_time):
    # 假设的一些字段值
    product_name = image_id+'_'+str(int(datetime.datetime.now().timestamp()))
    band_info =str(','.join([band['id'] for band in image.getInfo()['bands']]))
    projection_crs = image.getInfo()['bands'][0]['crs']
    geographic_crs  = 'EPSG:4326'
    spatial_coverage = geom
    data_source = "Google Earth Engine"
    image_path = './public/' + image_id + '.tif'
    epsg_code = image.getInfo()['bands'][0]['crs'].split(':')[1]
 

    metadata = {
        "product_name": product_name,
        "band_info": band_info,
        "acquisition_time": image_time,
        "projection_crs": projection_crs,
        "geographic_crs": geographic_crs,
        "spatial_coverage": spatial_coverage,
        "data_source": data_source,
        "image_path": image_path,
        "epsg_code": epsg_code,
    }

    return metadata

def main(dataset, day, coord_str, band_index_exp):
    # 解析坐标字符串
    coords = json.loads(coord_str)
    # 构造geom对象
    geom = {"type": "Polygon", "coordinates": coords}
    #当前本地日期-5天
    start_date = (datetime.datetime.now() - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
    #当前本地日期
    end_date  = datetime.datetime.now().strftime('%Y-%m-%d')

    try:
        collection = ee.ImageCollection(dataset).filterDate(start_date, end_date).filterBounds(ee.Geometry.Polygon(geom['coordinates']))
        if 'COPERNICUS' in dataset:
            cloud_cover_field = 'CLOUDY_PIXEL_PERCENTAGE'
        elif 'LANDSAT' in dataset:
            cloud_cover_field = 'CLOUD_COVER'
        collection = collection.filter(ee.Filter.lt(cloud_cover_field, 25))   
        #获取集合中的图像数
        count = collection.size().getInfo()
        if count == 0:
            #EEException
            raise EEException(f'No images found in {dataset} on {start_date} - {end_date}.')
        image = collection.sort('system:time_start',ascending = False).first()
        image_id = image.id().getInfo()
        
        image_time = datetime.datetime.fromtimestamp(image.get('system:time_start').getInfo() / 1000).strftime('%Y-%m-%d %H:%M:%S')
        if band_index_exp:
            image = image.expression(band_index_exp).rename('Computed')
        image = image.clip(ee.Geometry(geom))
    
        
 

      

        metadata = get_image_metadata(image, image_id, geom,image_time)
        geemap.download_ee_image(image, './public/' + metadata['product_name']
                                  + '.tif')
        print(metadata)
        
    except EEException as e:
        print(f'download2.py_Error: {e}')
        return



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download GEE data.')
    parser.add_argument('--dataset', type=str, required=True, help='Dataset to download')
    parser.add_argument('--day', type=int, required=True, help='Day to download')
    parser.add_argument('--coord_str', type=str, required=True, help='Coordinate string to download')
    parser.add_argument('--band_index_exp', type=str, required=False, help='Band index expression')
    
    args = parser.parse_args()
    
    main(args.dataset, args.day, args.coord_str, args.band_index_exp)

#  python d.py --dataset 'COPERNICUS/S2_SR_HARMONIZED' --day 10 --coord_str '[[[111.35831543956, 39.8671275634262], [111.358937702161, 39.8689875175398], [111.358797051329, 39.8716487997008], [111.365806666084, 39.8738835154638], [111.364633078833, 39.8763189523132], [111.364237284723, 39.877778785389], [111.36324486668, 39.8784940493233], [111.362859753993, 39.8796368068499], [111.362220157022, 39.8802600913505], [111.362076156088, 39.8806824356203], [111.361277952929, 39.8817543608664], [111.360355032998, 39.8824484312489], [111.358912926101, 39.8831012640554], [111.358655771769, 39.8831471942829], [111.358188849737, 39.884443213895], [111.353129837415, 39.8848051793372], [111.35136935008, 39.8826928270647], [111.351347910138, 39.8825730098227], [111.350289484959, 39.882585776391], [111.347957991853, 39.8825622786425], [111.346862994375, 39.8825684194668], [111.346728930823, 39.8825751913166], [111.346087680524, 39.8827806343287], [111.344409879303, 39.8835536958667], [111.34101489772, 39.8848317958111], [111.339187868058, 39.8847075580033], [111.337999548726, 39.883218803176], [111.334780931732, 39.8786075606531], [111.328772392766, 39.871933498297], [111.332565177057, 39.8704058236868], [111.334679840579, 39.8705050623781], [111.33507792373, 39.870756459968], [111.338272766194, 39.8707838583978], [111.3384623729, 39.8709568826799], [111.339225552907, 39.870865095805], [111.340388150566, 39.8712715303344], [111.341731579943, 39.8704232965403], [111.342744342548, 39.8686743024295], [111.348231890393, 39.8684352627528], [111.348423265983, 39.8671808805042], [111.35831543956, 39.8671275634262]]]' --band_index_exp '(b(\"B8\") - b(\"B4\")) / (b(\"B8\") + b(\"B4\"))'