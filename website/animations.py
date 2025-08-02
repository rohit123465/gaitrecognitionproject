import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation, FFMpegWriter
from scipy.ndimage import gaussian_filter1d

def load_smpl_output(json_path):

    with open(json_path, 'r') as f:
        data = json.load(f)
    if 'frames' not in data:
        raise ValueError("Invalid JSON format: Missing 'frames' key.")
    return data['frames']

def smooth_joints(joints, sigma=1.0):
    # Apply smoothing across frames for each joint's x, y, z coordinates
    smoothed_joints = np.zeros_like(joints)
    for i in range(joints.shape[1]):  # For each joint
        smoothed_joints[:, i, :] = gaussian_filter1d(joints[:, i, :], sigma=sigma, axis=0, mode='nearest')
    return smoothed_joints

def plot_smpl_data(joints, vertices, ax):

    ax.clear()
    ax.set_title('SMPL Model Animation')

    # Disable the axis
    ax.set_axis_off()

    x_j, y_j, z_j = joints[:, 0], joints[:, 1], joints[:, 2]
    ax.scatter(x_j, y_j, z_j, c='red', marker='o', s=80, label='Joints', edgecolors='black', linewidth=1.2)

    x_v, y_v, z_v = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    ax.scatter(x_v, y_v, z_v, c='blue', marker='.', alpha=0.2, s=5, label='Vertices')

    connections = [
    (0, 9),  # Pelvis to Spine1
    (9, 10),  # Spine1 to Spine2
    (10, 11),  # Spine2 to Spine3
    (11, 12),  # Spine3 to Neck
    (12, 13),  # Neck to Head

    (9, 14),  # Spine1 to Left Shoulder
    (14, 15),  # Left Shoulder to Left Elbow
    (15, 16),  # Left Elbow to Left Wrist

    (9, 17),  # Spine1 to Right Shoulder
    (17, 18),  # Right Shoulder to Right Elbow
    (18, 19),  # Right Elbow to Right Wrist

    (0, 1),  # Pelvis to Left Hip
    (1, 2),  # Left Hip to Left Knee
    (2, 3),  # Left Knee to Left Ankle
    (3, 4),  # Left Ankle to Left Foot

    (0, 5),  # Pelvis to Right Hip
    (5, 6),  # Right Hip to Right Knee
    (6, 7),  # Right Knee to Right Ankle
    (7, 8)   # Right Ankle to Right Foot
    ]
    for start, end in connections:
        ax.plot([x_j[start], x_j[end]], [y_j[start], y_j[end]], [z_j[start], z_j[end]], color='black', linewidth=2)

    ax.legend()

def animate(i, frames, ax, joints_data, sigma=1.0):
    frame = frames[i]
    if 'joints' in frame and 'vertices' in frame:
        joints = np.array(frame['joints'])
        vertices = np.array(frame['vertices'])

        # Apply Gaussian smoothing to joints over time
        smoothed_joints = joints_data[i]  # Use the precomputed smoothed joints for each frame

        plot_smpl_data(smoothed_joints, vertices, ax)

def save_smpl_animation(json_path, output_path, sigma=1.0):
    frames = load_smpl_output(json_path)

    # Preprocess all joint data across frames and apply Gaussian smoothing
    joints_data = []
    for frame in frames:
        if 'joints' in frame:
            joints = np.array(frame['joints'])
            joints_data.append(joints)
    joints_data = np.array(joints_data)

    # Apply Gaussian smoothing over all frames
    smoothed_joints_data = smooth_joints(joints_data, sigma=sigma)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.view_init(elev=100, azim=90)

    ani = FuncAnimation(fig, animate, frames=len(frames), fargs=(frames, ax, smoothed_joints_data, sigma), interval=33)  # 30 FPS
    writer = FFMpegWriter(fps=30, bitrate=1800)
    ani.save(output_path, writer=writer)
    print(f"Animation saved as {output_path}")
