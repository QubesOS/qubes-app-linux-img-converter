#!/usr/bin/env python3
"""
Integration test for SVG image conversion without explicit dimensions.

This test verifies the fix for QubesOS/qubes-issues#9145:
SVG images without explicit width/height attributes should be converted
successfully using rsvg-convert and then converted to RGBA format.

The test is designed to run on a Qubes system with the qubes.GetImageRGBA
script available.
"""

import os
import subprocess
import tempfile
import sys


def test_svg_without_dimensions():
    """
    Test that SVG files without explicit width/height can be converted to RGBA.
    
    This reproduces the issue where SVGs without explicit dimensions would fail
    because gm identify would return 0 for width/height, and the script needs to
    call rsvg-convert first to get actual dimensions.
    """
    
    # Minimal SVG without explicit width/height attributes
    # (only viewBox, no width="..." height="..." attributes)
    svg_content = b'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#3366cc"/>
  <circle cx="50" cy="50" r="30" fill="#ffffff"/>
</svg>
'''
    
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
        f.write(svg_content)
        svg_path = f.name
    
    try:
        # The qubes.GetImageRGBA script reads the filename from stdin
        # and outputs: "width height\nRGBA_BINARY_DATA"
        
        process = subprocess.Popen(
            ['/usr/lib/qubes/qubes.GetImageRGBA'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        stdout, stderr = process.communicate(input=svg_path.encode() + b'\n', timeout=5)
        
        if process.returncode != 0:
            # Script might not be available on non-Qubes system; skip gracefully
            if b'No such file' in stderr or b'command not found' in stderr:
                print(f"SKIP: qubes.GetImageRGBA not available")
                return True
            print(f"FAIL: Script returned {process.returncode}")
            print(f"stderr: {stderr.decode()}")
            return False
        
        # Parse output
        lines = stdout.split(b'\n', 1)
        dims_line = lines[0].decode().strip()
        
        try:
            width, height = map(int, dims_line.split())
        except (ValueError, IndexError):
            print(f"FAIL: Could not parse dimensions from: {dims_line}")
            return False
        
        if width <= 0 or height <= 0:
            print(f"FAIL: Invalid dimensions: {width}x{height}")
            return False
        
        # Verify RGBA data is present
        if len(lines) < 2:
            print(f"FAIL: No RGBA data in output")
            return False
        
        rgba_data = lines[1]
        expected_bytes = width * height * 4  # RGBA = 4 bytes per pixel
        
        if len(rgba_data) < expected_bytes:
            print(f"FAIL: RGBA data incomplete: {len(rgba_data)} < {expected_bytes}")
            return False
        
        print(f"PASS: SVG without dimensions converted to {width}x{height} RGBA")
        return True
        
    except subprocess.TimeoutExpired:
        print("FAIL: Script timed out")
        return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False
    finally:
        os.unlink(svg_path)


if __name__ == '__main__':
    success = test_svg_without_dimensions()
    sys.exit(0 if success else 1)
