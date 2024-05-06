import picamera
import time
import grovepi
import os
import subprocess  # To call MP4Box for conversion

# Connect the PIR motion sensor to digital port D8
pir_sensor = 4
# Connect the joystick to analog port A0
joystick = 0
# Connect the buzzer to digital port D3
buzzer = 3
# Define the directory to save videos
video_dir_mp4 = "static"
video_dir_h264 = "videos_h264"
# Define the motion log file
motion_log_file = "motion.txt"

# Function to initialize the camera
def initialize_camera():
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)  # Set smaller resolution
    camera.preview_fullscreen = False
    camera.preview_window = (10, 10, 320, 240)  # (x, y, width, height)
    return camera

# Function to initialize the buzzer
def initialize_buzzer():
    grovepi.pinMode(buzzer, "OUTPUT")

# Function to turn on the buzzer
def turn_on_buzzer():
    grovepi.digitalWrite(buzzer, 1)

# Function to turn off the buzzer
def turn_off_buzzer():
    grovepi.digitalWrite(buzzer, 0)

# Function to save the video with a timestamped filename
def save_video(camera):
    if not os.path.exists(video_dir_h264):
        os.makedirs(video_dir_h264)
    if not os.path.exists(video_dir_mp4):
        os.makedir(video_dir_mp4)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename_h264 = os.path.join(video_dir_h264, f"video_{timestamp}.h264")
    filename_mp4 = os.path.join(video_dir_mp4, f"video_{timestamp}.mp4")  # For the converted MP4 file
    camera.start_recording(filename_h264)
    start_time = time.time()  # Record the start time
    return filename_h264, filename_mp4, start_time

# Function to stop recording and convert to MP4
def stop_video(camera, start_time, filename_h264, filename_mp4):
    camera.stop_recording()
    end_time = time.time()
    duration = end_time - start_time
    if duration >= 10:
        # Convert H.264 to MP4
        subprocess.run(["MP4Box", "-add", filename_h264, filename_mp4])
        return duration
    else:
        os.remove(filename_h264)  # Delete the H.264 file if duration is less than 10 seconds
        return None

# Function to log motion events to motion.txt
def log_motion(filename, timestamp, duration):
    if duration:
        with open(motion_log_file, "a") as f:
            f.write(f"{filename}, {timestamp}\n")

# Main function
def main():
    camera = None
    camera_status = False  # Flag to track camera status
    grovepi.pinMode(pir_sensor, "INPUT")
    initialize_buzzer()  # Initialize buzzer

    try:
        while True:
            # Read the motion sensor state
            motion_state = grovepi.digitalRead(pir_sensor)

            # If motion is detected and the camera is not already on
            if motion_state == 1 and not camera_status:
                print("Motion detected! Turning camera on...")
                camera = initialize_camera()
                filename_h264, filename_mp4, start_time = save_video(camera)
                if filename_h264:
                    camera_status = True

            # If the camera is on and the recording duration has passed
            if camera_status and time.time() - start_time >= 10:
                print("Recording duration reached. Turning camera off.")
                duration = stop_video(camera, start_time, filename_h264, filename_mp4)
                if duration:
                    log_motion(filename_mp4, time.strftime("%Y-%m-%d %H:%M:%S"), duration)
                camera.stop_preview()
                camera.close()
                camera = None
                camera_status = False

            # Check if the joystick is pressed down
            if grovepi.analogRead(joystick) > 1000:
                print("Joystick pressed down! Turning on buzzer...")
                turn_on_buzzer()
                time.sleep(0.5)  # Buzzer on time
                turn_off_buzzer()

            # Delay to avoid continuous polling
            time.sleep(0.1)  # Adjust delay as needed

    except KeyboardInterrupt:
        print("Exiting...")
        if camera is not None:
            camera.stop_preview()
            camera.close()

if __name__ == "__main__":
    main()
