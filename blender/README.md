# Blender Addon for XtraCrysPy
An import addon for blender that reads in XML files generated by XtraCrysPy for more advanced renderings

Requirements:
- blender 2.80

Installation:
  Either copy the addons folder into your user scripts file in blender (edit/preferences/filepaths/data/scripts),
  or set the user scripts folder location to the blender subfolder in this XtraCrysPy project

### For Developers:
This addon requires the numpy package which should be packaged with Blender's python distribution. In the event that blender is
using the system python, numpy will need to be installed separately. This plugin is tested on blender 2.83 (the latest release
version). Some linux distributions do not have the most up to date version by default, for example, on Ubuntu the snap release
should be used. 