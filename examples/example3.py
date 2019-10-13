from XCrysPy import XCrysPy as XCP

if '__main__' == __name__:

  # 2D SnTe with colors red & blue for Sn & Te respectively.
  # Bonds are drawn between Sn & Te atoms if they are closer together than 8 angstrom
  cpy = XCP.XCrysPy(qe_fname='SnTe_data/SnTe.scf.in', spec_col={'Sn':(1,0,0), 'Te':(0,0,1)})
  cpy.draw_cell(nx=3, ny=3, nz=1, boundary=False)
  cpy.draw_bonds(dist={'Sn_Te':8.})