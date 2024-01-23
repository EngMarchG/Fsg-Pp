import os

driver_path = "driver"
folder_path = "Images"
driverPath = os.path.join(os.getcwd(), driver_path)
imagePath = os.path.join(os.getcwd(), folder_path)
if not os.path.exists(imagePath):
    os.makedirs(imagePath)
if not os.path.exists(driver_path):
    os.makedirs(driver_path)

try:
    if len(os.listdir(driverPath)) > 1:
        raise Exception("Put 1 driver only")
    elif os.listdir(driverPath)[0] != "driver.exe":
        os.rename(driverPath+"/"+"driver.exe")
except:
    pass
finally:
    executable_path = os.path.join(driverPath, 'driver.exe')


def imgList(mode=0):
    """
    Returns a list of image filenames in the specified format based on the mode.

    Args:
        mode (int, optional): Determines the format of the image filenames. 
                              If 0 (default), returns filenames without extensions (used for Danbooru).
                              If 1, returns filenames without suffixes after "_" (used for Pixiv).
                              If 2, returns all filenames as is (used for Zerochan and good for general sites).

    Returns:
        list: A list of image filenames in the specified format.
    """
    if mode==0: # Danbooru
        return [image.split(" ")[-1].split(".")[0] for image in os.listdir(imagePath) if image.split(".")[-1] in ["jpg","png","jpeg"]]
    if mode==1: # Pixiv
        return [image.split("_")[0] for image in os.listdir(imagePath) if image.split(".")[-1] in ["jpg","png","jpeg"]]
    if mode==2: # Zerochan
        return os.listdir(imagePath)