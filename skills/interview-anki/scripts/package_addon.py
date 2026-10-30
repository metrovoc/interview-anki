# /// script
# requires-python = ">=3.10"
# ///
"""Package the auto_furigana add-on, with Janome bundled, as an .ankiaddon file.

  package_addon.py OUT.ankiaddon

Install it in Anki with Tools > Add-ons > Install from file, then restart Anki.
"""
import os, subprocess, sys, tempfile, zipfile

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "addon", "auto_furigana")

out = sys.argv[1]
with tempfile.TemporaryDirectory() as tmp:
    vendor = os.path.join(tmp, "vendor")
    subprocess.run(["uv", "pip", "install", "--quiet", "--target", vendor, "janome==0.5.0"], check=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(SRC):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", "vendor")]
            for f in files:
                path = os.path.join(root, f)
                z.write(path, os.path.relpath(path, SRC))
        for root, dirs, files in os.walk(os.path.join(vendor, "janome")):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                path = os.path.join(root, f)
                z.write(path, os.path.join("vendor", os.path.relpath(path, vendor)))
print(out, f"{os.path.getsize(out) / 1e6:.1f} MB")
