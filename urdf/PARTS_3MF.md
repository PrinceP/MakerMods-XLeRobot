# Printed parts in the `.3mf` (inventory)

Extracted from `3mf/MakerMods XLeRobot Upgrade PLA+ P2S.3mf` (95 objects). Names are the object names in the Bambu Studio project;
sizes are the part's bounding box in print orientation (mm), not its orientation on the robot. "×" counts identical copies.

## Robot structure (XLRB02 series and named parts)

| Part | × | Size (mm) | Likely location / role |
|---|---|---|---|
| XLRB02-002-03 Neck Base Battery Lock structure | 1 | 120 × 65 × 40 | neck base, power bank lock |
| XLRB02-003-02 Battery Locking tab | 2 | 39 × 13 × 15 | power bank lock |
| Powerbank Mount | 1 | 140 × 65 × 122 | power bank holder below the neck |
| XLRB02-006-02 Neck Front | 1 | 102 × 244 × 28 | two-part neck column (front half) |
| XLRB02-007-02 Neck Rear | 1 | 102 × 239 × 27 | two-part neck column (rear half) |
| Head Pan Servo Mount | 1 | 54 × 65 × 61 | head, pan servo (bus ID 7) |
| Head Tilt Servo Mount | 1 | 61 × 46 × 84 | head, tilt servo (bus ID 8) |
| Head Servo Case | 1 | 65 × 45 × 31 | head servo housing |
| Head Servo Case 02 | 1 | 38 × 55 × 28 | head servo housing |
| Head Cam Mount | 1 | 64 × 49 × 24 | head camera bracket |
| Head Cam Cover | 1 | 27 × 76 × 59 | head camera shell |
| Wrist Camera Mount | 1 | 58 × 35 × 56 | wrist camera bracket |
| XLRB02-201-01 Arm Mount Bottom | 1 | 122 × 18 × 5 | arm mount bar (joins the two arm bases) |
| XLRB02-202-01 Arm Mount Left | 1 | 122 × 200 × 80 | left arm mount on the top basket |
| XLRB02-203-01 Arm Mount Right | 1 | 122 × 196 × 80 | right arm mount on the top basket |
| XLRB02-204-01 Driver Board Cover | 2 | 53 × 47 × 25 | servo driver board enclosure lid |
| XLRB02-205-01 Driver Board Mount | 2 | 53 × 73 × 49 | servo driver board enclosure base |
| XLRB02-206-01 USB Hub Mount | 2 | 100 × 18 × 36 | USB hub bracket |
| XLRB02-204-03 (7) | 1 | 50 × 8 × 122 | leader-arm stand piece (named "摇操臂支架", teleop-arm bracket) |
| Leader Arm Plate Left / Right | 1 + 1 | 193 × 122 × 10 | leader (teleop) arm base plates |
| XLRB02-012-02 Omniwheel Module Mounting hub | 1 | 231 × 200 × 78 | base: hexagonal hub holding the 3 wheel modules |
| XLRB02-013-02 Bottom Section Clamp Bottom | 1 | 231 × 208 × 16 | base: clamp under the cart's bottom mesh |
| XLRB02-015-02 Bottom Section Securing plate | 1 | 186 × 161 × 10 | base: securing plate |
| XLRB02-011-03 Motor mounting bracket | 3 | 149 × 88 × 67 | wheel module housing (servo IDs 7, 8, 9) |
| XLRB02-010-02 Omniwheel Mounting Bracket | 3 | 125 × 67 × 13 | wheel module bracket |
| XLRB02-009-02 Omniwheel Bearing mount | 3 | 60 × 60 × 14 | wheel idle side, bearing |
| XLRB02-008-01 Omniwheel Servo horn adapter | 3 | 60 × 58 × 14 | wheel drive side, servo horn |
| XLRB02-016-02 Single-edge spacer 1 / 2 / 3 mm | 3 + 3 + 3 | 103 × 60 × 1–3 | shims for the wheel modules |
| Xlerobot 030 (1) | 2 + 1 + 1 | 52 × 49 × 65; 48 × 37 × 20 | unlabelled in the project |
| 夹爪 ("gripper jaw"), objects 58, 62, 64, 65 | 4 | 67 × 24 × 24 | gripper jaws |

## SO-101 arm parts (four arms: two followers, two leaders)

`Prusa_Follower_SO101` and `Prusa_Leader_SO101` objects: the standard SO-101 follower and leader prints (TheRobotStudio SO-ARM100),
laid out for four arms. Use the SO-ARM100 assembly guide for these.

## How these relate to the URDF

The URDF merges all printed structure into colour meshes on `base_link`, `head_pan_link` and `head_tilt_link`. So it fixes where the
neck, head joints and arm bases are, but it does not give each printed part's pose. Matching printed parts to the assembled shape
needs the assembly guide in the main README (phases A–E) and the photos in `assets/mechanical/`.
