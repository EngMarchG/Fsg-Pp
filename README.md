# Fsg_Pp

Finally some good profile pictures!

Got tired of constantly searching for new profile pictures?
Or maybe even just the thought of changing it is a hassle.

Well, Fsg_Pp aims to automate that for you!
Just type what you want to find and it will filter out the best ones for you!
[<img src="/../public/assets/images/finally.png" width="350" />](/../public/assets/images/finally.png)

## Quick Links
- [Installing and Running](#installing-and-running)
- [Features](#features)
    - [AI Mode](#ai-mode)
    - [Automatic Crop](#automatic-crop)
    - [Image Search](#image-search)
    - [Pixiv](#pixiv)
    - [Danbooru](#danbooru)
    - [Zerochan](#zerochan)
- [Manual Installation](#manual-installation)
    - [Windows](#windows)
    - [macOS/Linux](#macoslinux)
- [Questionable Ideas](#questionable-ideas)
- [Troubleshooting](#troubleshooting)
- [Acknowledgment](#acknowledgment)
- [Disclaimer](#disclaimer)

## Installing and Running

1. Install Python (Recommend 3.10.7 and higher), while checking "Add Python to PATH"

2. Install git 
   > **Note** Skip steps 2 and 3 if you would like to download the release here [Fsg-Pp releases](https://github.com/EngMarchG/Fsg-Pp/releases)

3. Clone the repo ```git clone https://github.com/EngMarchG/Fsg_Pp.git```       

    > **Note**
    > If you prefer to install the requirements manually, please head to [Manual Installation](#manual-installation)

4. Run the installation.bat(Windows)/installation.sh(macOS/linux) and it will set everything up for you! 

    > **Warning**
    > to run installation.sh and launcher.sh on macOS/linux, run the following in your terminal at the current folder containing the scripts; else scripts will fail:

   To give permissions for the scripts to run:
   
        chmod 755 installation.sh
        chmod 755 launcher.sh
        
   Finally, to run the scripts:
   
        ./installation.sh
        ./launcher.sh

5. After installation.bat(Windows)/installation.sh(macOS/linux) has successfully finished, run launcher.bat(Windows)/launcher.sh(macOS/linux)

    > **Note**
    > To close the script process, press CTRL+C

# Features

## AI Mode 
![AI Mode GIF](/../public/assets/gifs/ai_class.gif)  

Uses a pretrained model to classify images suitable to be used as a profile picture.
Note: AI mode usually attempts to classify images based on the thumbnail (this is beneficial for both the website and the user)

## Automatic Crop 

Automatically detect faces and crop your images! Just drag and drop or click to upload an image.  

![Automatic Crop GIF](/../public/assets/gifs/autocrop.gif)


## Image Search

This app currently allows you to search for images using three sites:

 1. Pixiv
 2. Danbooru
 3. Zerochan


## Pixiv
![Pixiv PNG](/../public/assets/images/pixiv.png)
- Allows the searching of preview premium images and free images
- Restricts the search type to SFW and NSFW images 
    - If you are not logged in pixiv only offers SFW images
    - Default queries are based on account settings, so be sure R-18 is enabled if you want to use it
- Filter by Likes, bookmarks and/or views
- Download images in the standard or native size
- Continue on the previous page it ended or if it crashes (Ignores current query when checked)
>**Note:** Pixiv search will ignore your option filters if you are not logged in.  

## Danbooru
![Danbooru PNG](/../public/assets/images/danbooru.png)
- Allows downloading images that are ordered by Score
- Allows filtering by tags (both inclusions and exclusions)
- Has 3 modes of image restrictions gradually increasing the PG-Friendliness of the images found (More Pg < Sensitive < Strictly PG)
- Continue on the previous page it ended or if it crashes (Ignores current query when checked)

## Zerochan
![Zerochan PNG](/../public/assets/images/zerochan.png)
- Filter by Likes 
- Continue on the previous page it ended or if it crashes (Ignores current query when checked)  
>**Note:** It is better to make the query specific such as using the character's full name. Ex: Searching 'Honkai' would fail due to the existance of several similar names. Searching 'Honkai star rail', on the other hand, would work since it is more specific and wouldn't get mixed up with other names.


 
## Manual Installation
   
  To install the requirements manually on Windows, please use the following commands: 
  
 ### Windows
 
   Right click in the installed folder and open a new windows terminal
 
   Activate the Python environment:
    
    python -m venv venv


   Activate the virtual environment:
    
    venv\Scripts\activate.bat


   Install dependencies from requirements.txt:
    
    venv\Scripts\python.exe -m pip install -r requirements.txt

      
   For GPU torch (NVIDIA GPUs Only, ROCm is currently not supported due to its limited support from pytorch):
      
    venv\Scripts\pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
    
    venv\Scripts\pip install ultralytics
      
   For CPU torch (Default):
      
    venv\Scripts\pip install ultralytics
     
   Check if cv_files folder exists, create if it doesn't:
    
    if not exist cv_files (
    mkdir cv_files
    )
    
   Install AniClassifier.pt and AniFaceDet.pt inside cv_files folder:
    
    cd cv_files
    
   Install AniClassifier.pt and AniFaceDet.pt inside cv_files folder:
    
    curl -L -o AniClassifier.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniClassifier.pt 
    
    curl -L -o AniFaceDet.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniFaceDet.pt
  
   To install the requirements manually on macOS/Linux, please use the following commands:
 ### macOS/Linux
 
   Create the Python virtual environment:
   
    python3 -m venv venv
    
   Activate the Python environment:
   
    source venv/bin/activate
    
   Install dependencies from requirements.txt:
    
    python3 -m pip install -r requirements.txt
    
   Install PyTorch with GPU support on Linux:
   
   (NVIDIA GPUs):
   
    python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
    
    python3 -m pip install ultralytics
    
   (AMD GPUs):
   
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2
    
    python3 -m pip install ultralytics
    
   Install Ultralytics using pip (macOS):
   
    python3 -m pip install ultralytics
   
   Install AniClassifier.pt and AniFaceDet.pt inside cv_files folder:
   
    cd cv_files
    curl -L -o AniClassifier.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniClassifier.pt
    curl -L -o AniFaceDet.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniFaceDet.pt
    
   Go back to the parent directory
        
    cd ..
    
   Deactivate the virtual environment
    
    deactivate
    
   > **Note**
   > GPU torch on macOS requires macOS 12.3 or later, for more info: [Accelerated PyTorch training on Mac](https://developer.apple.com/metal/pytorch/)

## Questionable Ideas

* Using NLP for better tag searching/filtering (particularly for danbooru)

* Pixiv: Search for a specific Artist's artworks


## Troubleshooting
   For Windows users, in case you have problems with the installation.bat, disable the aliases in Windows:
   ![python_windows](/../public/assets/images/python_windows.png)  
   If you are able to use python in the cmd, but can't run the script, then you probably have permission issues. In that case, refer to the manual installation guide or you can try to change your execution policies (not recommended)

   For macOS/Linux users, in case you face problems while running both launcher.sh and installation.sh, make sure the proper access is granted to these files by running the following commands in a terminal at the same folder of both files:
    
    chmod 755 launcher.sh
    chmod 755 installation.sh
    
   Then run the following to launch the scripts:
   
    ./installation.sh
    ./launcher.sh

> **Note**
> In case selenium is unable to locate a driver, put your custom chrome driver in the driver folder. The chrome driver must not exceed your installed chrome version.
    
## Acknowledgment

We would like to thank the authors of the following datasets for contributing to a portion of the face detector model's dataset:  

[Authors of the Anime Heads Dataset](https://universe.roboflow.com/nyuuzyou/animeheads)

[Authors of the Face Detection Dataset](https://universe.roboflow.com/commic/facedet-p5q5p/dataset)  

Special thanks to gradio for providing an intuitive and flexible UI.


## Disclaimer

The main objective of the application is, as the name implies, to download pictures that are suitable for use as profile pictures. 

Therefore, we will **NOT** be incorporating any type of multithreaded functionality. 

That said, users can still expect some performance improvements and optimizations.

Furthermore, if you appreciate the artists' artwork, please consider following their respective accounts. The chosen naming convention makes it easy to trace back to the artists.

