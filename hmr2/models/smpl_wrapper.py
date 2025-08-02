import torch
import numpy as np
import pickle
from typing import Optional
import smplx
from smplx.lbs import vertices2joints
from smplx.utils import SMPLOutput
import json
import os


class SMPL(smplx.SMPLLayer):
    def __init__(self, *args, joint_regressor_extra: Optional[str] = None, update_hips: bool = False, **kwargs):
        """
        Extension of the official SMPL implementation to support more joints.
        Args:
            Same as SMPLLayer.
            joint_regressor_extra (str): Path to extra joint regressor.
        """
        super(SMPL, self).__init__(*args, **kwargs)
        smpl_to_openpose = [24, 12, 17, 19, 21, 16, 18, 20, 0, 2, 5, 8, 1, 4,
                            7, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34]
            
        if joint_regressor_extra is not None:
            self.register_buffer('joint_regressor_extra', torch.tensor(pickle.load(open(joint_regressor_extra, 'rb'), encoding='latin1'), dtype=torch.float32))
        self.register_buffer('joint_map', torch.tensor(smpl_to_openpose, dtype=torch.long))
        self.update_hips = update_hips
        print("Update hips:", self.update_hips)

    def forward(self, *args, **kwargs) -> SMPLOutput:
        """
        Run forward pass. Same as SMPL and also append an extra set of joints if joint_regressor_extra is specified.
        """
        smpl_output = super(SMPL, self).forward(*args, **kwargs)
        joints = smpl_output.joints[:, self.joint_map, :]
        if self.update_hips:
            joints[:, [9, 12]] = joints[:, [9, 12]] + \
                0.25 * (joints[:, [9, 12]] - joints[:, [12, 9]]) + \
                0.5 * (joints[:, [8]] - 0.5 * (joints[:, [9, 12]] + joints[:, [12, 9]]))
        if hasattr(self, 'joint_regressor_extra'):
            extra_joints = vertices2joints(self.joint_regressor_extra, smpl_output.vertices)
            joints = torch.cat([joints, extra_joints], dim=1)
        smpl_output.joints = joints

        # Extract pose parameters
        pose_params = smpl_output.body_pose
        root_orientation = smpl_output.global_orient
        shape_params = smpl_output.betas

        print("Pose Parameters (Body Pose):", pose_params)
        print("Root Orientation (Global Orient):", root_orientation)
        print("Shape Parameters (Betas):", shape_params)

        # Save SMPL Output to JSON
        self.save_smpl_output_to_json(smpl_output, file_path='/content/drive/MyDrive/4D-Humans/website/output/walking_man.json')

        return smpl_output

    @staticmethod
    def save_smpl_output_to_json(smpl_output, file_path='/content/drive/MyDrive/4D-Humans/website/output/walking_man.json'):
        """
        Append SMPL output to a JSON file instead of overwriting it.
        Args:
            smpl_output (SMPLOutput): Output from the SMPL forward pass.
            file_path (str): Path to save the JSON file.
        """
        smpl_data = {
            'joints': smpl_output.joints.detach().cpu().numpy().tolist() if smpl_output.joints is not None else None,
            'vertices': smpl_output.vertices.detach().cpu().numpy().tolist() if smpl_output.vertices is not None else None,
            'body_pose': smpl_output.body_pose.detach().cpu().numpy().tolist() if smpl_output.body_pose is not None else None,
            'global_orient': smpl_output.global_orient.detach().cpu().numpy().tolist() if smpl_output.global_orient is not None else None,
            'betas': smpl_output.betas.detach().cpu().numpy().tolist() if smpl_output.betas is not None else None,
            'camera_translation': smpl_output.translation.detach().cpu().numpy().tolist() if hasattr(smpl_output, 'translation') else None,
        }

        # Ensure output directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Load existing data if the file already exists
        if os.path.exists(file_path):
            with open(file_path, 'r') as json_file:
                try:
                    existing_data = json.load(json_file)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Append new data
        existing_data.append(smpl_data)

        # Write updated JSON file
        with open(file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

        print(f"SMPL output appended to {file_path}")