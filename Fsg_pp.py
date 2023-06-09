import numpy as np
import gradio as gr
import os
import commands.exec_path as exec_path
import commands.driver_instance as driver_instance
import inspect

from commands.universal import searchQuery
from ai.autocrop import autoCropImages
from sites.pixiv import getOrderedPixivImages
from sites.danbooru import getOrderedDanbooruImages
from sites.zerochan import getOrderedZerochanImages

def get_images(*args):
    global_imgz = args[-1]
    args = args[:-1]

    driver = driver_instance.create_driver(exec_path.executable_path)
        
    if len(args) == len(inspect.signature(getOrderedPixivImages).parameters)-2:
        global_imgz = getOrderedPixivImages(driver, exec_path, *args)
        print(global_imgz)
        return {imgz_global: global_imgz, pix_gallery: global_imgz}

    elif len(args) == len(inspect.signature(getOrderedDanbooruImages).parameters)-2:
        global_imgz = getOrderedDanbooruImages(driver, exec_path, *args)
        print(global_imgz)
        return {imgz_global:global_imgz, danb_gallery:global_imgz}

    elif len(args) == len(inspect.signature(getOrderedZerochanImages).parameters)-2:
        global_imgz = getOrderedZerochanImages(driver, exec_path, *args)
        print(global_imgz)
        return {imgz_global: global_imgz, zero_gallery: global_imgz}


def open_folder(folder_path, mode=0):
    folder_opened = os.path.abspath(folder_path)
    if mode:
        folder_opened = os.path.abspath(os.path.join(folder_path, "cropped"))
    os.system(f'open "{folder_opened}"' if os.name == 'posix' else f'explorer "{folder_opened}"')

imageIndex = 0

def get_select_index(evt: gr.SelectData):
    imageIndex=evt.index
    return evt.index

    
def send_number(indx,global_imgz): 
    imageIndex = indx
    return {imgz_global:global_imgz, image:global_imgz[int(imageIndex)], tabs:gr.Tabs.update(selected=0)}

def cropImages(image,crop_scale_factor):
    return autoCropImages(image,crop_scale_factor)

