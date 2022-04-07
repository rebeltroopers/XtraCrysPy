from XtraCrysPy.XCP_Atoms import XCP_Atoms as XCP

if '__main__' == __name__:

  a_info = {'bonds':6.1}
  xcp = XCP(params=a_info, model='data_files/Si46.scf.in', sel_type='Chain')
  xcp.start_crystal_view()

