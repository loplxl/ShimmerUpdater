try:
    from os import getcwd,path,remove,listdir,makedirs,environ
    from shutil import rmtree
    import requests
    from time import sleep
    import zipfile
    from subprocess import Popen, CREATE_NEW_PROCESS_GROUP,DETACHED_PROCESS,CREATE_NO_WINDOW,PIPE
    Popen(["taskkill","/f","/im","OSO.exe"],creationflags=CREATE_NO_WINDOW)
    Popen(["taskkill","/f","/im","SetTimerResolution.exe"],creationflags=CREATE_NO_WINDOW)
    print("Waiting to ensure OSO and SetTimerResolution are closed...")
    sleep(3)
    OSO_DIR = path.join(getcwd()[:2],"/Oslivion/","OSO")
    if not OSO_DIR:
        makedirs(OSO_DIR)

    print("Clearing files...")

    _internalPATH = path.join(OSO_DIR,"_internal")
    if path.exists(_internalPATH):
        rmtree(_internalPATH)
    OSO_EXE_DIR = path.join(OSO_DIR,"OSO.exe")
    if path.exists(OSO_EXE_DIR):
        remove(OSO_EXE_DIR)

    print("Cleared out files in OSO dir\n\nDownloading latest release...")
    OSO_DL = requests.get("https://github.com/loplxl/OSlivionOptions/releases/latest/download/OSO.zip",stream=True)
    OSO_DL.raise_for_status()
    ZIP_PATH = path.join(path.dirname(OSO_DIR),"OSO.zip") #put zip in parent dir
    with open(ZIP_PATH,'wb') as f:
        for chunk in OSO_DL.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Finished downloading latest release\n")

    while path.exists(OSO_EXE_DIR) or path.exists(path.join(OSO_DIR,"_internal")): #wait for files to finish being deleted (if they are)
        sleep(0.1)
        pass

    print("Files are confirmed deleted, unzipping contents...")
    with zipfile.ZipFile(ZIP_PATH,'r') as ZIP_REF:
        ZIP_REF.extractall(path.dirname(ZIP_PATH))
    print("Unzipped contents\n\nLaunching new version...")

    while not path.exists(OSO_EXE_DIR): #wait for oso.exe to exist
        sleep(0.1)
        pass
    Popen(OSO_EXE_DIR.split(" "),creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,close_fds=True)
    print("New version started")
    
    shortcutPath = path.join(environ['APPDATA'],r"Microsoft\Windows\Start Menu\Programs\Startup","SetTimerResolution.exe.lnk")
    Popen(['cmd', '/c', 'start', '', shortcutPath], shell=True)
except Exception as e:
    print("An error occured, please report this:\n",e)
    input()