with gr.Blocks(css='style.css') as demo:
    imgz_global = gr.State([])
  
    with gr.Tabs(selected=1) as tabs:
        selected = gr.Number(label="Gallery Number",visible=False)
        folder_input = gr.Textbox(value="./Images/", label="Enter Folder Path", visible=False)
        
        # Automatic Crop Tab
        with gr.TabItem("Automatic Crop", id=0):
            with gr.Row():
                with gr.Column():
                    image = gr.Image(type="filepath")
                    crop_scale_factor = gr.Slider(0.5,3, value=1.2,step=0.1, label="Crop Scale Factor")
                with gr.Column():
                    outputImages = gr.Gallery(label="Cropped Image Preview")
                    outputImages.style(preview=True,object_fit="cover",container=True)
                    with gr.Row():
                        green_btn = gr.Button(label="Cropping Button",value="Crop Image").style(size='sm')
                        green_btn.click(cropImages, [image,crop_scale_factor],outputs=outputImages)
                        open_btn = gr.Button(label="Open Folder",value="Open 📁",variant='secondary').style(size='sm')
                        open_btn.click(fn=open_folder, inputs=[folder_input,crop_scale_factor])

        # Pixiv Tab
        with gr.TabItem("Pixiv", id=1):
            with gr.Row():
                with gr.Column():
                    searchQuery = gr.Textbox(label="Search Query", placeholder="Suggested to use the char's full name")
                    with gr.Row():
                        num_pics = gr.Slider(1,30, value=2, step=int, label="Number of Pictures")
                    with gr.Row():
                        num_pages = gr.Slider(1,50, value=1, step=int, label="Number of Pages")
                    with gr.Row():
                        with gr.Column():
                            with gr.Row():
                                searchTypes = gr.CheckboxGroup(["Premium Search","Freemium"], value=["Freemium"], label="Search Type", type="index", elem_id="pixiv")
                            with gr.Row():
                                viewRestriction = gr.CheckboxGroup(["PG","R-18"],label="Viewing Restriction (Default: Account Settings)",type="index",elem_id="viewing-restrictions")
                        with gr.Row(elem_id='button-row'):
                            green_btn = gr.Button(label="Search", value="Search")
                    with gr.Row():
                        imageControl = gr.CheckboxGroup(["Full Res", "Continue Search","Search by Oldest", "AI Classifier"], value=["Full Res"], label="Image Control", type="index",elem_id="pixiv-filters")
                    with gr.Row():
                        with gr.Row():
                            n_likes = gr.Number(value=0, label="Filter by Likes")
                        with gr.Row():
                            n_bookmarks = gr.Number(value=0, label="Filter by Bookmarks")
                        with gr.Row():
                            n_views = gr.Number(value=0, label="Filter by Views")
                    with gr.Row():
                            start_date = gr.Textbox(label="Start date", placeholder=("2016-01-22  YEAR-MONTH-DAY"))
                    with gr.Row():
                            end_date = gr.Textbox(label="End date", placeholder=("2022-09-22  YEAR-MONTH-DAY"))
                    with gr.Row():
                            user_name = gr.Textbox(label="Email", type="email", placeholder=("Account email for pixiv login"))
                    with gr.Row():
                            pass_word = gr.Textbox(label="Password", type="password",placeholder=("Account password for pixiv login"))
                    
                with gr.Column():
                    pix_gallery=gr.Gallery(label="Image Preview")
                    pix_gallery.style(preview=True,object_fit="cover",columns=5,container=True)
                    with gr.Row():
                        blue_btn = gr.Button(label="Auto Crop",value="Crop Selected Image",variant='secondary')
                        blue_btn.click(fn=send_number,inputs=[selected,imgz_global],outputs=[imgz_global, image, tabs])
                        open_btn = gr.Button(label="Open Folder",value="Open 📁",variant='secondary')
                        open_btn.click(fn=open_folder, inputs=folder_input)

            pix_gallery.select(get_select_index, None, selected)
            green_btn.click(get_images, [searchQuery, num_pics, num_pages,searchTypes,viewRestriction,imageControl,n_likes, n_bookmarks, n_views, 
                                    start_date,end_date, user_name, pass_word, imgz_global], outputs=[imgz_global,pix_gallery])


        # Danbooru Tab
        with gr.TabItem("Danbooru", id=2):
            with gr.Row():
                with gr.Column():
                    searchQuery = gr.Textbox(label="Search Query", placeholder="Suggested to use the char's full name")
                    with gr.Row():
                        num_pics = gr.Slider(1,20, value=2, step=int, label="Number of Pictures")
                    with gr.Row():
                        num_pages = gr.Slider(1,50, value=1, step=int, label="Number of Pages")
                    with gr.Row():
                        filters = gr.CheckboxGroup(["Score", "Exact Match", "More PG", "Sensitive", "Strictly PG", "AI Classifier"], label="Filters", type="index", elem_id="filtering")
                    with gr.Row():
                        imageControl = gr.CheckboxGroup(["Continue Search"], label="Image Control", type="index", elem_id="imageControl")
                    with gr.Row():
                        bl_tags = gr.Textbox(label="Tags to Filter", placeholder=("Add stuff like typical undergarments etc to ensure complete pg friendliness"),lines=2)
                    with gr.Row():
                        inc_tags = gr.Textbox(label="Tags to Include", placeholder=("1girl, 1boy for profile pictures"))
                    green_btn = gr.Button(label="Search", value="Search")
                
                with gr.Column():
                    danb_gallery=gr.Gallery(label="Image Preview")
                    danb_gallery.style(preview=True,object_fit="cover",columns=5,container=True)
                    with gr.Row():
                        blue_btn = gr.Button(label="Auto Crop",value="Crop Selected Image",variant='secondary')
                        blue_btn.click(fn=send_number,inputs=[selected,imgz_global],outputs=[imgz_global, image, tabs])
                        open_btn = gr.Button(label="Open Folder",value="Open 📁",variant='secondary')
                        open_btn.click(fn=open_folder, inputs=folder_input)

            danb_gallery.select(get_select_index, None, selected)
            green_btn.click(get_images, [searchQuery, num_pics, num_pages, filters, bl_tags, inc_tags,imageControl,imgz_global], outputs=[imgz_global,danb_gallery])
            
        
        # Zerochan Tab
        with gr.TabItem("Zerochan", id=3):
            with gr.Row():
                with gr.Column():
                    searchQuery = gr.Textbox(label="Search Query", placeholder="Suggested to use the char's full name")
                    with gr.Row():
                        num_pics = gr.Slider(1,30, value=2, step=int, label="Number of Pictures")
                    with gr.Row():
                        num_pages = gr.Slider(1,50, value=1, step=int, label="Number of Pages")
                    with gr.Row():
                        with gr.Row():
                            n_likes = gr.Number(value=0, label="Filter by Likes")
                            with gr.Row():
                                filters = gr.CheckboxGroup(["AI Classifier"], label="Filters", type="index",elem_id="zeroAIhover")
                        with gr.Column():
                            imageControl = gr.CheckboxGroup(["Continue Search"], label="Image Control", type="index", elem_id="imageControl")   
                    green_btn = gr.Button(label="Search", value="Search")
                
                with gr.Column():
                    zero_gallery=gr.Gallery(label="Image Preview")
                    zero_gallery.style(preview=True,object_fit="cover",columns=5,container=True)
                    
                    with gr.Row():
                        blue_btn = gr.Button(label="Auto Crop",value="Crop Selected Image",variant='secondary')
                        blue_btn.click(fn=send_number,inputs=[selected,imgz_global],outputs=[imgz_global, image, tabs])
                        open_btn = gr.Button(label="Open Folder",value="Open 📁",variant='secondary')
                        open_btn.click(fn=open_folder, inputs=folder_input)

            zero_gallery.select(get_select_index, None, selected)
            green_btn.click(get_images, [searchQuery, num_pics, num_pages, n_likes, filters,imageControl,imgz_global], outputs=[imgz_global,zero_gallery])
 

demo.launch()
