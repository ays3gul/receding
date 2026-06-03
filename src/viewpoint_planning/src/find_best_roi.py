#!/usr/bin/env python3
"""
find_best_roi.py — Bunny uzerinde EN IYI ROI merkezini bulur.

Bunny yuzeyini tarayip, 60mm ROI kubunun en cok mesh noktasi icerdigi
(yani en yogun, en reconstruct-edilebilir) bolgeyi bulur. Ayrica kameraya
bakan on yuzeyi tercih eder (dusuk Y = kameraya yakin taraf).

Robot/ROS gerekmez. Calistir:  python find_best_roi.py
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
vertices_swapped = vertices[:, [0, 2, 1]]
scale = np.array([-1.2, 1.2, 1.2])
z_corr = float(os.environ.get("MESH_Z_CORR", 0.048))
translation = np.array([0.5, -0.4, 1.0 - z_corr])
coords = vertices_swapped * scale + translation

roi_half = 0.03

def count_in_roi(t):
    return int(np.sum(np.all(np.abs(coords - t) <= roi_half, axis=1)))

# Bunny yuzey noktalari uzerinde tara: her vertex'i potansiyel ROI merkezi yap
# ama hizlandirmak icin 3D grid uzerinde tara
bb_lo = coords.min(0); bb_hi = coords.max(0)
print("Bunny bbox:", bb_lo.round(3), bb_hi.round(3))
print(f"MESH_Z_CORR={z_corr}\n")

# Grid tarama (2cm adim)
best = []
for x in np.arange(bb_lo[0], bb_hi[0], 0.02):
    for y in np.arange(bb_lo[1], bb_hi[1], 0.02):
        for z in np.arange(bb_lo[2], bb_hi[2], 0.02):
            t = np.array([x, y, z])
            n = count_in_roi(t)
            best.append((n, t))
best.sort(key=lambda b: -b[0])

print("=== EN YOGUN 8 ROI MERKEZI (en cok mesh noktasi) ===")
for n, t in best[:8]:
    print(f"  target=({t[0]:.3f}, {t[1]:.3f}, {t[2]:.3f})  -> {n} mesh noktasi")

print(f"\n=== KARSILASTIRMA ===")
print(f"  Mevcut (0.5,-0.4,1.1)      -> {count_in_roi(np.array([0.5,-0.4,1.1]))} nokta")
print(f"  En iyi                      -> {best[0][0]} nokta @ ({best[0][1][0]:.3f},{best[0][1][1]:.3f},{best[0][1][2]:.3f})")

# Kameraya bakan on yuzey tercihi: en dusuk Y'li yogun bolge
print(f"\n=== KAMERAYA YAKIN TARAF (dusuk Y, >800 nokta) ===")
front = [(n,t) for n,t in best if n > 800]
front.sort(key=lambda b: b[1][1])  # en dusuk Y
for n, t in front[:5]:
    print(f"  target=({t[0]:.3f}, {t[1]:.3f}, {t[2]:.3f})  -> {n} nokta")
