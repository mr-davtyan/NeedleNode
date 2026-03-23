import pyembroidery
import sys

try:
    path = "inbox/Amazing Design Embroidery (22372 Files) Embroiderydonkers/MemoryCards/104 - Birds_ Butterflies/12.pes"
    pattern = pyembroidery.read(path)
    if not pattern:
        print("Failed to read pattern")
        sys.exit(1)
        
    print(f"Loaded {path}")
    print(f"Stitches: {len(pattern.stitches)}")
    print(f"Colors/Threads: {len(pattern.threads)}")
    print(f"Bounds: {pattern.bounds()}")
    
    # Test rendering to PNG
    pyembroidery.write_png(pattern, "test_render.png")
    print("Thumbnail written to test_render.png")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
