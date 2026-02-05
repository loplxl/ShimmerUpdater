    
use std::{
    env::{current_dir, var},
    fs,
    io::{copy, Write},
    path::{Path, PathBuf},
    process::Command
};

use std::os::windows::process::CommandExt;

use reqwest::blocking::get;
use zip::ZipArchive;

const STEPS: f32 = 9.0; //total steps to update
static mut STEPS_COMPLETE: u8 = 0;
const CREATE_NO_WINDOW: u32 = 0x08000000;
const DETACHED_PROCESS: u32 = 0x00000008;

fn taskkill(executable:&str) -> Option<i32> {
    let cmd = Command::new("cmd")
        .args(&["/C", "taskkill", "/f", "/t", "/im", executable])
        .creation_flags(CREATE_NO_WINDOW) //create no window
        .status().expect(&format!("Failed to get status from {}",executable));
    loop {
        let check = Command::new("tasklist")
            .args(&["/FI",(&format!("IMAGENAME eq {}",executable))])
            .output()
            .expect("Failed to run tasklist");
        if String::from_utf8_lossy(&check.stdout).contains("No tasks are running") {
            break; 
        } else { stage(&format!("Waiting for {}",executable),false); }
    }
    return cmd.code();
}

fn run_detached(path: PathBuf) {
    Command::new(&path)
        .creation_flags(DETACHED_PROCESS) //detached process
        .spawn()
        .expect(&format!("Failed to run detached {}",path.display()));
}

fn stage(msg: &str,progress: bool) {
    unsafe {
        if progress == true { STEPS_COMPLETE += 1; }
        let progress = (STEPS_COMPLETE as f32 / STEPS) * 100.0;
        let extra_space_count: usize = (progress as u8).to_string().len();
        let extra_spaces = " ".repeat(4 - extra_space_count);
        println!("{:.1}%{}│ {}", progress, extra_spaces, msg);
    }
}

fn current_drive() -> PathBuf {
    let dir = current_dir().unwrap();
    PathBuf::from(dir.components().next().unwrap().as_os_str()).join("\\")
}

fn download_shimmer(directory: &PathBuf) -> PathBuf {
    let target: &str = "https://github.com/loplxl/ShimmerOS/releases/latest/download/Shimmer.zip";
    let response = get(target).expect("Failed to download Shimmer.zip");
    let bytes = response.bytes().expect("Failed to get bytes from response");
    let zip_path = directory.join("Shimmer.zip");
    let mut zip_file = fs::File::create(&zip_path).expect("Failed to write Shimmer.zip");
    zip_file.write_all(&bytes).expect("Failed to write all to zipfile");
    return zip_path;
}

fn extract_shimmer(directory: &PathBuf, zipfile: fs::File) {
    let mut archive = ZipArchive::new(zipfile).expect("Failed to archive zipfile");
    { //use shimmer.exes own scope because you cant use 2 references to the same archive in 1 scope
        let mut shimmer_exe = archive.by_name("Software\\Shimmer.exe").expect("Failed to find Shimmer.exe in archive by name");
        let mut output_file = fs::File::create(directory.join("Shimmer.exe")).expect("Failed to create output file for Shimmer.exe from archive");
        copy(&mut shimmer_exe, &mut output_file).expect("Failed to extract Shimmer.exe");
        drop(shimmer_exe);
        drop(output_file);
    }

    {
        for i in 0..archive.len() {
            let mut file = archive.by_index(i).expect("Failed to find file by index in archive");
            let name: &str = file.name();
            if !name.starts_with("Software\\_internal") { continue }
            let rel_path = Path::new(name)
                .strip_prefix("Software")
                .unwrap();
            let output_path = directory.join(rel_path);
            if file.is_dir() {fs::create_dir_all(output_path).expect("Failed to create directory for _internal file."); continue; }

            //create directories above the file if they dont already exist
            if let Some(parent) = output_path.parent() { std::fs::create_dir_all(parent).expect("Failed to create directory for _internal file."); }

            let mut output_file = fs::File::create(&output_path).expect("Failed to create output file");
            copy(&mut file, &mut output_file).expect("Failed to extract file");
        }
    }
}

fn main() {
    println!("└──────┤ Shimmer Updater");
    // Setup to ensure compatibility
    let shimmer_dir:  PathBuf = current_drive().join("Shimmer");
    let software_dir: PathBuf = shimmer_dir.join("Software");
    fs::create_dir_all(&software_dir).expect("Unable to create software dir"); //use &software_dir so i can reuse software_dir later
    stage("Ensured software directories exist",true);

    let old_zip_path: PathBuf = software_dir.join("Shimmer.zip");
    if old_zip_path.exists() { fs::remove_file(old_zip_path).expect("Unable to remove old Shimmer.zip file (it might not exist)");}

    let zip_path = download_shimmer(&software_dir);
    stage(&format!("Downloaded Shimmer.zip to {}", &software_dir.display()),true);

    // Kill shimmer/settimerresolution to ensure that you can delete folders next step
    taskkill("Shimmer.exe");
    stage("Killed Shimmer.exe",true);
    let str_exe_code: i32 = taskkill("SetTimerResolution.exe").unwrap();
    stage(&format!("Killed SetTimerResolution.exe with exit code {}",str_exe_code),true);
    let internal_dir: PathBuf = software_dir.join("_internal");
    if internal_dir.exists() {
        for entry in walkdir::WalkDir::new(&internal_dir)
            .into_iter()
            .filter_map(|e: std::result::Result<walkdir::DirEntry, walkdir::Error>| e.ok())
            .filter(|e| e.path().is_file())
        {
            match fs::remove_file(entry.path()) {
                Ok(_) => (),
                Err(e) => println!("Could not remove {}: {:?}", entry.path().display(), e),
            }
        }
    }
    stage("Deleted _internal directory",true);

    let executable_dir: PathBuf = software_dir.join("Shimmer.exe");
    if executable_dir.exists() { fs::remove_file(executable_dir).expect("Unable to remove Shimmer.exe file");}
    stage("Deleted Shimmer.exe file",true);

    let zipfile = fs::File::open(&zip_path).expect("Failed to open downloaded ZIP file");
    let _ = extract_shimmer(&software_dir,zipfile);
    stage("Extracted Shimmer.exe and _internal dir from Shimmer.zip",true);

    run_detached(software_dir.join("Shimmer.exe"));
    stage("Running Shimmer.exe",true);
    if str_exe_code == 0 {
        let appdata = var("APPDATA").expect("Failed to find APPDATA");
        let mut shortcut_path = PathBuf::from(appdata);
        shortcut_path.push("Microsoft\\Windows\\Start Menu\\Programs\\Startup\\SetTimerResolution.exe.lnk");
        Command::new("cmd")
        .args(&["/C","start","",shortcut_path.to_str().unwrap(),])
        .creation_flags(DETACHED_PROCESS | CREATE_NO_WINDOW)
        .spawn().expect("Failed to restart timer resolution shortcut.");
    }
    stage("Complete, you can now exit this window.",true);
}
