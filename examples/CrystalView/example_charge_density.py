from XtraCrysPy import XCP_Atoms,Model
from XtraCrysPy.file_io import read_datablocks_XSF

if '__main__' == __name__:

  a_info = {'colors':{'Si':(0,.2,1)}, 'bonds':{'Si_Si':6.5}}

  fname = 'data_files/Si.scf.in'
  xcp = XCP_Atoms.XCP_Atoms(model=fname, params=a_info, nsc=(2,2,2))

  density_file = 'data_files/Si.density_0.xsf'
  data = read_datablocks_XSF(density_file)

  xcp.render_iso_surface(data[0], iso_vals=.000075)
  xcp.start_crystal_view()
