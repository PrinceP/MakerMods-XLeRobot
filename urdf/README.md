# MakerMods XLeRobot URDF

The assembled robot as a URDF: IKEA RÅSKOG cart with the MakerMods omniwheel base, two-part neck and arm mounts (merged into
`base_link`), two SO-101 arms, a pan/tilt head, and camera frames.

## Source and licence

- Published by MakerMods with the MakerMods XLeRobot project on tnkr.ai
  ([ryans-workspace/xlerobot](https://tnkr.ai/ryans-workspace/xlerobot), package `makermods-xlerobot-20260930`), where it drives the
  interactive 3D viewer.
- Licence: Apache License 2.0, [`LICENCE.txt`](LICENCE.txt) (copied unchanged with the package). The SO-101 arm meshes come from
  [TheRobotStudio SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) (Apache-2.0).
- `xlerobot.urdf` and the 23 STL meshes in `meshes/` are unmodified.

## Known issues in the package

- The URDF references `Fixed_Jaw_part1/2.ply` and `Moving_Jaw_part1/2/3.ply` (the jaws' collision meshes). On the host these files are
  S3 "Access Denied" pages, not meshes, so they are not included. Loaders must skip them; the jaws then have visual meshes only.
- Masses: `base_link` is 74.9 kg (cart + base + neck + electronics lumped together), `top_base_link` 4.35 kg, head 3.2 kg. The real robot is
  about 12 kg in total (XLeRobot docs, v0.3). Fix masses before using this for dynamics.
- Arm mount height: the arm bases (`arm_base_joint`, `arm_base_joint_2`) sit at z = 0.744 m. One measured build had its arm base bottoms
  at 0.86 m, so check this against your robot.
- Joint zero: the arms use the older SO-101 zero (arm stretched forward), in radians. LeRobot's calibrated degrees differ by sign and
  offset per joint (see the MuJoCo notes below).

## Frames and kinematic tree

`base_link` is the cart frame on the floor: x forward, y left, z up. The base moves on two prismatic joints and one yaw joint (a planar
stand-in for the three omniwheels; the wheels are not modelled as joints). "Right" arm = no suffix, "left" arm = `_2`.

| Joint | Type | Parent → child | Origin xyz (m) | Axis | Limits (rad) |
|---|---|---|---|---|---|
| `root_x_axis_joint` | prismatic | root → root_arm_1_link_1 | 0 0 0 | 1 0 0 | -20 .. 20 |
| `root_y_axis_joint` | prismatic | root_arm_1_link_1 → root_arm_1_link_2 | 0 0 0 | 0 1 0 | -20 .. 20 |
| `root_z_rotation_joint` | continuous | root_arm_1_link_2 → base_link | 0 0 0 | 0 0 1 | |
| `arm_base_joint` | fixed | base_link → Base (right arm) | -0.093 -0.137 0.744 | | |
| `Rotation` | revolute | Base → Rotation_Pitch | 0 -0.045 0.017 | 0 -1 0 | -2.10 .. 2.10 |
| `Pitch` | revolute | Rotation_Pitch → Upper_Arm | 0 0.102 0.031 | -1 0 0 | -0.10 .. 3.45 |
| `Elbow` | revolute | Upper_Arm → Lower_Arm | 0 0.113 0.028 | 1 0 0 | -0.20 .. 3.14 |
| `Wrist_Pitch` | revolute | Lower_Arm → Wrist_Pitch_Roll | 0 0.005 0.135 | 1 0 0 | -1.80 .. 1.80 |
| `Wrist_Roll` | revolute | Wrist_Pitch_Roll → Fixed_Jaw | 0 -0.060 0 | 0 -1 0 | -3.14 .. 3.14 |
| `Jaw` | revolute | Fixed_Jaw → Moving_Jaw | -0.020 -0.024 0 | 0 0 1 | 0 .. 1.70 |
| `Right_Arm_Camera_joint` | fixed | Fixed_Jaw → Right_Arm_Camera (wrist camera) | 0 -0.020 0.050 | | |
| `arm_base_joint_2` | fixed | base_link → Base_2 (left arm) | -0.093 0.138 0.744 | | |
| `Rotation_2` … `Jaw_2` | | same chain as the right arm | | | |
| `Left_Arm_Camera_joint` | fixed | Fixed_Jaw_2 → Left_Arm_Camera | 0 -0.020 0.050 | | |
| `top_base_joint` | fixed | base_link → top_base_link (neck) | 0 0 0 | | |
| `head_pan_joint` | revolute | top_base_link → head_pan_link | -0.068 0 1.094 | 0 0 1 | -1.57 .. 1.57 |
| `head_tilt_joint` | revolute | head_pan_link → head_tilt_link | 0.031 0 0.054 | 0 1 0 | -0.76 .. 1.45 |
| `head_camera_joint` | fixed | head_tilt_link → head_camera_link | 0.035 -0.001 0.032 | | |

Plus jaw-tip frames (`Fixed_Jaw_tip`, `Moving_Jaw_tip`) and head camera RGB/depth optical frames.

Meshes per link: `base_link` = `makermods_base_{dark,grey,light}.stl` (the whole printed/cart structure, merged and split by colour),
`head_pan_link` = `makermods_head_pan_{dark,light}.stl`, `head_tilt_link` = `makermods_head_tilt_{dark,grey,light}.stl`, arm links =
the SO-101 part + servo meshes (`Base`, `Rotation_Pitch`, `Upper_Arm`, `Lower_Arm`, `Wrist_Pitch_Roll`, `Fixed_Jaw`, `Moving_Jaw`),
wrist cameras = `XLeRobot_camera{1,2}.stl`.

The printed parts are merged into these colour meshes, so the URDF gives the **assembled shape and joint positions** but not individual
printed-part poses. For the individual parts (names, counts, sizes) see [`PARTS_3MF.md`](PARTS_3MF.md).

## Using it in MuJoCo

A MuJoCo model built from this URDF (masses fixed, servo actuators, cameras, jaw contact pads), with notes on the joint mapping to
LeRobot's calibrated degrees, is in
[PrinceP/robotics-antigravity-plugin, branch `xlerobot`, skill `xlerobot-sim`](https://github.com/PrinceP/robotics-antigravity-plugin/tree/xlerobot/plugins/robotics/skills/xlerobot-sim).
To load the raw URDF in MuJoCo, drop the `.ply` visual/collision blocks and give the zero-mass planar-base links a minimum mass
(`<compiler boundmass="0.001" boundinertia="1e-6"/>`).
