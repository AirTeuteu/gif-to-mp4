import os
print("\033[92mInit...\033[0m")
import subprocess
import shutil
import re
from PIL import Image, ImageSequence

# Paramètres
input_directory = os.getcwd()
temp_image_dir = "temp_images_gif"
    

    
def get_delay_first_frame(input_file_path):
    try:
        # Exécuter identify pour obtenir des informations sur l'animation Gif
        result = subprocess.run(['identify', '-format', '%T %f', input_file_path], capture_output=True, text=True)

        if result.returncode == 0:
            lines = result.stdout.splitlines()
            total_frames = len(lines) # Obtenez le nombre total de frames

            if total_frames > 0:
                # Obtenez le délai de la première frame (supposé identique pour toutes les frames)
                delay_first_frame = float(re.search(r'^([\d.]+)\s', lines[0]).group(1))
                return delay_first_frame
            else:
                print("Aucune frame trouvée dans le fichier Gif.")
        else:
            print(f"Erreur lors de l'exécution de identify: {result.stderr}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")



def convert_gif_to_mp4(input_file_path, output_file_path):
    
    print(f"  Création du repertoire temporaire...")
    os.makedirs(temp_image_dir, exist_ok=True)

    print(f"  Chargement de l'image...")
    img = Image.open(input_file_path)

    print(f"  Extraction des frames...")
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        frame.save(os.path.join(temp_image_dir, f"frame_{i + 1:05d}.png"), "PNG")

    nb_frames = i + 1  # Nombre total d'images extraites
    print(f"  {nb_frames} frames extraites...")

    delay_first_frame = get_delay_first_frame(input_file_path)
    print(f"  Delay frame : {delay_first_frame}")

    duration = nb_frames * delay_first_frame / 100.0  # Convertir en secondes
    print(f"  Durée : {duration}")

    fps = nb_frames / duration
    print(f"  FPS : {fps}")

    print(f"  Génération de la vidéo avec une durée totale de {duration} secondes et un framerate de {fps} fps...")
    if duration is not None and nb_frames is not None and fps is not None:
        subprocess.run(["ffmpeg", "-r", str(fps), "-i", f"{temp_image_dir}/frame_%05d.png",
                        "-c:v", "libx264", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                        "-pix_fmt", "yuv420p", "-loglevel", "error", output_file_path])
    else:
        print(f"\033[91mConversion ignorée pour {input_file_path} en raison de l'absence de FPS.\033[0m")
    
    print(f"  Suppression du repertoire temporaire...")
    shutil.rmtree(temp_image_dir)



try:
    files = [filename for filename in os.listdir(input_directory) if filename.endswith(".gif")]
    for i, filename in enumerate(files, start=1):
        input_file_path = os.path.join(input_directory, filename)
        output_file_path = os.path.join(input_directory, f"{os.path.splitext(filename)[0]}.mp4")
        print(f"\033[92m [{i}/{len(files)}] Début de conversion de {filename}\033[0m")
        convert_gif_to_mp4(input_file_path, output_file_path)
        print(f"\033[92m [{i}/{len(files)}] Conversion terminée pour {filename}\033[0m")
        print()
    print("\033[92mToutes les conversions sont terminées.\033[0m")
    print()
    input("\033[92m => Appuyez sur Entrée pour fermer la fenêtre...\033[0m")
except Exception as e:
    # Afficher l'erreur
    print(f"\033[91m Une erreur s'est produite: {e} \033[0m")
    # Ajouter une pause pour voir l'erreur avant de fermer
    input("Appuyez sur Entrée pour fermer la fenêtre...")
