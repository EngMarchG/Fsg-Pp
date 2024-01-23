import os
import asyncio
import gradio as gr
import commands.exec_path as exec_path
import commands.driver_instance as driver_instance

from commands.universal import searchQuery
from ai.autocrop import autoCropImages
from sites.pixiv import getOrderedPixivImages
from sites.danbooru import getOrderedDanbooruImages
from sites.zerochan import getOrderedZerochanImages
from sites.yandex import getOrderedYandexImages


class ImageGallery:
    def __init__(self):
        self.imgz = []
        self.selected = 0

    def return_images(self, image_locs):
        self.imgz = image_locs
        print(self.imgz)
        return self.imgz if self.imgz else []

    def get_select_index(self, evt: gr.SelectData):
        self.selected = evt.index
        return self.selected

    def send_number(self): 
        return self.imgz[int(self.selected)], gr.Tabs(selected=0)


# Create an instance of ImageGallery for each tab
pixiv_gallery = ImageGallery()
danbooru_gallery = ImageGallery()
zerochan_gallery = ImageGallery()
yandex_gallery = ImageGallery()


# Helper functions
async def pix_imgs(searchQuery, num_pics, num_pages,searchTypes,viewRestriction,imageControl,n_likes, n_bookmarks, n_views, 
             start_date, end_date, user_name, pass_word):
    driver_future = asyncio.ensure_future(driver_instance.create_driver_async(profile=1))
    driver = await driver_future
    args_dict = {'driver': driver, 'exec_path': exec_path, 'user_search': searchQuery, 'num_pics': num_pics, 'num_pages': num_pages,'searchTypes':searchTypes,'viewRestriction':viewRestriction,'imageControl':imageControl, 'n_likes': n_likes, 'n_bookmarks': n_bookmarks, 'n_views': n_views, 'start_date': start_date,'end_date':end_date, 'user_name': user_name, 'pass_word': pass_word}
    result = await getOrderedPixivImages(**args_dict)
    return pixiv_gallery.return_images(result)

async def danb_imgs(searchQuery, num_pics, num_pages, filters, bl_tags, inc_tags,imageControl):
    driver_future = asyncio.ensure_future(driver_instance.create_driver_async())
    driver = await driver_future
    args_dict = {'driver': driver, 'user_search': searchQuery, 'num_pics': num_pics, 'num_pages': num_pages, 'filters': filters, 'bl_tags': bl_tags, 'inc_tags': inc_tags, 'exec_path': exec_path,'imageControl':imageControl}
    result = await getOrderedDanbooruImages(**args_dict)
    return danbooru_gallery.return_images(result)

async def zero_imgs(searchQuery, num_pics, num_pages, n_likes, filters,imageControl):
    driver_future = asyncio.ensure_future(driver_instance.create_driver_async())
    driver = await driver_future
    args_dict = {'driver': driver, 'exec_path': exec_path, 'user_search': searchQuery, 'num_pics': num_pics, 'num_pages': num_pages, 'n_likes': n_likes, 'filters': filters,'imageControl':imageControl}
    result = await getOrderedZerochanImages(**args_dict)
    return zerochan_gallery.return_images(result)

async def yandex_imgs(searchQuery, num_pics, filters,imageOrientation):
    driver_future = asyncio.ensure_future(driver_instance.create_driver_async())
    driver = await driver_future
    args_dict = {'driver': driver, 'exec_path': exec_path, 'user_search': searchQuery, 'num_pics': num_pics, 'filters': filters,'imageOrientation':imageOrientation}
    result = await getOrderedYandexImages(**args_dict)
    return yandex_gallery.return_images(result)


# Feature Functions
def open_folder(folder_path, mode=0):
    folder_opened = os.path.abspath(folder_path)
    if mode:
        folder_opened = os.path.abspath(os.path.join(folder_path, "cropped"))
    os.system(f'open "{folder_opened}"' if os.name == 'posix' else f'explorer "{folder_opened}"')

def cropImages(image,crop_scale_factor):
    return autoCropImages(image,crop_scale_factor)

