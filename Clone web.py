import os
import requests
import tkinter as tk
from bs4 import BeautifulSoup
from tkinter import ttk, messagebox
from urllib.parse import urlparse, urljoin
from threading import Thread

class WebCloner:
    def __init__(self, root):
        self.root = root
        self.root.title("Clone web")
        self.missing_files = 0

        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Add a label
        label = tk.Label(root, text="Entrez l'URL du site à cloner", padx=10, pady=10)
        label.grid(row=0, column=0, sticky="W")

        # Add a text entry for the URL
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=1, column=0, padx=10, pady=10, sticky="EW")

        # Add a progress bar
        self.progress = ttk.Progressbar(root, length=200, mode='indeterminate')
        self.progress.grid(row=2, column=0, padx=10, pady=10, sticky="EW")

        # Add a button to start the cloning
        clone_button = tk.Button(root, text="Cloner le site", command=self.start_cloning)
        clone_button.grid(row=3, column=0, padx=10, pady=10, sticky="EW")

        # Add a label to display the value of self.missing_files
        self.missing_files_label = tk.Label(root, text="", padx=10, pady=10)
        self.missing_files_label.grid(row=4, column=0, sticky="W")

    def start_cloning(self):
        web_url = self.url_entry.get()
        self.progress.start()
        Thread(target=self.clone_website, args=(web_url,)).start()
        self.statut = True
        Thread(target=self.umf).start()

    def umf(self):
        while self.statut:
            self.missing_files_label.config(text=f"Fichiers manquants : {self.missing_files}")

    def clone_website(self, web_url):
        try:
            r = requests.get(web_url)
        except:
            self.progress.stop()
            self.statut = False
            return messagebox.showwarning(title="Clone Web", message="Il semblerait que votre lien ait un problème..")
        parsed_url = urlparse(web_url)

        site_name = parsed_url.netloc
        html_content = r.text
        os.makedirs(site_name, exist_ok=True)

        # Check if the request was successful
        if r.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(r.text, "html.parser")

            # Go through all <img> tags and download the images
            for img_tag in soup.find_all("img"):
                # Get the image URL
                img_url = img_tag.get("src")

                # Download the image and save it locally
                if img_url:
                    img_response = requests.get(urljoin(web_url, img_url))
                    if img_response.status_code == 200:

                        # Extract the path of the parent directory
                        dir_path = os.path.dirname(f"./{site_name}/{img_url}")

                        # Check if the parent directory already exists
                        if not os.path.exists(dir_path):
                            # Create all necessary folders
                            os.makedirs(dir_path, exist_ok=True)

                        with open(f"./{site_name}/{img_url}", "wb") as f:
                            f.write(img_response.content)
                        print(f"L'image {img_url} a été téléchargée avec succès.")
                    else:
                        self.missing_files += 1
                        print(f"Impossible de télécharger l'image {img_url}.")

            # Go through all <link> tags and download the stylesheets
            for link_tag in soup.find_all("link", rel="stylesheet"):
                # Get the stylesheet URL
                css_url = link_tag.get("href")

                # Download the stylesheet and save it locally
                if css_url:
                    css_response = requests.get(urljoin(web_url, css_url))
                    if css_response.status_code == 200:

                        # Extract the path of the parent directory
                        dir_path = os.path.dirname(f"./{site_name}/{css_url}")

                        # Check if the parent directory already exists
                        if not os.path.exists(dir_path):
                            # Create all necessary folders
                            os.makedirs(dir_path, exist_ok=True)

                        with open(f"./{site_name}/{css_url}", "wb") as f:
                            f.write(css_response.content)
                        print(f"La feuille de style {css_url} a été téléchargée avec succès.")
                    else:
                        self.missing_files += 1
                        print(f"Impossible de télécharger la feuille de style {css_url}.")

            # Go through all <script> tags and download the scripts
            for script_tag in soup.find_all("script"):
                # Get the script URL
                script_url = script_tag.get("src")

                # Download the script and save it locally
                if script_url:
                    script_response = requests.get(urljoin(web_url, script_url))
                    if script_response.status_code == 200:

                        # Extract the path of the parent directory
                        dir_path = os.path.dirname(f"./{site_name}/{script_url}")

                        # Check if the parent directory already exists
                        if not os.path.exists(dir_path):
                            # Create all necessary folders
                            os.makedirs(dir_path, exist_ok=True)

                        with open(f"./{site_name}/{script_url}", "wb") as f:
                            f.write(script_response.content)
                        print(f"Le script {script_url} a été téléchargé avec succès.")
                    else:
                        self.missing_files += 1
                        print(f"Impossible de télécharger le script {script_url}.")

            # Create a set to store already processed URLs
            processed_urls = set()

            # Recursive function to find and copy all pages of the website
            def copy_site_pages(page_url):
                # Send a GET request to retrieve the page
                page_response = requests.get(page_url)

                # Check if the request was successful
                if page_response.status_code == 200:
                    # Parse the HTML content of the page
                    page_soup = BeautifulSoup(page_response.text, "html.parser")
                    
                    # Find all links to other pages on the same website
                    for link in page_soup.find_all("a"):
                        href = link.get("href")
                        if href:
                            href = urljoin(page_url, href)
                            parsed_href = urlparse(href)
                            if parsed_href.netloc == site_name and parsed_href.path not in processed_urls:
                                # Add the URL to the set of already processed URLs
                                processed_urls.add(parsed_href.path)

                                # Create the folder to save the page
                                page_dir_path = os.path.join(site_name, os.path.dirname(parsed_href.path))
                                os.makedirs(page_dir_path, exist_ok=True)

                                # Send a GET request to retrieve the page and save it locally
                                page_response = requests.get(href)
                                if page_response.status_code == 200:
                                    # Get the base name of the path to use as the file name
                                    file_name = os.path.basename(parsed_href.path)
                                    # Add .html extension if necessary
                                    if not file_name.endswith('.html'):
                                        file_name += '.html'
                                    page_path = os.path.join(page_dir_path, file_name)
                                    try:
                                        with open(f"./{site_name}./{page_path}", "wb") as f:
                                            f.write((page_response.text).encode("utf-8"))
                                    except:
                                        self.missing_files += 1
                                    print(f"La page {page_path} a été enregistrée avec succès.")

                                    # Recursively find and copy other pages on the website
                                    copy_site_pages(href)
                                else:
                                    self.missing_files += 1
                                    print(f"Impossible de récupérer la page {href}.")
                else:
                    self.missing_files += 1
                    print(f"Impossible de récupérer la page {page_url}.")
                    
            # Call the function to copy all pages on the website
            copy_site_pages(web_url)
        else:
            print("La requête a échoué avec le code d'état: ", r.status_code)
        self.progress.stop()
        self.statut = False

# Create the main window
root = tk.Tk()

# Create the web cloner
cloner = WebCloner(root)

# Start the tkinter main loop
root.mainloop()