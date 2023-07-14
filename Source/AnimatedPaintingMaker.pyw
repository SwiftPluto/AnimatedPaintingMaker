import sys
import time
from tkinter import *
from tkinter import ttk, filedialog
import tkinter
from tkinter import messagebox
import PIL
from moviepy.editor import VideoFileClip
import threading
import numpy as np
from PIL import Image, ImageTk
import os
import math
import shutil

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
cwd = os.getcwd()
window = Tk()
window.title("Animated Painting Maker")
# window.iconbitmap(resource_path("icon.ico"))
window.geometry("960x540")
window.resizable(False,False)
window.fileDir = ""
window.outputFile = ""
original = 0
# window.configure(background='bisque2')
on_frame = 0
out_of = 0

# Update the elapsed time
def update_time():
    if is_running:
        elapsed_time = time.time() - start_time
        global on_frame
        global out_of
        time_label.config(text="Time Elapsed: {:.2f}".format(elapsed_time) + "     " + f"{on_frame}" + " / " + f"{out_of}")
        time_label.after(50, update_time)

def open_file():
    selected = filedialog.askopenfilename(initialdir=desktop, title="Select a file", filetypes=[('Video Files', ["*.mp4"])])
    openFileForm.delete(0, END)
    openFileForm.insert(INSERT, selected)
    original = VideoFileClip(selected)                                 # Load the video clip
    global out_of 
    out_of = math.ceil(20 * original.duration)
    time_label.config(text="Time Elapsed: 0.00" + "     " + f"0 / " +  f"{out_of}")

def select_dir():
    selected = filedialog.askdirectory(initialdir=desktop, title="Select Location")
    outputFileForm.delete(0, END)
    outputFileForm.insert(INSERT, selected)

def start():
    try:
        if(openFileForm.get() != "" and outputFileForm.get() != ""):
            width = int(widthForm.get())
            height = int(heightForm.get())
            limit = 0
            if(method.get() == True):
                limit = int(limitForm.get())  
            global out_of

            threading.Thread(target=process, args=(width, height, str(openFileForm.get()), str(outputFileForm.get()), method.get(), limit, out_of)).start()
            global is_running
            global start_time
            if not is_running:
                is_running = True
                start_time = time.time()
                update_time()
            verify.config(text="")
        else:
            verify.config(text="ERROR: Invalid input")

    except ValueError:
        verify.config(text="ERROR: Invalid input")

def process(w, h, f, o, m, l, t):
    currentFrame = 0                                      # Set currentFrame for loop
    original = VideoFileClip(f)                                 # Load the video clip
    new_clip = original.set_fps(20)                             # Change video framerate,
    video_clip = new_clip.resize( (w,h) )                       # Change video resolution
    film = np.zeros([0,0,3],dtype=np.uint8)                     # Create initial film image

    global on_frame
    startButton["state"] = "disabled"
    startButton["text"] = "Processing . . ."

    # if the saving_frames_per_second is above 20 video FPS, then set it to FPS (as maximum)
    saving_frames_per_second = min(video_clip.fps, 20)

    # if SAVING_FRAMES_PER_SECOND is set to 0, step is 1/fps, else 1/SAVING_FRAMES_PER_SECOND
    step = 1 / video_clip.fps if saving_frames_per_second == 0 else 1 / saving_frames_per_second
    
    if(m):
        #Create frames folder
        path = "Segmentation Processing (Do NOT Delete! It will delete itself)"
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
            cwd = os.getcwd()
        framesFolder = ''.join([cwd, f"\{path}"])
    Segments = []

    for current_duration in np.arange(0, video_clip.duration, step):
        if(currentFrame == 0):
            film = np.copy(np.asarray(video_clip.get_frame(current_duration))) 
        else:
            if(m and currentFrame % l == 0):
                part = Image.fromarray(film)
                part.save(os.path.join(framesFolder + f'/frames_to_{currentFrame}.png'))
                Segments.append(currentFrame)
                film = np.copy(np.asarray(video_clip.get_frame(current_duration))) 
            else:
                imgs = [film, np.asarray(video_clip.get_frame(current_duration))]
                film = np.vstack([i for i in imgs])

            if(m and (currentFrame+1) == out_of and len(Segments) > 0):
                part = Image.fromarray(film)
                part.save(os.path.join(framesFolder + f'/frames_to_{currentFrame}.png'))
                Segments.append(currentFrame)

        currentFrame += 1
        on_frame = currentFrame
        resize_image = Image.fromarray(np.asarray(video_clip.get_frame(current_duration))).resize((642, 369)) 
        img = ImageTk.PhotoImage(resize_image)
        canvas.create_image(0,0, anchor=NW, image=img)
        progressBar['value'] = (currentFrame / t) * 100

    if(len(Segments) > 0):
        film = np.zeros([0,0,3],dtype=np.uint8)
        arr = []
        for i in Segments:
            arr.append(Image.open(os.path.join(framesFolder + f'/frames_to_{i}.png')))
        film = np.vstack([i for i in arr])

    final = Image.fromarray(film)
    final.save(os.path.join(o , 'film.png'))
    film = np.zeros([0,0,3],dtype=np.uint8) # Reset Film to relieve memory after a process

    # Delete Folder code
    if(m):
        shutil.rmtree(framesFolder)
    
    window.bell()
    startButton["state"] = "normal"
    startButton["text"] = "Start Processing"
    global is_running
    is_running = False
    messagebox.showinfo("Finished", "Done :)")

