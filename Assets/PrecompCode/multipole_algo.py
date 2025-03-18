import numpy as np
from geometry import init_weight_mat, generate_candidate_points
from multipole_util import modified_gram_schmidt

def pick_multipole(residual, candidate_points, sample_points, weight_mat, multipole_basis_func, frequency):
    '''pick multipole that minimizes the error of bem'''
    best_score = -np.inf
    best_pos = None
    
    for candidate in candidate_points:        
        V_x = multipole_basis_func(candidate, sample_points, frequency)
        WV_x = weight_mat @ V_x
        U_x, _ = np.linalg.qr(WV_x)
        score = np.linalg.norm(U_x.T.conj() @ residual, 2)
        
        if score > best_score:
            best_score = score
            best_pos = candidate
    
    return best_pos

def expand_subspace_and_update_residual(Q, r, new_position, sample_points, weight_mat, multipole_basis_func, frequency):
    V_x = multipole_basis_func(new_position, sample_points, frequency)
    WV_x = weight_mat @ V_x
    
    QWV_x = np.hstack((Q, WV_x)) if Q.size > 0 else WV_x
    Q_new = modified_gram_schmidt(QWV_x)
    
    
    Q_x = Q_new[:, -WV_x.shape[1]:]
    projection = Q_x @ (Q_x.T.conj() @ r)
    r = r - projection
    
    return Q_new, r

    
def multipole_placement(tolerance, W, p_bar, offset_surface, sample_points, frequency, num_sources, num_candidates, multipole_basis_func):
    # residual
    print(W.shape, p_bar.shape)
    r = W @ p_bar
    r = r / np.linalg.norm(r)
    
    # init Q subspace
    Q = np.zeros((len(p_bar), 0), dtype=np.complex128)
    
    # init selected positions
    selected_positions = []
    
    print("Start Multipole Placement -------------------")
    print(f"Initial residual norm: {np.linalg.norm(r, 2)}")
    
    while np.linalg.norm(r, 2) > tolerance and len(selected_positions) < num_sources:
        print(f"finding source {len(selected_positions) + 1}")
        
        # generate candidate points
        candidate_points = generate_candidate_points(offset_surface, num_candidates)
        
        # pick multipole that minimizes the error of bem
        best_pos = pick_multipole(r, candidate_points, sample_points, W, multipole_basis_func, frequency)
        
        if best_pos is None:
            continue
        
        # update Q subspace
        Q, r = expand_subspace_and_update_residual(Q, r, best_pos, sample_points, W, multipole_basis_func, frequency) 
        
        print(f"Residual norm: {np.linalg.norm(r, 2)}")
        
        # update selected positions
        selected_positions.append(best_pos)
        
    return selected_positions
