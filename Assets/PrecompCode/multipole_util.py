import numpy as np
import scipy.special

def spherical_coords(x, center):
    diff = x - center
    r = np.linalg.norm(diff)
    theta = np.arccos(diff[2] / r)
    phi = np.arctan2(diff[1], diff[0])
    return r, theta, phi
    
def psi_val(l, m, k, r, theta, phi):
    r = np.maximum(r, 1e-10) 
    hankel_val = scipy.special.spherical_jn(l, k * r) - 1j * scipy.special.spherical_yn(l, k * r)
    if np.isnan(hankel_val).any() or np.isinf(hankel_val).any():
        hankel_val = 0.0
    spherical_harm_val = scipy.special.sph_harm(m, l, phi, theta)
    psi_lm = hankel_val * spherical_harm_val
    return psi_lm

def multipole_basis_func(x, sample_points, frequency, speed_of_sound=343):
    k = 2 * np.pi * frequency / speed_of_sound
    N = len(sample_points)

    lm_pairs = [(0,0), (1,0), (1,-1), (1,1)]
    V_x = np.zeros((N, 4), dtype=np.complex128)

    for idx, sample in enumerate(sample_points):
        r, theta, phi = spherical_coords(sample, x)      
        for j, (l, m) in enumerate(lm_pairs):
            V_x[idx, j] = psi_val(l, m, k, r, theta, phi)

    return V_x

def modified_gram_schmidt(A: np.ndarray) -> np.ndarray:
    n = A.shape[1]
    V = A.copy()
    Q = np.zeros_like(A, dtype=np.complex128)
    
    for i in range(n):
        Rii = np.linalg.norm(V[:, i])
        Q[:, i] = V[:, i] / Rii
        
        for j in range(i+1, n):
            Rij = np.dot(Q[:, i].conj().T, V[:, j])
            V[:, j] = V[:, j] - Rij * Q[:, i]

    return Q


# For real-time computation
def fin_multipole(sample_points, sources, frequency, speed_of_sound=343):
    # wave number
    k = 2 * np.pi * frequency / speed_of_sound
    N = len(sample_points)
    M = len(sources)
    
    # init basis
    # V_ij, jth multipole function evaluated at ith point
    lm_pairs = [(0,0), (1,0), (1,-1), (1,1)]
    V = np.zeros((N, M * len(lm_pairs)), dtype=np.complex128)
    
    for i, sample in enumerate(sample_points):
        for j, source in enumerate(sources):
            r, theta, phi = spherical_coords(sample, source)
            for k, (l, m) in enumerate(lm_pairs):
                V[i, j * len(lm_pairs) + k] = psi_val(l, m, k, r, theta, phi)
    return V


def compute_coefficient(weight, multipole_pos, p_bar, sample_points, frequency):
    # minimize the difference between p(x) and p_bar(x) with coefficient c
    
    # for all sample points, N, we can find the 
    # corresponding multipole basis function V(x_i)
    V = fin_multipole(sample_points, multipole_pos, frequency)
    
    weight = np.array(weight, dtype=np.float64)
    b = np.array(weight @ p_bar, dtype=np.complex128)
    
    U, S, VT = np.linalg.svd(weight @ V, full_matrices=False)
    S_truncated = np.zeros_like(S)
    mask = S > 1e-6
    S_truncated[mask] = 1.0 / S[mask]
    
    A_pinv = np.array(VT.T @ np.diag(S_truncated) @ U.T, dtype=np.complex128)
    
    c = np.array(A_pinv @ b, dtype=np.complex128)    
    return c
    