async def create_gallery_tab(tab_name, search_fn, search_inputs, gallery_instance, fn_on_click):
    with gr.Column():
        gallery=gr.Gallery(label="Image Preview", preview=True, object_fit="cover", container=True, columns=5)

        with gr.Row():
            crop_btn = gr.Button(value="Crop Selected Image",variant='secondary')
            crop_btn.click(fn=fn_on_click, outputs=[image,tabs])
            open_btn = gr.Button(value="Open 📁",variant='secondary')
            open_btn.click(fn=open_folder, inputs=folder_input)

    gallery.select(gallery_instance.get_select_index, None, concurrency_limit=4, queue=True)
    green_btn.click(search_fn, search_inputs, outputs=gallery)


# Main Layout of the GUI
with gr.Blocks(css='style.css', title="Fsg-Pp") as demo:
    with gr.Tabs(selected=1) as tabs:
        folder_input = gr.Textbox(value="./Images/", label="Enter Folder Path", visible=False)
        
        # Automatic Crop Tab
        with gr.TabItem("Automatic Crop", id=0):
            with gr.Row():
                with gr.Column():
                    image = gr.Image(type="filepath")
                    crop_scale_factor = gr.Slider(0.5,3, value=1.2,step=0.1, label="Crop Scale Factor")
                with gr.Column():
                    outputImages = gr.Gallery(label="Cropped Image Preview", preview=True, object_fit="cover", container=True)

                    with gr.Row():
                        green_btn = gr.Button(value="Crop Image", size='sm')
                        green_btn.click(cropImages, [image,crop_scale_factor],outputs=outputImages)
                        open_btn = gr.Button(value="Open 📁",variant='secondary', size='sm')
                        open_btn.click(fn=open_folder, inputs=[folder_input,crop_scale_factor])


        # Pixiv Tab
        with gr.TabItem("Pixiv", id=1, elem_id="pixiv_tab", elem_classes="tab-button"):
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
                            green_btn = gr.Button(value="Search")
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
                            user_name = gr.Textbox(label="Email", type="email")
                    with gr.Row():
                            pass_word = gr.Textbox(label="Password", type="password")
                    
                pixiv_inputs = [searchQuery, num_pics, num_pages,searchTypes,viewRestriction,imageControl,n_likes, n_bookmarks, n_views, 
                                start_date,end_date, user_name, pass_word]
                asyncio.run(create_gallery_tab("Pixiv", pix_imgs, pixiv_inputs, pixiv_gallery, pixiv_gallery.send_number))


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
                    green_btn = gr.Button(value="Search")
            
                danbooru_inputs = [searchQuery, num_pics, num_pages, filters, bl_tags, inc_tags,imageControl]
                asyncio.run(create_gallery_tab("Danbooru", danb_imgs, danbooru_inputs, danbooru_gallery, danbooru_gallery.send_number))


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
                    green_btn = gr.Button(value="Search")
                
                with gr.Column():
                    zerochan_inputs = [searchQuery, num_pics, num_pages, n_likes, filters,imageControl]
                    asyncio.run(create_gallery_tab("Zerochan", zero_imgs, zerochan_inputs, zerochan_gallery, zerochan_gallery.send_number))


        # Yandex Tab
        with gr.TabItem("Yandex", id=4):
            with gr.Row():
                with gr.Column():
                    searchQuery = gr.Textbox(label="Search Query", placeholder="Suggested to use the char's full name")
                    with gr.Row():
                        num_pics = gr.Slider(1,30, value=2, step=int, label="Number of Pictures")
                    with gr.Row():
                        with gr.Row():
                                filters = gr.CheckboxGroup(["AI Classifier","Search By Recent"], label="Filters", type="index",elem_id="zeroAIhover")
                        with gr.Column():
                            imageOrientation = gr.Radio(["Landscape","Portrait","Square"], label="Image Orientation", type="index", elem_id="imageControl")   
                    green_btn = gr.Button(value="Search")
                
                yandex_inputs = [searchQuery, num_pics, filters,imageOrientation]
                asyncio.run(create_gallery_tab("Yandex", yandex_imgs, yandex_inputs, yandex_gallery, yandex_gallery.send_number))


if __name__ == '__main__':
    open_in_browser = os.environ.get('OPEN_IN_BROWSER') == '-o'
    demo.launch(inbrowser=open_in_browser, allowed_paths=["./bg"])