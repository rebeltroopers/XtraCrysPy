from fury.utils import colors_from_actor,update_actor,vertices_from_actor
from .XtraCrysPy import XtraCrysPy
import numpy as np

class XCP_Atoms ( XtraCrysPy ):

  def __init__ ( self, size=(1024, 1024), axes=True, perspective=False, model=None, params={}, relax=False, nsc=(1,1,1), bond_type='stick', sel_type='chain' ):
    from .Model import Model
    super().__init__(size, axes, perspective)

    self.nsc = nsc
    self.units = 'bohr'
    self.runits = 'degree'
    self.sel_forward = True
    self.sel_type = sel_type
    self.bond_type = bond_type

    self.sel_inds = []
    self.sel_cols = []
    self.sel_bnds = []
    self.scolor = np.array((0,210,210))

    if model is not None:
      if isinstance(model, Model):
        pass
      elif isinstance(model, str):
        from os.path import isfile
        if not isfile(model):
          raise FileNotFoundError('File {} not found'.format(model))
        model = Model(params, fname=model, relax=relax)
      else:
        raise TypeError('Argument \'model\' must be a file name or a Model object.')
    elif params:
      model = Model(params, fname=None, relax=relax)
    else:
      raise Exception('Must specify model or params arguments')

    self.model = model
    self.relax = relax
    self.relax_index = 0
    self.nrelax = self.model.atoms.shape[0]
    if relax:
      from fury import ui
      from fury.data import read_viz_icons

      left_icon = [('left',read_viz_icons(fname='circle-left.png'))]
      left_button = ui.Button2D(icon_fnames=left_icon, size=(50,50))
      left_button.on_left_mouse_button_clicked = self.relax_backward

      right_icon = [('right',read_viz_icons(fname='circle-right.png'))]
      right_button = ui.Button2D(icon_fnames=right_icon, size=(50,50))
      right_button.on_left_mouse_button_clicked = self.relax_forward

      self.relax_panel = ui.Panel2D((110,50), (size[0]-120,size[1]-60), (0,0,0))
      self.relax_panel.add_element(left_button, (0,0))
      self.relax_panel.add_element(right_button, (60,0))
      self.scene.add(self.relax_panel)
      # Setup buttons
      pass

    self.render_atomic_model()


  def update_buttons ( self, caller, event ):
    super().update_buttons(caller, event)
    x,y = self.scene.GetSize()
    self.relax_panel.position = (x-120, y-60)


  def angle ( self, ai0, ai1, ai2 ):
    from numpy.linalg import norm

    v1 = self.aposs[ai0] - self.aposs[ai1]
    v2 = self.aposs[ai2] - self.aposs[ai1]
    conv = 1 if self.runits == 'radian' else 180/np.pi
    return conv * np.arccos((v1.dot(v2))/(norm(v1)*norm(v2)))


  def distance ( self, ai1, ai2 ):
    dist = np.sqrt(np.sum((self.aposs[ai2]-self.aposs[ai1])**2))
    if self.units == 'angstrom':
      from .conversion import BOHR_ANG
      dist *= BOHR_ANG
    else:
      pass # Bohr
    return dist


  def set_atom_color ( self, mem, index, nvert, col ):
    for i in range(index*nvert, (index+1)*nvert):
      mem[i] = np.array(col)


  def pop_sbond ( self, ind=-1 ):
    tbond = self.sel_bnds.pop(ind)
    self.scene.rm(tbond)


  def push_sbond ( self ):
    from fury import actor

    if self.sel_forward:
      ai1,ai2 = self.sel_inds[-2:]
    else:
      ai1,ai2 = self.sel_inds[:2]
      
    conn = self.aposs[ai1] - self.aposs[ai2]
    dist = np.linalg.norm(conn)
    cent = (self.aposs[ai1] + self.aposs[ai2]) / 2

    if self.bond_type == 'stick':
      brad = 0.01 + 1 / (4 * dist)
    elif self.bond_type == 'primary':
      prad = np.min([r for k,r in self.model.radii.items()])
      brad = 0.01 + 1.5 * prad / (2 * dist)
    tbond = actor.cylinder([cent], [conn], [self.scolor/255], radius=brad, heights=dist, resolution=20)

    self.scene.add(tbond)
    if self.sel_forward:
      self.sel_bnds.append(tbond)
    else:
      self.sel_bnds.insert(0, tbond)


  def pop_atom ( self, mem, index, nvert ):
    aind = self.sel_inds.index(index)
    self.sel_inds.pop(aind)
    col = self.sel_cols.pop(aind)
    self.set_atom_color(mem, index, nvert, col)


  def push_atom ( self, mem, index, nvert ):
    if index == -1:
      return False
    if self.sel_forward:
      self.sel_inds.append(index)
    else:
      self.sel_inds.insert(0, index)
    self.sel_cols.append(mem[index*nvert].copy())
    self.set_atom_color(mem, index, nvert, self.scolor)
    return True


  def selection_logic ( self, colors, index, nvert ):

    if index in self.sel_inds:
      nsi = len(self.sel_inds)
      sind = self.sel_inds.index(index)
      npop = nsi - sind

      if nsi == 1:
        self.pop_atom(colors, self.sel_inds[0], nvert)
      elif nsi == 2:
        self.pop_atom(colors, index, nvert)
        self.pop_sbond()
      else:
        mid = nsi - sind - 1
        if mid >= nsi-mid:
          rng = (0, sind+1)
          self.sel_forward = False
        else:
          rng = (sind, nsi)
          self.sel_forward = True
        for _ in range(rng[0], rng[1]):
          self.pop_atom(colors, self.sel_inds[rng[0]], nvert)
          if rng[0] == 0:
            self.pop_sbond(ind=rng[0])
          else:
            self.pop_sbond(ind=rng[0]-1)

    else:
      if self.sel_type == 'info':
        self.push_atom(colors, index, nvert)

      elif self.sel_type == 'distance':
        if len(self.sel_inds) == 0:
          self.push_atom(colors, index, nvert)
        elif len(self.sel_inds) == 1:
          if self.push_atom(colors, index, nvert):
            self.push_sbond()
            dist = self.distance(*self.sel_inds)
            print('Distance between atoms {} and {}:'.format(*self.sel_inds))
            print('{} {}\n'.format(self.distance(*self.sel_inds),self.units))

      elif self.sel_type == 'angle':
        if len(self.sel_inds) == 0:
          self.push_atom(colors, index, nvert)
        elif len(self.sel_inds) in [1,2]:
          if self.push_atom(colors, index, nvert):
            self.push_sbond()
            if len(self.sel_inds) == 3:
              print('Angle between atoms {}, {}, and {}:'.format(*self.sel_inds))
              print('{} {}\n'.format(self.angle(*self.sel_inds),self.runits))

      elif self.sel_type == 'chain':
        if self.push_atom(colors, index, nvert) and len(self.sel_inds) > 1:
          self.push_sbond()


  def relax_forward ( self, iren, obj, event ):
    if self.relax_index < self.nrelax-1:
      self.relax_index += 1
      self.update_atomic_model()


  def relax_backward ( self, iren, obj, event ):
    if self.relax_index > 0:
      self.relax_index -= 1
      self.update_atomic_model()


  def pick_atom ( self, obj, event ):

    pos = self.picker.event_position(self.smanager.iren)
    pinfo = self.picker.pick(pos, self.smanager.scene)

    vertices = vertices_from_actor(obj)
    colors = colors_from_actor(obj, 'colors')

    nvert = int(vertices.shape[0]/self.natoms)
    index = int(np.floor(pinfo['vertex']/nvert))

    self.selection_logic(colors, index, nvert)

    update_actor(obj)


  def update_atomic_model ( self ):
    from fury.utils import update_actor

    self.scene.rm(self.frame)
    self.scene.rm(self.atoms)
    for b in self.bonds:
      self.scene.rm(b)
    for b in self.sel_bnds:
      self.scene.rm(b)

    self.render_atomic_model()

    self.sel_forward = True
    sel_inds = self.sel_inds.copy()
    colors = colors_from_actor(self.atoms, 'colors')
    nvert = int(vertices_from_actor(self.atoms).shape[0]/self.natoms)

    self.sel_inds = []
    self.sel_cols = []
    self.sel_bnds = []
    for ind in sel_inds:
      self.selection_logic(colors, ind, nvert)

    self.smanager.render()


  def render_atomic_model ( self ):
    '''
    '''
    from fury import actor
    import numpy as np


    if self.model.units != self.units:
      self.units = model.units

    ainfo,binfo,linfo = self.model.lattice_atoms_bonds(*self.nsc, self.bond_type, self.relax_index)
 
    self.aposs = ainfo[0]
    self.natoms = ainfo[0].shape[0]
    self.atoms = []
    if self.natoms > 0:
      self.atoms = actor.sphere(centers=ainfo[0], colors=ainfo[1], radii=ainfo[2])
      self.scene.add(self.atoms)
      self.atoms.AddObserver('LeftButtonPressEvent', self.pick_atom, 1)

    self.bonds = []
    for i in range(binfo[0].shape[0]):
      tbond = actor.cylinder(binfo[0][i], binfo[1][i], binfo[2][i], radius=binfo[3][i], heights=binfo[4][i], resolution=20)
      self.scene.add(tbond)
      self.bonds.append(tbond)

    self.frame = actor.streamtube(linfo, colors=(1,1,1), linewidth=0.1)
    self.scene.add(self.frame)
