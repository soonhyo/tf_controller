import rospy
import tf
import tkinter as tk
import threading

mode = "translation"
source_frame = "world"
target_frame = "camera_color_optical_frame"
speed = 0.01

translation = rospy.get_param('~initial_translation', [1.0, 2.0, 0.5])
quaternion = rospy.get_param('~initial_rotation', [0.0, 0.0, 0.0, 1.0])

def set_translation_mode():
    global mode
    mode = "translation"
    mode_label.config(text="Current Mode: Translation")

def set_rotation_mode():
    global mode
    mode = "rotation"
    mode_label.config(text="Current Mode: Rotation")

def update_frames():
    global source_frame, target_frame
    source_frame = source_frame_entry.get()
    target_frame = target_frame_entry.get()
    root.focus_set()

def update_speed():
    global speed
    try:
        speed = float(speed_entry.get())
    except ValueError:
        speed = 0.01
    root.focus_set()

def key_event(event):
    global translation, quaternion, mode, speed

    if mode == "translation":
        if event.keysym == '1':
            translation[0] += speed  # x +
        elif event.keysym == '2':
            translation[0] -= speed  # x -
        elif event.keysym == '3':
            translation[1] += speed  # y +
        elif event.keysym == '4':
            translation[1] -= speed  # y -
        elif event.keysym == '5':
            translation[2] += speed  # z +
        elif event.keysym == '6':
            translation[2] -= speed  # z -

    elif mode == "rotation":
        euler = tf.transformations.euler_from_quaternion(quaternion)
        if event.keysym == '1':
            euler = (euler[0] + speed, euler[1], euler[2])  # x + (roll)
        elif event.keysym == '2':
            euler = (euler[0] - speed, euler[1], euler[2])  # x - (roll)
        elif event.keysym == '3':
            euler = (euler[0], euler[1] + speed, euler[2])  # y + (pitch)
        elif event.keysym == '4':
            euler = (euler[0], euler[1] - speed, euler[2])  # y - (pitch)
        elif event.keysym == '5':
            euler = (euler[0], euler[1], euler[2] + speed)  # z + (yaw)
        elif event.keysym == '6':
            euler = (euler[0], euler[1], euler[2] - speed)  # z - (yaw)
        quaternion = tf.transformations.quaternion_from_euler(euler[0], euler[1], euler[2])

    print(f"Translation: {translation}")
    print(f"Rotation (quaternion): {quaternion}")

def publish_transform():
    global translation, quaternion, source_frame, target_frame

    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)

    while not rospy.is_shutdown():
        br.sendTransform(translation,
                         quaternion,
                         rospy.Time.now(),
                         target_frame,
                         source_frame)

        euler = tf.transformations.euler_from_quaternion(quaternion)

        rate.sleep()

if __name__ == '__main__':
    rospy.init_node('camera_tf_broadcaster', anonymous=True)

    root = tk.Tk()
    root.title("Camera TF Control")

    instructions = (
        "How to use:\n"
        "1. Translation Mode: 1 (x+), 2 (x-), 3 (y+), 4 (y-), 5 (z+), 6 (z-)\n"
        "2. Rotation Mode: 1 (roll+), 2 (roll-), 3 (pitch+), 4 (pitch-), 5 (yaw+), 6 (yaw-)\n"
    )
    instruction_label = tk.Label(root, text=instructions, justify="left")
    instruction_label.pack()

    mode_label = tk.Label(root, text="Current Mode: Translation")
    mode_label.pack()

    translation_button = tk.Button(root, text="Translation Mode", command=set_translation_mode)
    translation_button.pack()

    rotation_button = tk.Button(root, text="Rotation Mode", command=set_rotation_mode)
    rotation_button.pack()

    # frame setting UI
    frame_label = tk.Label(root, text="Set Source and Target Frames:")
    frame_label.pack()

    source_frame_label = tk.Label(root, text="Source Frame:")
    source_frame_label.pack()
    source_frame_entry = tk.Entry(root)
    source_frame_entry.insert(0, source_frame)
    source_frame_entry.pack()

    target_frame_label = tk.Label(root, text="Target Frame:")
    target_frame_label.pack()
    target_frame_entry = tk.Entry(root)
    target_frame_entry.insert(0, target_frame)
    target_frame_entry.pack()

    set_frames_button = tk.Button(root, text="Set Frames", command=update_frames)
    set_frames_button.pack()

    # speed setting UI
    speed_label = tk.Label(root, text="Set Speed:")
    speed_label.pack()

    speed_entry = tk.Entry(root)
    speed_entry.insert(0, str(speed))
    speed_entry.pack()

    set_speed_button = tk.Button(root, text="Set Speed", command=update_speed)
    set_speed_button.pack()

    root.bind("<KeyPress>", key_event)

    ros_thread = threading.Thread(target=publish_transform)
    ros_thread.daemon = True
    ros_thread.start()

    root.mainloop()
