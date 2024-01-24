#!/bin/sh

# Check the Python version
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.10"
if [ "$(printf '%s\n' "$python_version" "$required_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Python 3.10 or higher is required. Please update your Python installation."
    read -p "Press Enter to close the window..."
    exit 1
fi

# Set the current directory to the script's location
cd "$(dirname "$0")"

# Check if the venv directory exists
if [ -d "venv" ]; then
    # Ask the user if they want to delete the venv directory
    read -p "The venv directory already exists. Do you want to delete it? (y/n): " choice

    if [[ "$choice" == [Yy]* ]]; then
        # Delete the venv directory
        echo "Deleting the venv directory..."
        rm -rf venv
    fi
fi

# Create the Python virtual environment using python -m venv venv
echo "Creating Python virtual environment..."
python3 -m venv venv

# Check if virtual environment creation failed and try using python3 if necessary
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment using python -m venv venv."
    echo "Attempting to create virtual environment using python3 -m venv venv..."
    python3 -m venv venv
fi

# Check if virtual environment creation still failed and exit the script
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment. Please make sure Python 3 is installed."
    read -p "Press Enter to continue..."
    exit 1
fi

# Activate the Python environment
source venv/bin/activate

# Install dependencies from requirements.txt
python3 -m pip install -r requirements.txt

# Check the operating system
os=$(uname -s)
install_gpu=false

if [[ "$os" == "Linux" ]]; then
    # Offer choice to install PyTorch with GPU on Linux
    read -p "Do you want to install PyTorch with GPU support? (y/n): " choice

    if [[ "$choice" == [Yy]* ]]; then
        install_gpu=true
    fi
fi

if [ "$install_gpu" = true ]; then
    # Install PyTorch with GPU support on Linux
    python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
    python3 -m pip install ultralytics==8.0.228
else
    # Install ultralytics==8.0.228 using pip
    python3 -m pip install ultralytics==8.0.228
fi


# Check if cv_files folder exists, create if it doesn't
if [ ! -d "cv_files" ]; then
  mkdir cv_files
fi

# Check if AniClassifier.pt already exists before downloading
if [ ! -f "cv_files/AniClassifier.pt" ]; then
  # Download AniClassifier.pt
  curl -L -o cv_files/AniClassifier.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniClassifier.pt
fi

# Check if AniFaceDet.pt already exists before downloading
if [ ! -f "cv_files/AniFaceDet.pt" ]; then
  # Download AniFaceDet.pt
  curl -L -o cv_files/AniFaceDet.pt https://huggingface.co/datasets/Kyo-Kai/Fsg_pp_files/resolve/main/AniFaceDet.pt
fi


# Deactivate the virtual environment
deactivate

# Check the exit code of the previous command
if [ $? -ne 0 ]; then
    echo "An error occurred while running the script."
    read -p "Press Enter to continue..."
else
    echo "Installation is complete."
    read -p "Press any key to close the window..."
fi
