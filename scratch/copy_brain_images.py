import shutil
import os

brain_dir = r"C:\Users\Marcio Fernando Maia\.gemini\antigravity\brain\dea24b1c-795d-446e-998b-c93e8d65d667"
dest_dir = r"D:\Loterias\AnalisePorPosicao-DiaDeSorte-Only\img"

os.makedirs(dest_dir, exist_ok=True)

media_files = [
    "media_dea24b1c-795d-446e-998b-c93e8d65d667_1779283506261.jpg",
    "media_dea24b1c-795d-446e-998b-c93e8d65d667_1779283541838.jpg",
    "media_dea24b1c-795d-446e-998b-c93e8d65d667_1779283943706.jpg"
]

# Copy the files
for idx, mf in enumerate(media_files, 1):
    src = os.path.join(brain_dir, ".tempmediaStorage", mf)
    if os.path.exists(src):
        # We will also save a copy under the name you requested to adapt
        shutil.copy(src, os.path.join(dest_dir, mf))
        print(f"Copied {mf} to {dest_dir}")
        if idx == 3: # Let's copy the last one as the specific requested name
            shutil.copy(src, os.path.join(dest_dir, "desdobramente-mega-sena-PARA-ADPTAR-PARA-O-DIA-DE--SORTE.jpeg"))
            print(f"Copied {mf} as desdobramente-mega-sena-PARA-ADPTAR-PARA-O-DIA-DE--SORTE.jpeg")
    else:
        # fallback to brain_dir directly
        src_fallback = os.path.join(brain_dir, mf)
        if os.path.exists(src_fallback):
            shutil.copy(src_fallback, os.path.join(dest_dir, mf))
            print(f"Copied {mf} from fallback to {dest_dir}")
            if idx == 3:
                shutil.copy(src_fallback, os.path.join(dest_dir, "desdobramente-mega-sena-PARA-ADPTAR-PARA-O-DIA-DE--SORTE.jpeg"))
        else:
            print(f"Source not found: {src} or {src_fallback}")