#Creating GUI
presetsLabel = Label(window,  text="Presets", font=('Helvetica 10'))
presetsLabel.place(x=130, y=75)
presetsLabel = Label(window,  text="Customize", font=('Helvetica 10'))
presetsLabel.place(x=120, y=260)

openFileLabel = Label(window,  text="(Choose a video to convert)").place(x=20, y=45)
openFileButton = Button(window, text="Open File", command=open_file, width=10, height=1).place(x=20,y=20)
openFileForm=Entry(window,width=25, font=('Helvetica 14'))
openFileForm.place(x=100, y=20)

outputFileLabel = Label(window,  text="(Choose a location to export to)").place(x=400, y=45)
outputFileButton = Button(window, text="Export", command=select_dir, width=10, height=1).place(x=400,y=20)
outputFileForm=Entry(window,width=25, font=('Helvetica 14'))
outputFileForm.place(x=480, y=20)

startButton = Button(window, text="Start Processing", command=start, width=20, height=2,) #bg='palegreen3'
startButton.place(x=790,y=20)
verify = Label(window, text='')
verify.place(x=808,y=62)

widthLabel = Label(window,  text="Width").place(x=20, y=295)
widthForm=Entry(window, width=35)
widthForm.place(x=64, y=295)

heightLabel = Label(window,  text="Height").place(x=20, y=335)
heightForm=Entry(window,width=35)
heightForm.place(x=64, y=335)

def segmentationShow():
    limit.place(x=20,y=420)
    limitForm.place(x=64,y=420)
def segmentationHide():
    limit.place_forget()
    limitForm.place_forget()
method = BooleanVar()
method.set(False)
Radiobutton(window, text="Memory Method", variable=method, value=False, command=segmentationHide).place(x=20, y=375)
Radiobutton(window, text="Segmentation", variable=method, value=True, command=segmentationShow).place(x=172,y=375)

limit = Label(window,  text="Limit")
limitForm=Entry(window, width=35)

canvas = Canvas(window, width = 640, height = 360, borderwidth=1, relief="solid", highlightthickness=0, background= "gray78")      
canvas.place(x=298,y=80)  

time_label = tkinter.Label(window, text="Time Elapsed: 0.00     - / -")
time_label.place(x=20,y=460)
is_running = False

s = ttk.Style()
s.theme_use("default")
s.configure("TProgressbar", thickness=30)
progressBar = ttk.Progressbar(window, style="TProgressbar", length=920, orient=HORIZONTAL, mode='determinate')
progressBar.place(x=20,y=488)

size = StringVar()
def preset():
    match size.get():
        case "1x1":
            widthForm.delete(0, END)
            heightForm.delete(0, END)
            widthForm.insert(INSERT, 64)
            heightForm.insert(INSERT, 64)
        case "1x2":
            widthForm.delete(0, END)
            heightForm.delete(0, END)
            widthForm.insert(INSERT, 128)
            heightForm.insert(INSERT, 64)
        case "2x1":
            widthForm.delete(0, END)
            heightForm.delete(0, END)
            widthForm.insert(INSERT, 64)
            heightForm.insert(INSERT, 128)
        case "2x2":
            widthForm.delete(0, END)
            heightForm.delete(0, END)
            widthForm.insert(INSERT, 128)
            heightForm.insert(INSERT, 128)
        case "4x2":
            widthForm.delete(0, END)
            heightForm.delete(0, END)
            widthForm.insert(INSERT, 256)
            heightForm.insert(INSERT, 128)
        case "4x3":
            widthForm.delete(0, END)
            heightForm.delete(0, END)
            widthForm.insert(INSERT, 256)
            heightForm.insert(INSERT, 192)
        case "4x4":
            widthForm.delete(0, END)
            heightForm.delete(0, END)
            widthForm.insert(INSERT, 256)
            heightForm.insert(INSERT, 256)

onexoneImage =PhotoImage(file=resource_path("image1x1.png"))
onextwoImage =PhotoImage(file= resource_path("image1x2.png"))
twoxoneImage =PhotoImage(file=resource_path("image2x1.png"))
twoxtwoImage =PhotoImage(file= resource_path("image2x2.png"))
fourxtwoImage =PhotoImage(file=resource_path("image4x2.png"))
fourxthreeImage =PhotoImage(file=resource_path("image4x3.png"))
fourxfourImage =PhotoImage(file=resource_path("image4x4.png"))
Radiobutton(window, text="1x1", indicator = 0, variable=size, value="1x1", command=preset, image=onexoneImage).place(x=20, y=110, width=64, height=64)
Radiobutton(window, text="1x2", indicator = 0, variable=size, value="1x2", command=preset, image=onextwoImage).place(x=84, y=110, width=64, height=64)
Radiobutton(window, text="2x1", indicator = 0, variable=size, value="2x1", command=preset, image=twoxoneImage).place(x=148, y=110, width=64, height=64)
Radiobutton(window, text="2x2", indicator = 0, variable=size, value="2x2", command=preset, image=twoxtwoImage).place(x=212, y=110, width=64, height=64)
Radiobutton(window, text="4x2", indicator = 0, variable=size, value="4x2", command=preset, image=fourxtwoImage).place(x=20, y=174, width=64, height=64)
Radiobutton(window, text="4x3", indicator = 0, variable=size, value="4x3", command=preset, image=fourxthreeImage).place(x=84, y=174, width=64, height=64)
Radiobutton(window, text="4x4", indicator = 0, variable=size, value="4x4", command=preset, image=fourxfourImage).place(x=148, y=174, width=64, height=64)

window.mainloop()