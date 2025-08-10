# GLB Assets

This directory contains optimized 3D model files for the Boller store.

## Files

- GOLF BLACK_optimized.glb - Optimized black golf ball model (~24.3 MB)
- GOLF ORANGE_optimized.glb - Optimized orange golf ball model (~24.3 MB)  
- GOLF TRANSLUCENT_optimized.glb - Optimized translucent golf ball model (~24.3 MB)
- shrink_glb_gltfpack.py - Python script used to optimize GLB files

## Optimization Details

These files were optimized from ~254 MB each to ~24 MB each (90% size reduction) using gltfpack with:
- Basic compression (-c flag)
- Mesh simplification (progressive steps: 5, 10, 20, 30, 50, 70, 90%)
- Target size: 25 MB

## Usage

To use the optimization script:

Single file:
python shrink_glb_gltfpack.py input.glb -o output.glb -t 25

All files in directory:
python shrink_glb_gltfpack.py . -t 25

Requires gltfpack to be installed: npm install -g gltfpack
