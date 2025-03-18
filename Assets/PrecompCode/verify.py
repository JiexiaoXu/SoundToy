import numpy as np
import struct

def verify_sources_file(filename):
    """
    Reads and verifies the structure of a .sources binary file.
    
    Args:
        filename (str): Path to the .sources file.
    """
    print(f"Verifying {filename}...")

    # Read binary file
    with open(filename, "rb") as f:
        data = f.read()

    # Convert binary data to NumPy array (double precision)
    values = np.frombuffer(data, dtype=np.float64)

    # Check if the number of values is a multiple of 11
    if len(values) % 11 != 0:
        print(f"❌ ERROR: Data length {len(values)} is not a multiple of 11!")
        return

    num_sources = len(values) // 11
    print(f"✅ {num_sources} sources found in {filename}.")

    # Print first 5 sources for verification
    for i in range(min(num_sources, 5)):  # Show up to 5 sources
        source_data = values[i * 11 : (i + 1) * 11]
        print(f"\n🔹 Source {i + 1}:")
        print(f"  Position:     ({source_data[0]:.6f}, {source_data[1]:.6f}, {source_data[2]:.6f})")
        print(f"  Monopole:     ({source_data[3]:.6f} + {source_data[4]:.6f}j)")
        print(f"  Dipole (m=0): ({source_data[5]:.6f} + {source_data[6]:.6f}j)")
        print(f"  Dipole (m=-1): ({source_data[7]:.6f} + {source_data[8]:.6f}j)")
        print(f"  Dipole (m=+1): ({source_data[9]:.6f} + {source_data[10]:.6f}j)")

    print(f"\n✅ Verification complete! File format appears correct.")

# Example usage
verify_sources_file("output/101.sources")
