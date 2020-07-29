# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import codecs
import datetime
import mappyfile
import shutil
import tempfile
import git
import oerebLader.logging
import oerebLader.mapfile

def get_gemeinden_directories(directory):
    '''
    Ermittelt alle Gemeinden, für die
    im Repository Mapfiles vorliegen. Wird für
    den MODE=oereb verwendet, da im öffentlichen
    Dienst alle aufgeschalteten Gemeinden auf-
    tauchen sollen. Über das Release-Command wird
    gewährleistet, dass nur Mapfiles von auf-
    geschalteten Gemeinden in das oereb-Repository
    gelangen.
    Zurückgegeben wird eine Liste von Verzeichnissen.
    :param directory: Verzeichnis, in dem sich die gemeindespezifischen Mapfiles befinden
    '''
    gemeinden_directories = []
    for gd in os.listdir(directory):
        item = os.path.join(directory, gd)
        if os.path.isdir(item):
            gemeinden_directories.append(item)
    
    return gemeinden_directories
    
def get_gemeinde_mapfiles(gemeinde_directory):
    gemeinde_mapfiles = []
    for ff in os.listdir(gemeinde_directory):
        item = os.path.join(gemeinde_directory, ff)
        if os.path.isfile(item) and item.endswith(".map"):
            gemeinde_mapfiles.append(item)
            
    return gemeinde_mapfiles

def get_include_line(gemeinde_mapfile):
    bfsnr = gemeinde_mapfile[-7:-4]
    
    include_path = os.path.join("nupla", bfsnr, os.path.basename(gemeinde_mapfile))
    
    include_line = "INCLUDE \"" + include_path + "\""
    
    return include_line

def write_publish_batch(repo_dir, mapfile_path_de, mapfile_path_fr, publish_dir, batch_dir, publish2_dir, mode):
    '''
    Beim Aufruf von shp2img via subprocess kommt es immer zu 
    einem Fehler, der nicht eingegrenzt werden kann.
    Daher wurde der Test mit shp2img sowie auch gleich das
    Publizieren (d.h. Kopieren auf den Austausch-Share) via
    ein Batch-File gelöst.
    Somit wird hier nur ein Batch-File erzeugt, dass anschliessend
    ausserhalb des oerebLaders ausgeführt werden muss.
    '''
    png_file_de = os.path.join(batch_dir, "maptest_de.png")
    png_file_fr = os.path.join(batch_dir, "maptest_fr.png")
    # Die EXIT-Option bewirkt, dass es im Fehlerfall nach shp2img nicht weitergeht.
    cmd1 = "shp2img -e 2550300 1120800 2688900 1247400 -o " + png_file_de + " -s 1095 1000 -map_debug 2 -m " + mapfile_path_de + " || EXIT /B 1"
    cmd2 = "shp2img -e 2550300 1120800 2688900 1247400 -o " + png_file_fr + " -s 1095 1000 -map_debug 2 -m " + mapfile_path_fr + " || EXIT /B 1"
    cmd3 = "rmdir " + publish_dir + " /s /q"
    cmd4 = "mkdir " + publish_dir
    cmd5 = "xcopy " + repo_dir + "\* " + publish_dir + " /s /e"
    if mode == 'oerebpruef':
        cmd6 = "rmdir " + publish2_dir + " /s /q"
        cmd7 = "mkdir " + publish2_dir
        cmd8 = "xcopy " + repo_dir + "\* " + publish2_dir + " /s /e"
    batch_file_path = os.path.join(batch_dir, "publish.bat")
    with codecs.open(batch_file_path, "w", "utf-8") as batch_file:
        batch_file.write(cmd1)
        batch_file.write("\n")
        batch_file.write(cmd2)
        batch_file.write("\n")
        batch_file.write(cmd3)
        batch_file.write("\n")
        batch_file.write(cmd4)
        batch_file.write("\n")
        batch_file.write(cmd5)
        if mode == 'oerebpruef':
            batch_file.write("\n")
            batch_file.write(cmd6)
            batch_file.write("\n")
            batch_file.write(cmd7)
            batch_file.write("\n")
            batch_file.write(cmd8)
        
    return batch_file_path
    
    
