import numpy as np
import trimesh

def load_mesh(membrane_path, surface_path):
    membrane = trimesh.load(membrane_path, process=True)
    surface = trimesh.load(surface_path, process=True)
    return membrane, surface

# Load meshes
def offset(original_mesh, offset_mesh):
    # Sample points from original mesh surface
    sample_points, _ = trimesh.sample.sample_surface(original_mesh, 1000)

    # Compute closest distances from sample points to offset mesh
    closest_points, distances, _ = trimesh.proximity.closest_point(offset_mesh, sample_points)

    # Calculate average distance
    avg_distance = np.mean(distances)
    max_distance = np.max(distances)
    min_distance = np.min(distances)

    print(f"Average offset distance: {avg_distance:.4f} m")
    print(f"Max offset distance: {max_distance:.4f} m")
    print(f"Min offset distance: {min_distance:.4f} m")
    
    edge_lengths = original_mesh.edges_unique_length
    max_edge_length = np.max(edge_lengths)
    min_edge_length = np.min(edge_lengths)
    print(f"Max edge length: {max_edge_length:.4f} m")
    print(f"Min edge length: {min_edge_length:.4f} m")

def init_weight_mat(mesh):
    num_vertices = len(mesh.vertices)
    
    # get area of faces
    face_area = mesh.area_faces
    
    vertex_weight = np.zeros(num_vertices)
    for idx, face in enumerate(mesh.faces):
        for v_id in face:
            vertex_weight[v_id] += face_area[idx] / 3.0
    
    # sample size N equal to number of vertices
    # W is a diagonal matrix with diagonal elements equal to sqrt(vertex_weight)
    W = np.diag(np.sqrt(vertex_weight))
    return W, mesh.vertices

def generate_candidate_points(mesh, num_points):
    # create bounding box and sample points
    min_bounds, max_bounds = mesh.bounds
    candidate_points = np.random.uniform(min_bounds, max_bounds, (num_points, 3))
    
    # check if candidate points are inside the mesh
    insides = []
    for point in candidate_points:
        if mesh.contains([point])[0]:  # Check if inside
            insides.append(point)
    
    return np.array(insides)
