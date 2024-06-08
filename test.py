import ee
import geemap

# 身份验证和初始化
ee.Authenticate()
ee.Initialize(project='ee-cbxgjs')

# 影像ID
image_id = 'MODIS/061/MOD13Q1/2023_05_09'

# 加载影像
image = ee.Image(image_id)

# 选择NDVI波段
ndvi = image.select('NDVI')

# 限定区域
region = ee.Geometry.Rectangle([119.55677149836102, 44.73028615293674, 122.05216665668421, 46.45218297432774])

# 裁剪影像到限定区域
clipped_ndvi = ndvi.clip(region)

# 获取NDVI的最小值和最大值
ndvi_min = clipped_ndvi.reduceRegion(
    reducer=ee.Reducer.min(), 
    geometry=region, 
    scale=250, 
    bestEffort=True
).get('NDVI')

ndvi_max = clipped_ndvi.reduceRegion(
    reducer=ee.Reducer.max(), 
    geometry=region, 
    scale=250, 
    bestEffort=True
).get('NDVI')

# 计算VFC
vfc = clipped_ndvi.subtract(ee.Number(ndvi_min)).divide(ee.Number(ndvi_max).subtract(ee.Number(ndvi_min)))

# 计算c值的表达式
def calculate_c(image):
    return image.expression(
        'VFC == 0 ? 1 : (VFC >= 0.783 ? 0 : 0.6508 - 0.3436 * log(VFC))',
        {'VFC': image}
    )

c = calculate_c(vfc)

# 将影像重新投影到WGS84
c_wgs84 = c.reproject(crs='EPSG:4326', scale=250)

# 设置颜色映射
# c_vis = {
#     'min': 0,
#     'max': 1,
#     'palette': ['darkgreen', 'green', 'lightgreen', 'white']
# }

# 应用颜色映射
# c_colored = c_wgs84.visualize(**c_vis)

# 下载带颜色的影像为GeoTIFF
out_dir = './'  # 替换为你的输出目录
out_file = f'{out_dir}/vfc_calculation_colored.tif'
geemap.ee_export_image(c_wgs84, filename=out_file, scale=250, region=region, file_per_band=False)

print('下载完成:', out_file)
