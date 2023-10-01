#!/usr/bin/env python3

"""
    Copyright (C) 2023  Juliandev02

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses>
"""

import os
import time
import json
import sqlite3 as sql
import urllib.request
import platform
import requests

from sqlite3 import *
from urllib.error import HTTPError
from colorama import Fore
from halo import Halo
from sys import exit
from init import *

language = config['language']


if language == "de":
    PackageNotFound = f"{Fore.RED + Colors.BOLD}[E]{Fore.RESET} Paket wurde nicht gefunden{Colors.RESET}"
    FinishedDownloading = f"Download abgeschlossen für"
    StrGet = "Holen"
    UnknownError = f"{Fore.RED + Colors.BOLD}[?]{Fore.RESET} Unbekannter Fehler{Colors.RESET}"
    Canceled = f"{Fore.RED + Colors.BOLD}[!!!]{Fore.RESET} Prozess wurde abgebrochen!{Colors.RESET}"
    PackageDatabaseNotSynced = f"{Fore.RED + Colors.BOLD}[!]{Fore.RESET} Die Paketdatenbank wurde noch nicht synchronisiert. Führe {Fore.CYAN}spkg sync{Fore.RESET} aus, um die Datenbank zu synchronisieren{Colors.RESET}"
    SearchingDatabaseForPackage = f"{Colors.BOLD}Durchsuche Datenbank nach Paket ...{Colors.RESET}"
    ContinePackageInstallation1 = f"{Colors.RESET}Das Paket {Fore.CYAN + Colors.BOLD}"
    ContinePackageInstallation2 = f"{Colors.RESET} wird nun heruntergeladen. \nDafür müssen "
    ContinePackageInstallation3 = f"{Colors.RESET} heruntergeladen werden. Fortfahren? [J/N]{Fore.RESET}{Colors.RESET}"
    Abort = "Abbruch ... "


elif language == "en":
    PackageNotFound = f"{Fore.RED  + Colors.BOLD}[E]{Fore.RESET} Package not found{Colors.RESET}"
    FinishedDownloading = f"Finished downloading"
    StrGet = "Get"
    UnknownError = f"{Fore.RED + Colors.BOLD}[?]{Fore.RESET} Unknown Error{Colors.RESET}"
    Canceled = f"{Fore.RED + Colors.BOLD}[!!!]{Fore.RESET} Process canceled!{Colors.RESET}"
    PackageDatabaseNotSynced = f"{Fore.RED + Colors.BOLD}[!]{Fore.RESET} The package database has not been synchronized yet. Run {Fore.CYAN}spkg sync{Fore.RESET} to synchronize the database{Colors.RESET}"
    SearchingDatabaseForPackage = f"{Colors.BOLD}Searching through the database ...{Colors.RESET}"
    ContinePackageInstallation1 = f"{Colors.RESET}The package {Fore.CYAN + Colors.BOLD}"
    ContinePackageInstallation2 = f"{Colors.RESET} will now be downloaded. \nThis requires "
    ContinePackageInstallation3 = f"{Colors.RESET} to be downloaded. Continue? [Y/N]{Fore.RESET}{Colors.RESET}"
    Abort = "Aborting ..."


if arch == "x86_64":
    arch = "amd64"

elif arch == "x86":
    arch = "i386"

elif arch == "aarch64":
    arch = "arm64"
    
