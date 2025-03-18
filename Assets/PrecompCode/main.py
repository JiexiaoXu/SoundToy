from geometry import load_mesh, offset, init_weight_mat
from bem import p_bar
from multipole_algo import multipole_placement
from multipole_util import multipole_basis_func
from multipole_util import compute_coefficient
import struct

import numpy as np

membrane_path = '/home/jiexiao/class/493v/cse493v-25wi/final_project/assets/membrane.obj'
surface_path = '/home/jiexiao/class/493v/cse493v-25wi/final_project/assets/surface.obj'

speed_of_sound = 343  # m/s (Air)
rho_air = 1.21  # kg/m³ (Air)

modal_data = [
    {"frequency": 101.171, "participation": np.array([61.244601, 0, 0])},
    {"frequency": 156.719, "participation": np.array([0, 63.0976975, 0])},
    {"frequency": 431.00, "participation": np.array([22.3486006, 0, 0.0001])},
    {"frequency": 450.849, "participation": np.array([0, 0, 78.8592994])},
    {"frequency": 495.658, "participation": np.array([0, 22.4906996, 0])},
]


def export_sound_data(frequency, positions, coefficients, output_dir="output"):
    # Export sound data to a file or any other format
    k = 2 * np.pi * frequency / speed_of_sound
    coefficients = np.array(coefficients.flatten(), dtype=np.complex128)
    positions = np.array(positions, dtype=np.float64)
    
    num_sources = len(positions)
    
    sources_filename = f"{output_dir}/{frequency:.0f}.sources"
    k_filename = f"{output_dir}/{frequency:.0f}.k"
    
    sources_data = []
    for i in range(num_sources):
        sources_data.extend(positions[i].tolist())
        
        # Monopole term (Re, Im)
        sources_data.append(coefficients[4 * i].real)
        sources_data.append(coefficients[4 * i].imag)

        # Dipole (m=0) term (Re, Im)
        sources_data.append(coefficients[4 * i + 1].real)
        sources_data.append(coefficients[4 * i + 1].imag)

        # Dipole (m=-1) term (Re, Im)
        sources_data.append(coefficients[4 * i + 2].real)
        sources_data.append(coefficients[4 * i + 2].imag)

        # Dipole (m=+1) term (Re, Im)
        sources_data.append(coefficients[4 * i + 3].real)
        sources_data.append(coefficients[4 * i + 3].imag)
    
    sources_data = np.array(sources_data, dtype=np.float64)
    print(sources_data)
    
    with open(sources_filename, "wb") as f:
        f.write(sources_data.tobytes())

    print(f"Exported {sources_filename} with {num_sources} sources.")

    # Write .k file in binary format
    with open(k_filename, "wb") as f:
        f.write(struct.pack("d", k))  # Write one double-precision float

    print(f"Exported {k_filename} (wave number = {k:.6f}).")

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
            object_mesh=surface,
            sample_points=sample_points.T,
            frequency=frequency,
            participation=participation
            )
        
        print(p_bar_val)
        
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
        export_sound_data(
            frequency=frequency,
            positions=selected_positions,
            coefficients=coefficients
        )
        print("=========================================")

        
        