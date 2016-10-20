import os

from osgeo import gdal
from osgeo import osr
import TileStache
from notebook.base.handlers import IPythonHandler


def mapnik_config(layer_name, file_path, layer_srs):
    """ Creates a mapnik config file
    file_path is the absolute path to
    the geotiff file """

    return """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE Map[]>
<Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over" font-directory="./fonts">
<Style name="raster-style">
  <Rule>
    <RasterSymbolizer>
      <RasterColorizer default-mode="linear" default-color="white" epsilon="0.001">
        <stop color="#a6611a" value = "0" />
        <stop color="#dfc27d" value = "25" />
        <stop color="#f5f5f5" value = "100" />
        <stop color="#80cdc1" value = "175"/>
        <stop color="#018571" value = "250"/>
      </RasterColorizer>
    </RasterSymbolizer>
  </Rule>
</Style>
<Layer name="{}" status="on" srs="{}">
<StyleName>raster-style</StyleName>
<Datasource>
    <Parameter name="type">gdal</Parameter>
    <Parameter name="file">{}</Parameter>
    <Parameter name="format">tiff</Parameter>
    <Parameter name="band">4</Parameter>
</Datasource>
</Layer>
</Map>
""".format(layer_name, layer_srs, file_path)

def get_config(layer_name, file_path, layer_srs):

    mapnik_conf = mapnik_config(layer_name, file_path, layer_srs)
    config = {
        "cache": {
            "name": "Test",
            "path": "/tmp/stache",
            "umask": "0000"
        },
        "layers": {
            "{}".format(layer_name): {
                "provider": {"name": "mapnik", "mapconfig": mapnik_conf},
                "projection": "spherical mercator"
            }
        }
    }

    return TileStache.parseConfig(config)


class TileServerHandler(IPythonHandler):
    def get(self):

        file_path = "/home/dorukozturk/Desktop/Tasks/NBAR/L57.Globe.month02.2009.hh09vv04.h6v1.doy032to055.NBAR.v3.0.tiff"
        raster = gdal.Open(file_path)
        srs = osr.SpatialReference()
        srs.ImportFromWkt(raster.GetProjectionRef())
        layer_srs = srs.ExportToProj4()

        components = [x for x in self.request.path.split("/") if x]
        layer_name, z, x, y = components
        config = get_config(layer_name, file_path, layer_srs)
        layer = config.layers
        status_code, headers, content = TileStache.requestHandler2(config, self.request.path)

        # Get the header
        header = headers.items()[0]

        # Tornado syntax for passing headers
        self.set_header(header[0], header[1])
        self.write(content)
