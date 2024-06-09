# Screen recording over x server with Xephyr.
# Make sure the GUI you want to record connects with the correct display port

from easyprocess import EasyProcess

from pyvirtualdisplay.smartdisplay import SmartDisplay
import cv2
import numpy as np
import threading
import argparse


class XScreenRecording:
    def __init__(self, cmd, width, height, auto=True, output_name="output.mp4", fps=20):
        self.recording = True
        self.result = 0
        self.width = width
        self.height = height
        self.start = False
        # Flag for automaitcally start recording when gui is up
        self.auto = auto
        # The subcommand to execute
        self.cmd = cmd
        # Set the output filename
        if output_name == ".mp4":
            output_name = "output.mp4"
        self.output_name = output_name
        # Frames per secod for the recorded video file
        self.fps = fps
        self.cur_printout = ""

    def background_work(self):
        
        # Note that Xephyr screen size is (width, height)
        writer = None
        # Define the fourcc codec for makein the mp4 video
        code = cv2.VideoWriter_fourcc(*'avc1')
        with SmartDisplay(visible=True, size=(self.width, self.height)) as disp:
            # Start a xephyr process 
            #print(f"The display environemtn is: {disp.env()}")
            with EasyProcess(self.cmd) as proc:
                # Start the process that should be placed in the Xephyr interface
                while not self.start:
                    # Hold loop to controll start of recording
                    pass

                while self.recording:
                    self.cur_printout = proc.stdout
                    # recording loop controlled by the main thread
                    # screenshot of the GUI is taken
                    img = np.array(disp.grab())
                    if img.size > 1:
                        if not writer:
                            # Create the video writer object if this is the first iteration
                            writer = cv2.VideoWriter(self.output_name, code, int(self.fps), (img.shape[1], img.shape[0]))
                        
                        # Write the image to the video
                        writer.write(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
    
        if writer:
            # If any video was recorded, release the reccording and save the file to disk
            writer.release() 

    def main(self):
        # Start the recording thread
        background = threading.Thread(target=self.background_work)
        background.start()
        # If the auto flag was set to false, wait for user confirmation to start recording
        if not self.auto:
            input("press enter to start recording: ")
        
        # set the recording flag to release the hold loop in the recording thread
        self.start = True
        print("recording started!")
        
        while True:
            # controll loop for the stop signal from user
            response = input("press s to stop recording: ")
            # If the user inputs an "s", the application is breaking the recording loop and releases the mp4 file
            if response == "s":
                self.recording = False
                break

        background.join()
        


if __name__=='__main__':
    # The program can be run with a set of arguments. The important argument is -c where the subprocess is 
    # specified for the program that should be recorded. 
    parser = argparse.ArgumentParser(
                    prog='XephyrScreenRecorder',
                    description='This program can be used to create mp4 videos of GUIs running in the Xephyr interface',
                    epilog='')
    parser.add_argument("-c", "--cmd")
    # Await record signal from user
    parser.add_argument("-a", "--auto", default=False, type=bool)
    # Resolution of xephyr window
    parser.add_argument("-r", "--resolution", default="800x800")
    parser.add_argument("-o", "--output_name", default="output")
    parser.add_argument("-f", "--fps", default=20)

    args = parser.parse_args()
    width, height = args.resolution.split("x")
    cmd = args.cmd.split(" ")
    out_file_name = args.output_name + ".mp4"
    fps = args.fps
    
    recorder = XScreenRecording(cmd, width, height, auto=args.auto, output_name=out_file_name, fps=fps)
    recorder.main()
