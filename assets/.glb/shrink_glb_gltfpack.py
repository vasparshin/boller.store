import argparse, os, shutil, subprocess, tempfile, pathlib

TARGET_MB_DEFAULT = 25.0
# Very conservative simplification steps - preserve scene structure
SIMPLIFY_STEPS = [0.98, 0.95, 0.92, 0.90, 0.87, 0.85, 0.82, 0.80]  # Ratio of triangles to keep

def sizeof_mb(p): return os.path.getsize(p)/(1024*1024)

def run_gltfpack(src, dst, si_ratio=None, preserve_precision=False):
    """
    Run gltfpack with conservative settings
    si_ratio: triangle ratio to keep (0.95 = keep 95% of triangles)
    preserve_precision: use floating point attributes for better precision
    """
    cmd_parts = [f'gltfpack -i "{src}" -o "{dst}"']
    
    # Add basic compression (safe)
    cmd_parts.append("-c")
    
    # Preserve scene structure
    cmd_parts.extend(["-kn", "-km", "-ke"])  # keep named nodes, materials, and extras
    
    # Preserve precision for better geometry quality
    if preserve_precision:
        cmd_parts.extend(["-vpf", "-vnf", "-vtf"])  # floating point for positions, normals, texcoords
        cmd_parts.extend(["-vp", "16"])  # maximum precision for positions
    
    # Add conservative mesh simplification if specified
    if si_ratio is not None and si_ratio < 1.0:
        cmd_parts.extend(["-si", str(si_ratio)])
        # Add flags to preserve borders and avoid gaps between connected meshes
        cmd_parts.extend(["-slb"])  # lock border vertices during simplification
    
    cmd = " ".join(cmd_parts)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"gltfpack command failed: {cmd}")
        print(f"Error output: {e.stderr}")
        raise

def process_file(in_path, out_path, target_mb):
    work = tempfile.NamedTemporaryFile(delete=False, suffix=".glb").name
    work_out = tempfile.NamedTemporaryFile(delete=False, suffix=".glb").name
    shutil.copyfile(in_path, work)
    
    print(f"Processing {in_path} (original: {sizeof_mb(in_path):.2f} MB)")

    # Step 1: Try basic compression with precision preservation
    try:
        print("  Step 1: Basic compression with precision preservation...")
        run_gltfpack(work, work_out, preserve_precision=True)
        shutil.move(work_out, work)
        current_size = sizeof_mb(work)
        print(f"  After high-precision compression: {current_size:.2f} MB")
        
        if current_size <= target_mb:
            print("  ✓ Target achieved with high-precision compression!")
            shutil.move(work, out_path)
            return True, current_size
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"ERROR: gltfpack failed on {in_path}. Error: {e}")
        return False, sizeof_mb(in_path)

    # Step 2: Try basic compression without floating point (smaller file)
    try:
        print("  Step 2: Basic compression without floating point...")
        shutil.copyfile(in_path, work)  # Reset to original
        run_gltfpack(work, work_out, preserve_precision=False)
        shutil.move(work_out, work)
        current_size = sizeof_mb(work)
        print(f"  After basic compression: {current_size:.2f} MB")
        
        if current_size <= target_mb:
            print("  ✓ Target achieved with basic compression!")
            shutil.move(work, out_path)
            return True, current_size
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  Basic compression failed: {e}")

    # Step 3: Very conservative mesh simplification with border preservation
    for si_ratio in SIMPLIFY_STEPS:
        if sizeof_mb(work) <= target_mb:
            break
        
        try:
            print(f"  Step 3: Conservative simplification (keep {si_ratio*100:.0f}% triangles, preserve borders)...")
            run_gltfpack(work, work_out, si_ratio=si_ratio, preserve_precision=False)
            shutil.move(work_out, work)
            current_size = sizeof_mb(work)
            print(f"  After simplification ({si_ratio*100:.0f}%): {current_size:.2f} MB")
            
            if current_size <= target_mb:
                print(f"  ✓ Target achieved with {si_ratio*100:.0f}% geometry!")
                break
        except subprocess.CalledProcessError:
            print(f"  Simplification at {si_ratio*100:.0f}% failed, trying next level...")
            continue

    final_mb = sizeof_mb(work)
    shutil.move(work, out_path)
    return final_mb <= target_mb, final_mb

def main():
    ap = argparse.ArgumentParser(description="Shrink .glb files to <= target size via gltfpack.")
    ap.add_argument("input", help="Input .glb file or directory")
    ap.add_argument("-o","--output", help="Output file/dir (default: *_optimized.glb or <dir>_optimized)")
    ap.add_argument("-t","--target-mb", type=float, default=TARGET_MB_DEFAULT)
    args = ap.parse_args()

    in_path = pathlib.Path(args.input)
    if in_path.is_file():
        outf = pathlib.Path(args.output) if args.output else in_path.with_name(in_path.stem + "_optimized.glb")
        ok, sz = process_file(str(in_path), str(outf), args.target_mb)
        print(f"{'OK' if ok else 'NOT MET'}: {outf} -> {sz:.2f} MB")
    else:
        if args.output:
            out_dir = pathlib.Path(args.output)
        else:
            # Handle current directory case
            if in_path.name == '.' or in_path.name == '':
                out_dir = pathlib.Path.cwd() / "optimized"
            else:
                out_dir = in_path.with_name(in_path.name + "_optimized")
        out_dir.mkdir(exist_ok=True, parents=True)
        for p in in_path.glob("*.glb"):
            outf = out_dir / (p.stem + "_optimized.glb")
            ok, sz = process_file(str(p), str(outf), args.target_mb)
            print(f"{'OK' if ok else 'NOT MET'}: {outf.name} -> {sz:.2f} MB")

if __name__ == "__main__":
    main()
