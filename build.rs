fn main() {
    println!("cargo:rerun-if-changed=icon.res");
    println!("cargo:rustc-link-arg=icon.res");
}
