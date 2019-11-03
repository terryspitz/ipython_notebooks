import collections
import copy
import numpy as np

class TriangleStack(object):
  Element = collections.namedtuple("Element", ["vertex", "triangle_offsets"])
  # vertex: Optional(List[float, 2])
  # triangle_offsets: Optional(List(int, 2))
  ARRAY_SHAPE = [150, 6]
  
  def __init__(self, elements):
    self._elements = elements
    
  @property
  def elements(self):
    return self._elements
  
  def get_triangles(self, debug=False):
    if debug:
      print("\nget_triangles")
    vertices = []
    triangles = []
    for vertex, triangle in self._elements:
      if vertex is not None:
        vertices.append(vertex)
      if triangle is not None:
        last_vertex = len(vertices)-1
        triangles.append([last_vertex, last_vertex-1-triangle[0], last_vertex-2-triangle[1]])
    if debug:
      print(vertices, triangles)
      
    return {'vertices': vertices, 'triangles': triangles}

  @classmethod    
  def build_stack(cls, nptri, debug=False):
    elements = []
    vertex_index_to_old_index = []
    vertices = nptri['vertices']
    triangles = copy.copy(nptri['triangles'])
    if debug:
      print("\nbuild_stack")
      #print(vertices)
      #print(triangles)
    def add_vertex(index):
      if debug:
        print("add_vertex: ", index)
      elements.append(TriangleStack.Element(vertices[index], None))
      vertex_index_to_old_index.append(index)
    def add_triangle(j, k):
      i = len(vertex_index_to_old_index)-1
      triangle_offsets = [i-j-1, i-k-2]
      if debug:
        print("add_triangle: ", (i, j, k), "->", triangle_offsets)
      if not elements[-1].triangle_offsets:
        elements[-1] = TriangleStack.Element(elements[-1].vertex, triangle_offsets)
      else:
        elements.append(TriangleStack.Element(None, triangle_offsets))
    index = -1
    while triangles.max()>-1:
      if debug:
        print("index: %d, last element: %s, vertices: %s" %(index, elements[-1] if elements else "", vertex_index_to_old_index))
      if debug:
        print("Add next vertex")
      for i in range(len(vertex_index_to_old_index)-1, -1, -1):
        matches = ((triangles==index) + (triangles==vertex_index_to_old_index[i])).sum(axis=1)
        assert 0 <= matches.max() <= 2
        matching_tris = (matches==2).nonzero()[0]
        if matching_tris.size:
          # Add index from triangle with 2 other matches
          tri_index = np.random.choice(matching_tris)
          indices = list(triangles[tri_index])
          if debug:
            print("matches2: ", matching_tris, matches, tri_index, indices)
          indices.remove(index)
          indices.remove(vertex_index_to_old_index[i])
          index = indices[0]
          add_vertex(index)
          break
      else:
        matches = (triangles==index).sum(axis=1)
        assert 0 <= matches.max() <= 1
        matching_tris = (matches==1).nonzero()[0]
        if matching_tris.size:
          if debug:
            print("triangle matches 1, pick from: ", matching_tris)
          pick_triangles = triangles[matching_tris]
          pick_triangles[pick_triangles==index] = -1
        else:
          pick_triangles = triangles
        # Add index with min uses overall
        vertex_use_counts = np.bincount(pick_triangles[pick_triangles>=0].flatten())
        vertex_use_counts[vertex_use_counts==0] = 999
        if debug:
          print("vertex_use_counts: ", vertex_use_counts, pick_triangles)
        indices = (vertex_use_counts==vertex_use_counts.min()).nonzero()[0]
        if debug:
          print("min indices: ", indices)
        index = np.random.choice(indices)
        add_vertex(index)        

      # Add any triangles possible, closest matches first
      if debug:
        print("Add any triangles")
      for i in range(len(vertex_index_to_old_index)-2, -1, -1):
        for j in range(i-1, -1, -1):
          matching_tris = ((triangles==index) 
                           + (triangles==vertex_index_to_old_index[i]) 
                           + (triangles==vertex_index_to_old_index[j])).sum(axis=1)
          if matching_tris.max()==3:
            tri = (matching_tris==3).nonzero()[0][0]
            if debug:
              print("tris: ", tri, matching_tris)
            add_triangle(i, j)
            triangles[tri] = -1

    if debug:
      print("Done build_stack")
    return cls(elements)

  @property
  def array(self):
    element_list = [[1.0 if vertex is not None else 0.0,
                    vertex[0] if vertex is not None else 0.0,
                    vertex[1] if vertex is not None else 0.0,
                    1.0 if offsets is not None else 0.0,
                    float(offsets[0]) if offsets is not None else 0.0,
                    float(offsets[1]) if offsets is not None else 0.0
                   ] for vertex, offsets in self._elements]
    if len(element_list)>self.ARRAY_SHAPE[0]:
      print("Too many elements: %d, truncating to %d" % (len(elements_list), self.ARRAY_SHAPE[0]))
      element_list = element_list[:self.ARRAY_SHAPE[0]]
    else:
      element_list += [[0.0]*6] * (self.ARRAY_SHAPE[0]-len(element_list))
    nparray = np.array(element_list)
    assert list(nparray.shape) == self.ARRAY_SHAPE, "%s!=%s" % (nparray.shape, self.ARRAY_SHAPE)
    return nparray

  @classmethod    
  def from_array(cls, nparray):
    assert list(nparray.shape) == cls.ARRAY_SHAPE, "%s!=%s" % (nparray.shape, cls.ARRAY_SHAPE)
    elements = []
    for i in range(0, nparray.shape[0]):
      is_vertex = nparray[i, 0]>0.5
      is_triangle = nparray[i, 3]>0.5
      if not is_vertex and not is_triangle:
        break
      elements.append(TriangleStack.Element(
          [nparray[i, 1], nparray[i, 2]] if is_vertex else None,
          [max(0, int(nparray[i, 4])), max(0, int(nparray[i, 5]))] if is_triangle else None))
    return cls(elements)
