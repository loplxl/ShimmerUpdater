try:
    from os import getcwd,path,remove,makedirs,environ
    from shutil import rmtree
    import requests
    from time import sleep
    import zipfile
    from subprocess import Popen, CREATE_NEW_PROCESS_GROUP,DETACHED_PROCESS,CREATE_NO_WINDOW,PIPE
    Popen(["taskkill","/f","/im","Shimmer.exe"],creationflags=CREATE_NO_WINDOW)
    Popen(["taskkill","/f","/im","SetTimerResolution.exe"],creationflags=CREATE_NO_WINDOW)
    print("Waiting to ensure Shimmer and SetTimerResolution are closed...")
    sleep(3)
    SHIMMER_DIR = path.join(getcwd()[:2],"/Shimmer")
    SOFTWARE_DIR = path.join(SHIMMER_DIR,"/Software")
    if not path.exists(SOFTWARE_DIR):
        makedirs(SOFTWARE_DIR)
    if not path.exists(SHIMMER_DIR):
        makedirs(SHIMMER_DIR)

    print("Clearing files...")

    _internalPATH = path.join(SHIMMER_DIR,"_internal")
    if path.exists(_internalPATH):
        rmtree(_internalPATH)
    SHIMMER_EXE_DIR = path.join(SHIMMER_DIR,"Shimmer.exe")
    if path.exists(SHIMMER_EXE_DIR):
        remove(SHIMMER_EXE_DIR)

    print("Cleared out files in Shimmer dir\n\nDownloading latest release...")
    SHIMMER_DL = requests.get("https://github.com/loplxl/Shimmer/releases/latest/download/Shimmer.zip",stream=True)
    SHIMMER_DL.raise_for_status()
    ZIP_PATH = path.join(path.dirname(SHIMMER_DIR),"Shimmer.zip") #put zip in parent dir
    with open(ZIP_PATH,'wb') as f:
        for chunk in SHIMMER_DL.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Finished downloading latest release\n")

    while path.exists(SHIMMER_EXE_DIR) or path.exists(path.join(SHIMMER_DIR,"_internal")): #wait for files to finish being deleted (if they are)
        sleep(0.1)
        pass

    print("Files are confirmed deleted, unzipping contents...")
    with zipfile.ZipFile(ZIP_PATH,'r') as ZIP_REF:
        ZIP_REF.extractall(path.dirname(ZIP_PATH))
    print("Unzipped contents\n\nLaunching new version...")

    while not path.exists(SHIMMER_EXE_DIR): #wait for shimmer.exe to exist
        sleep(0.1)
        pass
    Popen(SHIMMER_EXE_DIR.split(" "),creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,close_fds=True)
    print("New version started")
    
    TRES_DIR = path.join(environ['APPDATA'],r"Microsoft\Windows\Start Menu\Programs\Startup","SetTimerResolution.exe.lnk")
    if path.exists(TRES_DIR):
        Popen(['cmd', '/c', 'start', '', TRES_DIR], shell=True)
except Exception as e:
    print("An error occured, please report this:\n",e)
    input()
