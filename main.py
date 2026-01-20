from os import getcwd,path,remove,listdir,makedirs
from shutil import rmtree
import requests
import zipfile
from subprocess import Popen, CREATE_NEW_PROCESS_GROUP,DETACHED_PROCESS
OSO_DIR = path.join(getcwd()[:2],"/Oslivion/","OSO")
if not OSO_DIR:
    makedirs(OSO_DIR)

files = listdir(OSO_DIR)
print(files)
print("Clearing files...")
for file in files:
    filepath = path.join(OSO_DIR,file)
    dir = path.isdir(filepath)
    if not (dir and file == "quickaccess"):
        if dir:
            rmtree(filepath)
        else:
            remove(filepath)

print("Cleared out files in OSO dir\n\nDownloading latest release...")
OSO_DL = requests.get("https://github.com/loplxl/OSlivionOptions/releases/latest/download/OSO.zip",stream=True)
OSO_DL.raise_for_status()
ZIP_PATH = path.join(path.dirname(OSO_DIR),"OSO.zip") #put zip in parent dir
with open(ZIP_PATH,'wb') as f:
    for chunk in OSO_DL.iter_content(chunk_size=8192):
        f.write(chunk)
print("Finished downloading latest release\n")

while len(listdir(OSO_DIR)) > 1: #wait for files to finish being deleted (if they are)
    print(len(listdir(OSO_DIR)))
    pass

print("Files are confirmed deleted, unzipping contents...")
with zipfile.ZipFile(ZIP_PATH,'r') as ZIP_REF:
    ZIP_REF.extractall(path.dirname(ZIP_PATH))
print("Unzipped contents\n\nLaunching new version...")

OSO_EXE_DIR = path.join(OSO_DIR,"OSO.exe")
while not path.exists(OSO_EXE_DIR): #wait for oso.exe to exist
    pass
Popen(OSO_EXE_DIR.split(" "),creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,close_fds=True)
print("New version started\n\nSafely exiting")