import zipfile
import os
from pathlib import Path

# Paths
base_dir = Path("C:/Users/R5 5600 GT/.gemini/antigravity/scratch/resource_command")
zip_path = base_dir.parent / "Resource_Command_Audit_Pack_v2.0_AUDIT_READY.zip"

files_to_include = [
    ("boundless_prover.py", base_dir / "boundless_prover.py"),
    ("demo_server.py", base_dir / "demo_server.py"),
    (".env.example", base_dir / ".env.example"),
    ("test_demo_api.py", base_dir / "test_demo_api.py"),
    ("circuits/compliance_guest/src/main.rs", base_dir / "circuits/compliance_guest/src/main.rs"),
    ("circuits/compliance_guest/Cargo.toml", base_dir / "circuits/compliance_guest/Cargo.toml"),
]

print(f"Creating Audit Pack zip at: {zip_path}")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for arcname, file_path in files_to_include:
        if file_path.exists():
            zipf.write(file_path, arcname)
            print(f"  Added: {arcname}")
        else:
            print(f"  WARNING: File not found {file_path}")

print("Pack completed successfully!")
