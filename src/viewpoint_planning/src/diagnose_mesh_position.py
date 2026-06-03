#!/usr/bin/env python3
"""
diagnose_mesh_position.py — Bunny mesh'in dunyadaki GERCEK konumunu hesaplar.

Hicbir robot/ROS gerektirmez, sadece mesh dosyasini okur. Calistir:
    python diagnose_mesh_position.py

Cikti: bunny'nin centroid'i, bounding box'i ve ONERILEN target_position.
Bu, ROI'yi bunny govdesine hizalamak icin gereken dogru target'i verir.
"""
import os
import numpy as np
import xml.etree.ElementTree as ET

file_path = "/home/ayse/gradientnbv/src/simulation_environment/meshes/bunny.dae"
tree = ET.parse(file_path); root = tree.getroot()
ns = {"ns": "http://www.collada.org/2005/11/COLLADASchema"}
arr = root.find(".//ns:float_array[@id='bun_zipper-mesh-positions-array']", ns)
raw = list(map(float, arr.text.split()))
vertices = np.array(raw).reshape(-1, 3)

# Ayni transform (viewpoint_planning.py ile birebir)
vertices_swapped = vertices[:, [0, 2, 1]]
scale = np.array([-1.2, 1.2, 1.2])
z_corr = float(os.environ.get("MESH_Z_CORR", 0.048))
translation = np.array([0.5, -0.4, 1.0 - z_corr])
coords = vertices_swapped * scale + translation

centroid = coords.mean(axis=0)
bb_lo = coords.min(axis=0)
bb_hi = coords.max(axis=0)
bb_center = (bb_lo + bb_hi) / 2

print("="*55)
print(f"  BUNNY MESH GERCEK KONUMU (MESH_Z_CORR={z_corr})")
print("="*55)
print(f"  Vertex sayisi    : {len(coords)}")
print(f"  Centroid (ortalama): ({centroid[0]:.4f}, {centroid[1]:.4f}, {centroid[2]:.4f})")
print(f"  BBox merkezi      : ({bb_center[0]:.4f}, {bb_center[1]:.4f}, {bb_center[2]:.4f})")
print(f"  BBox X: [{bb_lo[0]:.4f}, {bb_hi[0]:.4f}]  (genislik {(bb_hi[0]-bb_lo[0])*1000:.0f}mm)")
print(f"  BBox Y: [{bb_lo[1]:.4f}, {bb_hi[1]:.4f}]  (genislik {(bb_hi[1]-bb_lo[1])*1000:.0f}mm)")
print(f"  BBox Z: [{bb_lo[2]:.4f}, {bb_hi[2]:.4f}]  (genislik {(bb_hi[2]-bb_lo[2])*1000:.0f}mm)")
print()
print("="*55)
print("  MEVCUT vs ONERILEN TARGET")
print("="*55)
print(f"  Mevcut target_position : (0.5, -0.4, 1.1)")
print(f"  ONERILEN (centroid)    : ({centroid[0]:.3f}, {centroid[1]:.3f}, {centroid[2]:.3f})")
print()
roi_half = 0.03
print(f"  Mevcut ROI kubu Z: [1.070, 1.130]")
print(f"  Onerilen ROI kubu Z: [{centroid[2]-roi_half:.3f}, {centroid[2]+roi_half:.3f}]")
print()
# ROI'ye giren mesh nokta sayisi: mevcut vs onerilen
def count_in_roi(t):
    return int(np.sum(np.all(np.abs(coords - t) <= roi_half, axis=1)))
print(f"  Mevcut target ile ROI'deki mesh nokta sayisi  : {count_in_roi(np.array([0.5,-0.4,1.1]))}")
print(f"  Onerilen target ile ROI'deki mesh nokta sayisi: {count_in_roi(centroid)}")
print()
print("  -> Onerilen target ROI'ye cok daha fazla mesh sokarsa, hizalama sorunu bu.")
