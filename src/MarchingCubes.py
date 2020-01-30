

def marching_cubes ( grid, iso_val, rlat, BZ_planes, color ):
  '''
    March through the entire grid and create a list of all triangles to draw

    Arguments:
      grid (ndarray): Array with the surface data to compare to iso_val
      iso_val (float): Value of the desired iso-surface
      rlat (ndarray): 3 reciprocal lattice vectors
      BZ_planes (ndarray): List of all of the planes which make up the BZ
      color (list): 3-d RGB color vectors for the band.

    Returns:
      (ndarray): List of vpython triangles that were drawn
  '''
  import numpy as np
  import vpython as vp
  from .VertexTables import edge_offsets, corner_offsets, vertex_table

  if len(grid.shape) != 3:
    print('Grid must be 3 dimensional.')
    quit()

  n1,n2,n3 = grid.shape
  vp_shift = .5 * np.ones(3)

  # Precompute samples
  samples = np.zeros((n1-1,n2-1,n3-1,8),dtype=int)
  for i in range(n1-1):
    for j in range(n2-1):
      for k in range(n3-1):
        key = (i,j,k)
        for c in range(8):
          ind = tuple(key[v]+corner_offsets[c][v] for v in range(3))
          samples[i,j,k,c] = grid[ind]

  vertex_norms = np.zeros((n1,n2,n3,3), dtype=float)
  def get_cube_triangles ( index ):
    '''
      Evaluates the requred triangles within a single cube.
  
      Arugments:
        index (tuple of ints): A tuple with 3 indices for the current position in grid
  
      Returns:
        (ndarray): List of 3d points, always in multiples of 3 points to define triangles.
    '''
    case = 0
    a,b,c = index
    for i in range(8):
      if samples[a,b,c,i] > iso_val:
        case |= 1<<i
  
    if case == 0 or case == 255:
      return
  
    vertex = -1
    vertices = []
    for i in range(5):
      v_inds = []
      for j in range(3):
        vertex += 1
        edge = vertex_table[case, vertex]

        if edge == -1:
          return np.array(vertices)
  
        v1 = np.array(index) + edge_offsets[edge, 0]
        v2 = np.array(index) + edge_offsets[edge, 1]
        s1 = grid[tuple(v1)]
        s2 = grid[tuple(v2)]
  
        diff = s1 - s2
        diff = .5 if diff==0. else (s1-iso_val)/diff
        corner_pos = v1 + diff * (v2 - v1)
        vertices.append(corner_pos)
  
        v_inds.append(tuple(v1) if diff<.5 else tuple(v2))
  
      vt = vertices[-3:]
      norm = np.cross(vt[1]-vt[0], vt[2]-vt[1])
      for v in v_inds:
        vertex_norms[v] += norm

  def vector ( a ):
    return vp.vector(a[0], a[1], a[2])

  def inside_BZ ( pnt ):
    pmag = np.linalg.norm(pnt)
    for p in BZ_planes:
      if pmag > np.linalg.norm(p):
        return False
    return True

  vp_vertices = {}
  color = vector(color)
  def add_triangle ( tri ):
    vs = []
    for j,t in enumerate(tri):
      ind = tuple(np.rint(t).astype(int))
      t = t / grid.shape[j] - vp_shift
      t = t @ rlat
      if not inside_BZ(t):
        for v in vs:
          v.visible = False
          del v
        return None
      if ind not in vp_vertices:
        vp_vertices[ind] = vp.vertex(pos=vector(t), color=color)
      vs.append(vp_vertices[ind])
    return vp.triangle(vs=vs)

  triangles = []
  for i in range(n1-1):
    for j in range(n2-1):
      for k in range(n3-1):
        cube_tris = get_cube_triangles((i,j,k))
        if cube_tris is not None:
          for c in range(cube_tris.shape[0]//3):
            t = add_triangle(cube_tris[3*c:3*(c+1)])
            if t is not None:
              triangles.append(t)

  for k,v in vp_vertices.items():
    v.normal = vector(vertex_norms[k]).norm()

  return triangles 