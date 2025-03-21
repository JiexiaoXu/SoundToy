import numpy as np
import struct
import scipy.special as sp
import scipy.io.wavfile as wavfile

def spherical_coords(rel_pos):
    x, y, z = rel_pos
    r = np.linalg.norm(rel_pos)
    theta = np.arccos(z / r) if r > 0 else 0.0
    phi = np.arctan2(y, x)
    return r, theta, phi, x, y, z

def complex_mul(aRe, aIm, bRe, bIm):
    oRe = (aRe) * (bRe) - (aIm) * (bIm)
    oIm = (aRe) * (bIm) + (aIm) * (bRe)
    return oRe, oIm

def complex_fma(aRe, aIm, bRe, bIm, oRe, oIm):
    oRe += (aRe) * (bRe) - (aIm) * (bIm)
    oIm += (aRe) * (bIm) + (aIm) * (bRe)
    return oRe, oIm

# input: mic_pos: position of the microphone (numpy array)
#        sources: array of sources, each source is a numpy array of shape (11,)
#        k: wavenumber
# ouput: pressure: the evaluated pressure at the microphone position
def evaluate_dipoles(mic_pos, sources, k):
    pressure_re, pressure_im = 0.0, 0.0

    for source in sources:
        src_pos = source[:3]
        rel_pos = mic_pos - src_pos
        x,y,z = rel_pos
        r = np.linalg.norm(rel_pos)
        planar_r = np.sqrt(x**2 + y**2)
        if r == 0 or planar_r == 0:
            continue
        
        cos_theta = z / np.sqrt(x**2 + y**2 + z**2)
        sin_theta = planar_r / np.linalg.norm([x, y, z])
        cos_phi = x / planar_r if planar_r > 0 else 0.0
        sin_phi = y / planar_r if planar_r > 0 else 0.0
        
        kr = k * r
        invKr = 1.0 / kr if kr != 0 else 0.0
        sin_kr, cos_kr = np.sin(kr), np.cos(kr)

        cos_phi_sin_theta = cos_phi * sin_theta
        sin_phi_sin_theta = sin_phi * sin_theta

        mono_re, mono_im = source[3], source[4]
        dip0_re, dip0_im = source[5], source[6]
        dip_m1_re, dip_m1_im = source[7], source[8]
        dip_p1_re, dip_p1_im = source[9], source[10]

        # monopole contribution
        bufferRe = sin_kr * invKr
        bufferIm = cos_kr * invKr
        pressure_re, pressure_im = complex_fma(bufferRe, bufferIm, mono_re, mono_im, pressure_re, pressure_im)

        # dipole m=0 contribution
        radial_re = invKr * (-cos_kr + invKr * sin_kr)
        radial_im = invKr * (sin_kr + invKr * cos_kr)
        
        bufferRe = radial_re * cos_theta
        bufferIm = radial_im * cos_theta
        pressure_re, pressure_im = complex_fma(bufferRe, bufferIm, dip0_re, dip0_im, pressure_re, pressure_im)
        
        # dipole m=-1 contribution
        bufferRe, bufferIm = complex_mul(radial_re, radial_im, cos_phi_sin_theta, -sin_phi_sin_theta)
        pressure_re, pressure_im = complex_fma(bufferRe, bufferIm, dip_m1_re, dip_m1_im, pressure_re, pressure_im)

        # dipole (m=+1)
        bufferRe, bufferIm = complex_mul(radial_re, radial_im, -cos_phi_sin_theta, -sin_phi_sin_theta)
        pressure_re, pressure_im = complex_fma(bufferRe, bufferIm, dip_p1_re, dip_p1_im, pressure_re, pressure_im)

    return np.abs(pressure_re + 1j * pressure_im)

# Example usage:
def load_sources(filename):
    with open(filename, 'rb') as f:
        data = f.read()
        num_sources = len(data) // (11 * 8)
        sources = struct.unpack(f'{num_sources * 11}d', data)
    return np.array(sources).reshape(num_sources, 11)

def load_k(filename):
    with open(filename, 'rb') as f:
        f.seek(-8, 2)  # last 8 bytes
        k = struct.unpack('d', f.read())[0]
    return k

def pressure_to_waveform(pressures, freqs, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.zeros_like(t)

    for pressure, freq in zip(pressures, freqs):
        waveform += pressure * np.sin(2 * np.pi * freq * t)

    waveform /= np.max(np.abs(waveform))
    return waveform


if __name__ == '__main__':
    
    duration = 2.0  # Audio duration (seconds)
    sample_rate = 44100  # Standard audio sampling rate
    
    # Load example data and evaluate pressures
    with open("PATlist.txt") as f:
        pat_list = f.read().splitlines()
    
    mic_positions = np.array([0.0, 0.0, 1.0])  # Example microphone positions
    
    frequencies = []
    pressures = []
    for idx, pat in enumerate(pat_list):
        print(f"Processing PAT: {pat}")    
        sources = load_sources(f"{pat}.sources")
        k = load_k(f"{pat}.k")
        frequencies.append(k * (343 / (2 * np.pi)))  # Assuming speed of sound is 343 m/s
        pressures.append(evaluate_dipoles(mic_positions, sources, k))
    

    print("Pressure magnitudes:", pressures)
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    waveform = pressure_to_waveform(pressures, frequencies, duration, sample_rate)
    wavfile.write("pat_sound.wav", sample_rate, np.int16(waveform * 32767))