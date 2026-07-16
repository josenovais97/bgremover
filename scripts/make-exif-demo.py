"""Regenerate static/img/demo-exif-sample.jpg — the "Try a sample photo" fixture.

The demo on /exif-remover/ parses this file for real, so it has to be a real
JPEG carrying real EXIF. The source is an original Pixel 7 Pro shot; the EXIF
block below is rebuilt rather than copied because the original lost its GPS in
transit between phone and PC. The values are the photo's own (camera, lens,
timestamp), and the coordinates are Lake Naivasha, where it was actually taken.

Run:  venv/bin/python scripts/make-exif-demo.py path/to/original.jpg
"""
import sys

from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else 'PXL_20250915_133342247.PORTRAIT.jpg'
OUT = 'static/img/demo-exif-sample.jpg'

# Lake Naivasha, Kenya — 0°46'S 36°22'E
LAT, LON = -0.766700, 36.366700


def dms(deg):
    """Decimal degrees -> (d, m, s) floats; PIL packs these as RATIONALs."""
    deg = abs(deg)
    d = int(deg)
    m_f = (deg - d) * 60
    m = int(m_f)
    s = round((m_f - m) * 60, 4)
    return (float(d), float(m), s)


im = Image.open(SRC).convert('RGB')
# Keep it a sensible page asset — the demo is about the metadata, not megapixels.
im.thumbnail((900, 900), Image.LANCZOS)

exif = Image.Exif()
exif[0x010F] = 'Google'                      # Make
exif[0x0110] = 'Pixel 7 Pro'                 # Model
exif[0x0131] = 'HDR+ 1.0.773153310zp'        # Software
exif[0x0132] = '2025:09:15 16:33:42'         # DateTime
exif[0x0112] = 1                             # Orientation

ex = exif.get_ifd(0x8769)
ex[0x9003] = '2025:09:15 16:33:42'           # DateTimeOriginal
ex[0x9004] = '2025:09:15 16:33:42'           # DateTimeDigitized
ex[0x9011] = '+03:00'                        # OffsetTimeOriginal
ex[0x829A] = 1 / 1433                        # ExposureTime
ex[0x829D] = 1.85                            # FNumber
ex[0x8827] = 47                              # ISOSpeedRatings
ex[0x920A] = 6.81                            # FocalLength
ex[0xA433] = 'Google'                        # LensMake
ex[0xA434] = 'Pixel 7 Pro back camera 6.81mm f/1.85'  # LensModel

gps = exif.get_ifd(0x8825)
gps[0x0001] = 'S' if LAT < 0 else 'N'        # GPSLatitudeRef
gps[0x0002] = dms(LAT)                       # GPSLatitude
gps[0x0003] = 'W' if LON < 0 else 'E'        # GPSLongitudeRef
gps[0x0004] = dms(LON)                       # GPSLongitude
gps[0x0006] = 1884.0                         # GPSAltitude (Naivasha sits high)
gps[0x001D] = '2025:09:15'                   # GPSDateStamp

im.save(OUT, 'JPEG', quality=86, exif=exif, optimize=True)
print('wrote', OUT, im.size)
