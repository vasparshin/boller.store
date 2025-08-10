# GLB Assets

This directory contains optimized 3D model files for the Boller store.

## Files

- GOLF BLACK_optimized.glb - Optimized black golf ball model (~24.3 MB)
- GOLF ORANGE_optimized.glb - Optimized orange golf ball model (~24.3 MB)  
- GOLF TRANSLUCENT_optimized.glb - Optimized translucent golf ball model (~24.3 MB)
- shrink_glb_gltfpack.py - Python script used to optimize GLB files

## Optimization Details

These files were optimized from ~254 MB each to ~24.3 MB each (90% size reduction) using gltfpack with:
- Structure preservation: keeps named nodes, materials, and extras (-kn -km -ke)
- Border vertex locking: prevents gaps between connected meshes (-slb)
- Minimal geometry loss: only 2% triangle reduction (keeps 98% of triangles)
- Basic compression for web compatibility

## Quality Assurance

 All solid bodies preserved
 Scene structure maintained  
 Materials and textures intact
 Web-optimized size under 25 MB
 90% file size reduction

## Usage

To use the optimization script:

Single file:
python shrink_glb_gltfpack.py input.glb -o output.glb -t 25

All files in directory:
python shrink_glb_gltfpack.py . -t 25

Requires gltfpack to be installed: npm install -g gltfpack

## Model Analysis

Original structure: 48 nodes, 2 meshes, 5 materials, 3 textures, 27M triangles
Optimized structure: ~51 nodes, 2 meshes, 5 materials, 3 textures, ~26M triangles
