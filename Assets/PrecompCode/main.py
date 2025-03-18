from geometry import load_mesh, offset, init_weight_mat
from bem import p_bar
from multipole_algo import multipole_placement
from multipole_util import multipole_basis_func
from multipole_util import compute_coefficient

import numpy as np

membrane_path = '/home/jiexiao/class/493v/cse493v-25wi/final_project/assets/membrane.obj'
surface_path = '/home/jiexiao/class/493v/cse493v-25wi/final_project/assets/surface.obj'

density = 8470  # kg/m³
youngs_modulus = 97e9 # MPa
poisson_ratio = 0.31
speed_of_sound = 343  # m/s (Air)
rho_air = 1.21  # kg/m³ (Air)

modal_data = [
    {"frequency": 101.171, "participation": np.array([61.244601, 0, 0])},
    {"frequency": 156.719, "participation": np.array([0, 63.0976975, 0])},
    {"frequency": 224.079, "participation": np.array([0, 0, 0])},
    {"frequency": 431.00, "participation": np.array([22.3486006, 0, 0.0001])},
    {"frequency": 450.849, "participation": np.array([0, 0, 78.8592994])},
    {"frequency": 495.658, "participation": np.array([0, 22.4906996, 0])},
    {"frequency": 653.693, "participation": np.array([0, 0, 0])},
    {"frequency": 865.311, "participation": np.array([2.61620004, 0.0001, 0])},
]

if __name__ == '__main__':
    membrane, surface = load_mesh(membrane_path, surface_path)
    offset(membrane, surface)
    
    W, sample_points = init_weight_mat(surface)
    
    # bem solver, produce sound pressure evaluation on vertices of membrane
    
    for mode in modal_data:
        frequency = mode["frequency"]
        participation = mode["participation"]
        if np.linalg.norm(participation) < 1e-6:
            continue

        p_bar_val = p_bar(
            object_mesh=membrane,
            sample_points=sample_points.T,
            frequency=frequency,
            participation=participation
            )
        
        selected_positions = multipole_placement(
            tolerance=1e-3,
            W = W,
            p_bar=p_bar_val.T,
            offset_surface=membrane,
            sample_points=sample_points,
            frequency=frequency,
            num_sources=3,
            num_candidates=10,
            multipole_basis_func=multipole_basis_func
        )
        
        coefficients = compute_coefficient(
            weight=W,
            multipole_pos=selected_positions,
            p_bar=p_bar_val.T,
            sample_points=sample_points,
            frequency=frequency
        )
        print(selected_positions)
        print(coefficients)
        print("=========================================")
        
        