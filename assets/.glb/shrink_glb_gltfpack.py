import argparse, os, shutil, subprocess, tempfile, pathlib

TARGET_MB_DEFAULT = 25.0
# Start modest, increase if still too big - made more aggressive
SIMPLIFY_STEPS = [5, 10, 20, 30, 50, 70, 90]  # percent-ish; higher = more aggressive

def sizeof_mb(p): return os.path.getsize(p)/(1024*1024)

def run_gltfpack(src, dst, si):
    # -si N simplification aggressiveness, -c basic compression
    cmd = f'gltfpack -i "{src}" -o "{dst}" -si {si} -c'
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

    # First attempt (light)
    try:
        run_gltfpack(work, work_out, si=5)
        shutil.move(work_out, work)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"ERROR: gltfpack failed on {in_path}. Error: {e}")
        return False, sizeof_mb(in_path)

    # If still big, step up simplification
    for si in SIMPLIFY_STEPS:
        if sizeof_mb(work) <= target_mb:
            break
        run_gltfpack(work, work_out, si=si)
        shutil.move(work_out, work)

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