def download(name):
    spinner_db = Halo(text=f"{SearchingDatabaseForPackage}", spinner={'interval': 150, 'frames': [
                       '[-]', '[\\]', '[|]', '[/]']}, text_color="white", color="green")
    spinner_db.start()
    
    c.execute("SELECT arch FROM packages where name = ?", (name,))
    
    try:
        result = c.fetchone()[0]
        
    except TypeError:
        print(PackageNotFound)
        exit()
    
    if result == "all":
        try:
            c.execute("SELECT name, fetch_url, file_name FROM packages where name = ?", (name,))
        
        except OperationalError:
            print(PackageDatabaseNotSynced)
            exit()
        
    else:
        try:
            c.execute("SELECT name, fetch_url, file_name FROM packages where name = ? AND arch = ?", (name, arch))
            
        except OperationalError:
            print(PackageDatabaseNotSynced)
            exit()
    
    
    for row in c:
        url = row[1]
        filename = row[2]
        
        response = requests.head(url)
        file_size_bytes = int(response.headers.get('Content-Length', 0))
        file_size_mb = file_size_bytes / (1024 * 1024)

    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        )

        f = urllib.request.urlopen(req)
        
        spinner_db.stop()
        print(f"{Fore.GREEN + Colors.BOLD}[✓] {Fore.RESET + Colors.RESET}{SearchingDatabaseForPackage}")
        
        
        try:
            continue_pkg_installation = input(
                f"{ContinePackageInstallation1}{filename}{Colors.RESET}{ContinePackageInstallation2}{round(file_size_mb, 2)} MB{ContinePackageInstallation3} ")

        except KeyboardInterrupt as e:
            print(f"\n{Canceled}")
            exit()

        if continue_pkg_installation.lower() == "j":
            pass

        elif continue_pkg_installation.lower() == "y":
            pass

        else:
            print(Abort)
            exit()

        download_time_start = time.time()

        spinner = Halo(text=f"{StrGet}: {url}", spinner={'interval': 150, 'frames': [
                       '[-]', '[\\]', '[|]', '[/]']}, text_color="white", color="green")
        spinner.start()

        with open(filename, 'wb') as file:
            file.write(f.read())

        download_time_end = time.time()
        print(f"\n{FinishedDownloading} {Fore.LIGHTCYAN_EX + Colors.BOLD}{filename}{Colors.RESET} in {round(download_time_end - download_time_start, 2)} s{Colors.RESET}")
        spinner.stop()

    except HTTPError as e:
        print(Str[lang]["HttpError"])
        exit()

    except NameError as e:
        print(PackageNotFound)
        exit()
        
        
        
def download_compact(name):
    c.execute("SELECT arch FROM packages where name = ?", (name,))
    
    try:
        result = c.fetchone()[0]
        
    except TypeError:
        print(PackageNotFound)
        exit()
    
    if result == "all":
        try:
            c.execute("SELECT name, fetch_url, file_name FROM packages where name = ?", (name,))
        
        except OperationalError:
            print(PackageDatabaseNotSynced)
            exit()
        
    else:
        try:
            c.execute("SELECT name, fetch_url, file_name FROM packages where name = ? AND arch = ?", (name, arch))
            
        except OperationalError:
            print(PackageDatabaseNotSynced)
            exit()
    
        download_time_start = time.time()
    
    for row in c:
        url = row[1]
        filename = row[2]
        
        response = requests.head(url)
        file_size_bytes = int(response.headers.get('Content-Length', 0))
        file_size_mb = file_size_bytes / (1024 * 1024)

    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        )

        f = urllib.request.urlopen(req)

        spinner = Halo(text=f"{StrGet}: {url} ({round(file_size_mb, 2)} MB)", spinner={'interval': 150, 'frames': [
                       '[-]', '[\\]', '[|]', '[/]']}, text_color="white", color="green")
        spinner.start()

        with open(filename, 'wb') as file:
            file.write(f.read())

        print()
        
        spinner.stop()

    except HTTPError as e:
        print(Str[lang]["HttpError"])
        exit()

    except NameError as e:
        print(PackageNotFound)
        exit()
        
        
def download_compact_noarch(name): 
    try:
        c.execute("SELECT name, fetch_url, file_name FROM packages where name = ?", (name,))
    
    except OperationalError:
        print(PackageDatabaseNotSynced)
        exit()
    
    download_time_start = time.time()
    
    for row in c:
        url = row[1]
        filename = row[2]
        
        response = requests.head(url)
        file_size_bytes = int(response.headers.get('Content-Length', 0))
        file_size_mb = file_size_bytes / (1024 * 1024)

    try:
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        )

        f = urllib.request.urlopen(req)

        spinner = Halo(text=f"{StrGet}: {url} ({round(file_size_mb, 2)} MB)", spinner={'interval': 150, 'frames': [
                       '[-]', '[\\]', '[|]', '[/]']}, text_color="white", color="green")
        spinner.start()

        with open(filename, 'wb') as file:
            file.write(f.read())

        print()
        
        spinner.stop()

    except HTTPError as e:
        print(Str[lang]["HttpError"])
        exit()

    except NameError as e:
        print(PackageNotFound)
        exit()