def clone_master_repo(master_repo_dir, mode):
    tmpdir = tempfile.mkdtemp()
    cloned_repo = git.Repo.clone_from(master_repo_dir, tmpdir)
    return cloned_repo.working_dir

def run_build_map(mode, batch_dir):
    config = oerebLader.config.get_config()
    logger = oerebLader.logging.init_logging("build_map", config)
    logger.info("Das Mapfile des Dienstes " + mode + " wird erstellt.")
    
    # Config
    # =====================================================
    fonts_subdir = "fonts"
    templates_subdir = "templates"
    build_subdir = "build"
    images_subdir = "images"
    layers = []
    if mode in ("oereb", "oerebpreview", "oerebpruef"):
        for layer in config['KOMMUNALE_LAYER']:
            layers.append(layer['layer'].split(".")[1])
    master_repo_dir = config['REPOS'][mode]
    logger.info("Repository wird geklont.")
    repo_dir = clone_master_repo(master_repo_dir, mode)
    logger.info("Klon residiert in: " + repo_dir)
    publish_dir = os.path.join(config['REPOS']['mapfile_publish_directory'], mode)
    publish2_dir = os.path.join(config['LEGENDS']['legend_mapfile'], mode)
    # Da es ein oerebpreview-Repo nicht gibt, sondern stattdessen das
    # oereb-repo verwendet wird, braucht es eine zusätzliche Variable neben mode,
    # mit der im Preview-Fall im oereb-Repo die richtigen Pfade gefunden werden.  
    input_mode = mode
    if mode == 'oerebpreview':
        input_mode = 'oereb'
    # =====================================================
    
    build_dir = os.path.join(repo_dir, build_subdir, mode)
    template_mapfile_path = os.path.join(repo_dir, input_mode + "/" + input_mode + ".map")
    template_mapfile_temp_path = os.path.join(repo_dir, input_mode + "/" + input_mode + "_temp.map")
    output_mapfile_de_path = os.path.join(build_dir, mode + "_de.map")
    output_mapfile_fr_path = os.path.join(build_dir, mode + "_fr.map")
    
    # Build-Verzeichnis initialisieren
    logger.info("Build-Verzeichnis wird erstellt:" + build_dir)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # Fonts kopieren
    logger.info("Fonts kopieren...")
    src_fonts_dir = os.path.join(repo_dir, input_mode, fonts_subdir)
    dest_fonts_dir = os.path.join(build_dir, fonts_subdir)
    if os.path.exists(src_fonts_dir):
        shutil.copytree(src_fonts_dir, dest_fonts_dir)
    else:
        logger.info("Fonts-Directory ist leer, es wird nicht kopiert.")

    # Templates kopieren
    logger.info("Templates kopieren...")
    src_templates_dir = os.path.join(repo_dir, input_mode, templates_subdir)
    dest_templates_dir = os.path.join(build_dir, templates_subdir)
    if os.path.exists(src_templates_dir):
        shutil.copytree(src_templates_dir, dest_templates_dir)
    else:
        logger.info("Templates-Directory ist leer, es wird nicht kopiert.")    
    
    # Images kopieren
    logger.info("Images kopieren...")
    src_images_dir = os.path.join(repo_dir, input_mode, images_subdir)
    dest_images_dir = os.path.join(build_dir, images_subdir)
    if os.path.exists(src_images_dir):
        shutil.copytree(src_images_dir, dest_images_dir)
    else:
        logger.info("Images-Directory ist leer, es wird nicht kopiert.")

    logger.info("Template-Mapfile wird eingelesen: " + template_mapfile_path)
    with codecs.open(template_mapfile_path, "r", encoding="utf-8") as mapfile_raw:
        mapfile_raw_content = mapfile_raw.read()

    # Alles Gemeindespezifische gibts nicht für oerebav und oerebhinweis
    # Daher wird das hier abgefangen
    if mode in ("oereb", "oerebpreview", "oerebpruef"):
        # NUPLA-Includes bilden
        nupla_dir = os.path.join(repo_dir, input_mode + "/nupla")
        include_lines = []
    
        logger.info("Gemeindeliste ermitteln...")
        logger.info("Ermittle Gemeinden anhand der vorhandenen Gemeinde-Directories in " + nupla_dir)
        gemeinde_directories = get_gemeinden_directories(nupla_dir)
            
        for gemeinde in gemeinde_directories:
            for gemeinde_mapfile in get_gemeinde_mapfiles(gemeinde):
                include_line = get_include_line(gemeinde_mapfile)
                include_lines.append(include_line)
    
        logger.info("Strings werden ersetzt.")
        # #3399 Der Filter muss nicht mehr mit Thun ersetzt werden.
        # Er kann leer bleiben.
        mapfile_raw_content = mapfile_raw_content.replace("[[[BFSNR]]]","")
                
        for layer in layers:
            layer_include_search_string = "###" + layer +"###"
            layer_include_string = ""
            for il in include_lines:
                if layer in il:
                    layer_include_string += il + "\n"
            
            mapfile_raw_content = mapfile_raw_content.replace(layer_include_search_string, layer_include_string)
    
    logger.info("Temporäres Mapfile wird geschrieben: " + template_mapfile_temp_path)
    with codecs.open(template_mapfile_temp_path, "w", encoding="utf-8") as temp_mapfile:
        temp_mapfile.write(mapfile_raw_content)
    
    # Mapfile kopieren
    logger.info("Temporäres Mapfile wird mit mappyfile geparst.")
    mapfile_content_de = mappyfile.open(template_mapfile_temp_path)
    mapfile_content_fr = mappyfile.open(template_mapfile_temp_path)

    # Sprachunabhängige Parameter manipulieren
    
    # Stufe MAP
    mapfile_content_de = oerebLader.mapfile.fill_map_metadata(mapfile_content_de, mode, config)
    mapfile_content_fr = oerebLader.mapfile.fill_map_metadata(mapfile_content_fr, mode, config)
    
    # Stufe LAYER
    mapfile_content_de = oerebLader.mapfile.fill_layer_metadata(mapfile_content_de, mode, config)
    mapfile_content_fr = oerebLader.mapfile.fill_layer_metadata(mapfile_content_fr, mode, config)
        
    # Sprachabhängige Parameter manipulieren

    # Stufe MAP
    mapfile_content_de = oerebLader.mapfile.fill_map_language_metadata(mapfile_content_de, "de", mode, config)
    mapfile_content_fr = oerebLader.mapfile.fill_map_language_metadata(mapfile_content_fr, "fr", mode, config)
    
    # Stufe LAYER
    mapfile_content_de = oerebLader.mapfile.fill_layer_language_metadata(mapfile_content_de, "de", config)
    mapfile_content_fr = oerebLader.mapfile.fill_layer_language_metadata(mapfile_content_fr, "fr", config)
        
    logger.info("Deutsches Mapfile wird geschrieben: " + output_mapfile_de_path)
    with codecs.open(output_mapfile_de_path, "w", encoding="utf-8") as mapfile:
        mapfile.write(mappyfile.dumps(mapfile_content_de))

    logger.info("Französisches Mapfile wird geschrieben: " + output_mapfile_fr_path)
    with codecs.open(output_mapfile_fr_path, "w", encoding="utf-8") as mapfile:
        mapfile.write(mappyfile.dumps(mapfile_content_fr))
    
    logger.info("Das Mapfile liegt in: " + build_dir)
    
    write_publish_batch(build_dir, output_mapfile_de_path, output_mapfile_fr_path, publish_dir, batch_dir, publish2_dir, mode)
    