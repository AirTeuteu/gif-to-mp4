import os
import subprocess
import shutil
print("\033[92mInit...\033[0m")
from PIL import Image, ImageSequence

# Paramètres
input_directory = os.getcwd()
temp_image_dir = "temp_images_gif"
    
try:
    

    def get_gif_fps(input_file_path):
        # Utiliser FFmpeg pour obtenir le framerate du fichier Gif
        result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", input_file_path], capture_output=True, text=True)

        if result.returncode == 0:
            try:
                # Convertir le framerate en nombre à virgule flottante
                fps = eval(result.stdout)
                print(f"   Framerate du fichier Gif : {fps} fps")
                return fps
            except (SyntaxError, TypeError):
                pass

        # En cas d'échec, retourner None pour indiquer qu'aucun FPS n'a été trouvé
        print(f"\033[91m Avertissement : Aucun FPS trouvé pour {input_file_path}.\033[0m")
        return None

    def convert_gif_to_mp4(input_file_path, output_file_path):
        
        print(f"  Création du repertoire temporaire...")
        os.makedirs(temp_image_dir, exist_ok=True)

        print(f"  Chargement de l'image...")
        img = Image.open(input_file_path)

        print(f"  Extraction des frames...")
        for i, frame in enumerate(ImageSequence.Iterator(img)):
            frame.save(os.path.join(temp_image_dir, f"frame_{i + 1:05d}.png"), "PNG")

        print(f"  Calcul du framerate...")
        gif_fps = get_gif_fps(input_file_path)

        print(f"  Génération de la vidéo...")
        if gif_fps is not None:
            subprocess.run(["ffmpeg", "-framerate", str(gif_fps), "-i", f"{temp_image_dir}/frame_%05d.png",
                            "-c:v", "libx264", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                            "-pix_fmt", "yuv420p", "-loglevel", "error", output_file_path])
        else:
            print(f"\033[91mConversion ignorée pour {input_file_path} en raison de l'absence de FPS.\033[0m")
        
        print(f"  Suppression du repertoire temporaire...")
        shutil.rmtree(temp_image_dir)

    gif_files = [filename for filename in os.listdir(input_directory) if filename.endswith(".gif")]
    for i, filename in enumerate(gif_files, start=1):
        input_file_path = os.path.join(input_directory, filename)
        output_file_path = os.path.join(input_directory, f"{os.path.splitext(filename)[0]}.mp4")
        print(f"\033[92m [{i}/{len(gif_files)}] Début de conversion de {filename}\033[0m")
        convert_gif_to_mp4(input_file_path, output_file_path)
        print(f"\033[92m [{i}/{len(gif_files)}] Conversion terminée pour {filename}\033[0m")
        print()
    print("\033[92mToutes les conversions sont terminées.\033[0m")
    print()
    input("\033[92m => Appuyez sur Entrée pour fermer la fenêtre...\033[0m")
except Exception as e:
    # Afficher l'erreur
    print(f"\033[91m Une erreur s'est produite: {e} \033[0m")
    # Ajouter une pause pour voir l'erreur avant de fermer
    input("Appuyez sur Entrée pour fermer la fenêtre...")