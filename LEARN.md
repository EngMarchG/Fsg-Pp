Welcome to Fsg-Pp's learning guide! The goal of this document is to provide you additional contect on how the project works.

## Components of the program

### 1. Interface
    1. The UI uses gradio's gr.TabItems, which are then joined together by gr.Tabs. Gradio offers a flexible interface with many popular features such as asynchronous behavior and concurrency.


### 2. Workflow
    1. The idea of the program is to open a browser in the background and search for your specified term on the predefined websites and download it, depending on your filters.
    2. AI mode, more accurately uses a pre-trained deeplearning model, which is the state-of-the-art model which promises high accuracy while maintaining quick inference, even on CPUs! This design choice has been chosen due to the nature of the task.
    3. Classification takes place at the size of 256x256 pixels. This is due to the size of thumbnails typically being around that size. Additionally, using thumbnails is more beneficial for both the user and the website by avoiding wasteful data usage.
    4. The second model, face detection, takes the index of the picture in which the gallery is displaying and sends it over to the the autocrop tab. The model then downscales the image to 256x256 and crops the correct portion of the size, before rescaling the box to fit the original image. Once again, this results in slightly less accuracy, but more convience.


### 3. Results
    1. The results are quite satisfactory considering the size of the model and its convienience. The models will be updated every once in awhile with the announcement of yolov9 and other breakthroughs in deep learning.