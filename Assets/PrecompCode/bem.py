import bempp.api
import numpy as np

def p_bar(object_mesh, sample_points, frequency, participation, c=343, rho_air=1.21):
    print(f"Start Calculating p_bar for frequency {frequency}-------------------")
    
    object_grids = bempp.api.Grid(object_mesh.vertices.T, object_mesh.faces.T)
    space = bempp.api.function_space(object_grids, "P", 1)
    identity = bempp.api.operators.boundary.sparse.identity(space, space, space)
        
    omega = 2 * np.pi * frequency
    k = omega / c
    
    slp = bempp.api.operators.boundary.helmholtz.single_layer(space, space, space, k)
    dlp = bempp.api.operators.boundary.helmholtz.double_layer(space, space, space, k)
    
    @bempp.api.complex_callable
    def vibration(x, n, domain_index, result):
        normal_disp = np.dot(participation, n)
        result[0] = rho_air * omega**2 * normal_disp
    
    rhs_fun = bempp.api.GridFunction(space, fun=vibration)
    lhs = 0.5 * identity - dlp + 1j * k * slp
    pressure_solution, _ = bempp.api.linalg.gmres(lhs, rhs_fun, tol=1e-5)
            
    slp_potential = bempp.api.operators.potential.helmholtz.single_layer(space, sample_points, k)
    p_bar = slp_potential.evaluate(pressure_solution)
    
    print("Finish Calculating p_bar -------------------")
    return np.real(p_bar)