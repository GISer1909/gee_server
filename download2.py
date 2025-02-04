import argparse
import ee
import json
import geemap
import datetime
from ee.ee_exception import EEException

def load_config(filename='config.json'):
    with open(filename, 'r') as f:
        return json.load(f)

def _authenticate_and_initialize():
    ee.Authenticate()
    config = load_config()
    project = config.get('project', None)
    ee.Initialize(project=project)

def calculate_copernicus_coverage(collection, geom):
    def calculate_coverage(image):
        mask = image.select('MSK_CLDPRB').gt(0)
        mask_pixel_count = mask.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=ee.Geometry(geom),
            scale=20,
            maxPixels=1e9
        ).get('MSK_CLDPRB')
        total_pixel_count = image.reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=ee.Geometry(geom),
            scale=20,
            maxPixels=1e9
        ).get('MSK_CLDPRB')
        coverage = ee.Number(mask_pixel_count).divide(total_pixel_count).multiply(100)
        return image.set('COVERAGE', coverage)
    return collection.map(calculate_coverage).filter(ee.Filter.lt('COVERAGE', 10))

def calculate_landsat_cloud_coverage(collection, geom):
    def calculate_cloud_coverage(image):
        # Bit 3: 云影, Bit 4: 云
        cloud_shadow_bit_mask = (1 << 3)
        clouds_bit_mask = (1 << 4)
        qa = image.select('QA_PIXEL')
        clear_mask = qa.bitwiseAnd(cloud_shadow_bit_mask).eq(0).And(qa.bitwiseAnd(clouds_bit_mask).eq(0))
        cloud_mask = clear_mask.Not()
        cloud_masked_image = cloud_mask.updateMask(cloud_mask)
        cloud_pixels = cloud_masked_image.reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=ee.Geometry(geom),
            scale=30
        ).get('QA_PIXEL')
        total_pixels = image.select('QA_PIXEL').clip(ee.Geometry(geom)).reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=ee.Geometry(geom),
            scale=30
        ).get('QA_PIXEL')
        cloud_pixels = ee.Number(cloud_pixels)
        total_pixels = ee.Number(total_pixels).max(1)
        cloud_coverage = cloud_pixels.divide(total_pixels).multiply(100)
        return image.set('COVERAGE', cloud_coverage)
    return collection.map(calculate_cloud_coverage).filter(ee.Filter.lt('COVERAGE', 10))

def get_image_metadata(image, image_id, geom, image_time, dataset, cloud_coverage):
    data_time = image_time[:10]
    band_names = image.bandNames().getInfo()
    resolutions = [image.select(b).projection().nominalScale().getInfo() for b in band_names]
    resolution = round(min(resolutions), 2)
    return {
        "data_time": data_time,
        "cloud_coverage": cloud_coverage,
        "epsg_code": 4326,
        "resolution": resolution
    }

def main(dataset, day, coord_str, band_index_exp):
    coords = json.loads(coord_str)
    geom = {"type": "Polygon", "coordinates": coords}
    start_date = (datetime.datetime.now() - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
    end_date  = datetime.datetime.now().strftime('%Y-%m-%d')

    try:
        collection = ee.ImageCollection(dataset).filterDate(start_date, end_date).filterBounds(ee.Geometry.Polygon(geom['coordinates']))
        if 'COPERNICUS' in dataset:
            collection = calculate_copernicus_coverage(collection, geom)
        elif 'LANDSAT' in dataset:
            collection = calculate_landsat_cloud_coverage(collection, geom)
        count = collection.size().getInfo()
        if count == 0:
            raise EEException(f'No images found in {dataset} on {start_date} - {end_date}.')
            
        sorted_collection = collection.sort('system:time_start', ascending=False)
        image = sorted_collection.first()
        image_id = image.id().getInfo()
        image_time = datetime.datetime.fromtimestamp(image.get('system:time_start').getInfo() / 1000).strftime('%Y-%m-%d %H:%M:%S')
        cloud_coverage = round(image.get('COVERAGE').getInfo(), 2)
        
        if band_index_exp.lower() != 'all':
            image = image.expression(band_index_exp).rename('Computed')
        image = image.clip(ee.Geometry(geom))
    
        metadata = get_image_metadata(image, image_id, geom, image_time, dataset, cloud_coverage)
        geemap.download_ee_image(image, './public/' + image_id + '.tif', crs="EPSG:4326")
        print(metadata)
        
    except EEException as e:
        print(f'download2.py_Error: {e}')

if __name__ == "__main__":
    _authenticate_and_initialize()
    parser = argparse.ArgumentParser(description='Download GEE data.')
    parser.add_argument('--dataset', type=str, required=False, default='COPERNICUS/S2_SR_HARMONIZED', help='Dataset to download')
    parser.add_argument('--day', type=int, required=False, default=10, help='Day to download')
    parser.add_argument('--coord_str', type=str, required=False, default='[[[111.35831543956, 39.8671275634262], [111.358937702161, 39.8689875175398], [111.358797051329, 39.8716487997008], [111.365806666084, 39.8738835154638], [111.364633078833, 39.8763189523132], [111.364237284723, 39.877778785389], [111.36324486668, 39.8784940493233], [111.362859753993, 39.8796368068499], [111.362220157022, 39.8802600913505], [111.362076156088, 39.8806824356203], [111.361277952929, 39.8817543608664], [111.360355032998, 39.8824484312489], [111.358912926101, 39.8831012640554], [111.358655771769, 39.8831471942829], [111.358188849737, 39.884443213895], [111.353129837415, 39.8848051793372], [111.35136935008, 39.8826928270647], [111.351347910138, 39.8825730098227], [111.350289484959, 39.882585776391], [111.347957991853, 39.8825622786425], [111.346862994375, 39.8825684194668], [111.346728930823, 39.8825751913166], [111.346087680524, 39.8827806343287], [111.344409879303, 39.8835536958667], [111.34101489772, 39.8848317958111], [111.339187868058, 39.8847075580033], [111.337999548726, 39.883218803176], [111.334780931732, 39.8786075606531], [111.328772392766, 39.871933498297], [111.332565177057, 39.8704058236868], [111.334679840579, 39.8705050623781], [111.33507792373, 39.870756459968], [111.338272766194, 39.8707838583978], [111.3384623729, 39.8709568826799], [111.339225552907, 39.870865095805], [111.340388150566, 39.8712715303344], [111.341731579943, 39.8704232965403], [111.342744342548, 39.8686743024295], [111.348231890393, 39.8684352627528], [111.348423265983, 39.8671808805042], [111.35831543956, 39.8671275634262]]]', help='Coordinate string to download')
    parser.add_argument('--band_index_exp', type=str, required=False, default='(b("B8") - b("B4")) / (b("B8") + b("B4"))', help='Band index expression')
    
    args = parser.parse_args()
    
    main(args.dataset, args.day, args.coord_str, args.band_index_exp)

#  python download2.py --dataset 'LANDSAT/LC08/C02/T2_L2' --band_index_exp 'all' --day 30