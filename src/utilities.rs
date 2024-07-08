use std::{fs, io};
use std::io::Write;
use std::path::Path;
use crate::core::{CONFIG, SPKG_DIRECTORIES};

pub fn open_file(path: &str) -> String {
    fs::read_to_string(path).expect("Could not read file")
}

pub fn delete_last_line() {
    print!("\x1b[1A");
    print!("\x1b[2K");
    io::stdout().flush().unwrap();
}

pub fn get_language_strings() -> String {
    open_file(format!("{}{}.yml", &SPKG_DIRECTORIES.language_files, CONFIG.language).as_str())
}

pub fn get_basename(path: &str) -> Option<String> {
    let path = Path::new(path);
    path.file_name()?.to_str().map(|s| s.to_string())
}