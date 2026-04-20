"""
Integration test for SVG conversion without explicit dimensions.
Tests the fix for issue #9145: SVG images without explicit width/height attributes
"""

import os
import subprocess
import tempfile
import struct

# Path to the qubes.GetImageRGBA script
QIMG_SCRIPT = os.path.join(os.path.dirname(__file__), '../qubes-core-agent-linux/qubes-rpc/qubes.GetImageRGBA')

# Test SVG without explicit width/height (minimal Whonix-like logo)
TEST_SVG_NO_DIMENSIONS = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#3366cc" />
  <text x="50" y="55" text-anchor="middle" font-size="20" fill="white">W</text>
</svg>
'''

def test_svg_without_dimensions():
    """Test that SVG without explicit width/height dimensions converts successfully."""
    
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False, mode='w') as f:
        f.write(TEST_SVG_NO_DIMENSIONS)
        svg_path = f.name
    
    try:
        # Run the conversion script
        result = subprocess.run(
            [QIMG_SCRIPT],
            input=svg_path.encode() + b'\n',
            capture_output=True,
            timeout=10
        )
        
        assert result.returncode == 0, f"Script failed with: {result.stderr.decode()}"
        
        # Parse output: first line is "width height", rest is RGBA data
        lines = result.stdout.split(b'\n')
        dims = lines[0].decode().split()
        assert len(dims) == 2, f"Expected 'width height' output, got: {result.stdout[:100]}"
        
        width, height = int(dims[0]), int(dims[1])
        assert width > 0, "Width should be positive"
        assert height > 0, "Height should be positive"
        
        # Verify RGBA data is present and correct size
        rgba_data = b''.join(lines[1:])
        expected_size = width * height * 4  # RGBA = 4 bytes per pixel
        assert len(rgba_data) >= expected_size, \
            f"RGBA data too small: {len(rgba_data)} < {expected_size}"
        
        print(f"✓ SVG conversion successful: {width}x{height} image produced")
        
    finally:
        os.unlink(svg_path)

if __name__ == '__main__':
    test_svg_without_dimensions()
    print("All tests passed!")
