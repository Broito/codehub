from osgeo import gdal, gdalconst
import os

# 获取指定路径下所有指定后缀的文件
# dir 指定路径
# ext 指定后缀，链表&不需要带点 或者不指定。例子：['xml', 'java']
def GetFileFromThisRootDir(dir,ext = None):
  allfiles = []
  needExtFilter = (ext != None)
  for root,dirs,files in os.walk(dir):
    for filespath in files:
      filepath = os.path.join(root, filespath)
      extension = os.path.splitext(filepath)[1][1:]
      if needExtFilter and extension in ext:
        allfiles.append(filepath)
      elif not needExtFilter:
        allfiles.append(filepath)
  return allfiles

raster_paths = GetFileFromThisRootDir(r'I:\DataHub\Landcover_gallery\GISD30\GISD30_1985_2020_E65_E150','tif')
raster_objs = []
for raster in raster_paths:
    raster_obj = gdal.Open(raster, gdal.GA_ReadOnly)
    raster_objs.append(raster_obj)

proj = raster_obj.GetProjection()
output_raster = r'I:\DataHub\Landcover_gallery\GISD30\GISD30_1985-2020_E65_E150.tif'
options=gdal.WarpOptions(srcSRS=proj, dstSRS=proj,format='GTiff',resampleAlg=gdalconst.GRA_Bilinear)
gdal.Warp(output_raster,raster_objs,options=options)






















