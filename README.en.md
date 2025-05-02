# rush-generator

[日本語](README.md) | English

A Python tool for generating rush footage for video editing. It combines multiple video and image files, displaying timecode, cut information, staff information, and more to create preview videos for editing.

## Main Features

- Combining multiple video/image files
- Displaying timecode, timesheet, and frame numbers
- Displaying project information and cut information
- Displaying staff information
- Automatic completion for cuts without video

## Requirements

- Python 3.6 or higher
- OpenCV (opencv-python)
- Other dependencies (listed in requirements.txt)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install development packages (required for running tests)
pip install -r requirements-dev.txt
```

## Project Structure

The project has the following structure:

```
project/
├── project_info.csv     # Project settings file
├── cut_info.csv         # Cut information file
├── videos/            # Video files
│   ├── A0001/         # Cut number folder
│   │   └── A0001.mov  # Video file
│   ├── A0002/
│   │   └── A0002.png  # Image file
│   └── ...
└── out/               # Output folder
```

Note: The project includes basic sample files (2 CSV files and sample videos).

### CSV File Formats

#### project_info.csv
Defines the basic settings for the project.

```csv
project_name,width,height,fps
MyProject,1920,1080,30
```

Field descriptions:
- project_name: Project name (string)
  * Displayed in the top left of the video
  * Any string including Japanese characters can be used
- width: Output video width (pixels)
  * Recommended value: 1920 (Full HD)
  * Input materials are automatically resized to this size
- height: Output video height (pixels)
  * Recommended value: 1080 (Full HD)
  * Input materials are automatically resized to this size
- fps: Frame rate (frames per second)
  * Specified as an integer (e.g., 24, 30, 60)
  * Used for timecode calculation
  * The output video is generated at this frame rate regardless of the input material's frame rate
  * Extremely high frame rates have not been tested

#### cut_info.csv
Defines information for each cut.

```csv
cut_number,seconds,frames,status,take,staff
A0001,5,0,OK,Take1,John
A0002,3,15,NG,Take2,Mike
```

- cut_number: Cut number (must match the folder name in the video directory)
- seconds: Cut length (seconds)
- frames: Additional frame count
- status: Cut status (OK/NG, etc.)
- take: Take number
- staff: Staff member name

## Execution Method

```bash
# Using default settings (using files in the current directory)
python rush_generator.py

# Specifying paths for video directory and CSV files
python rush_generator.py --videos-dir path/to/videos \
                        --project-csv path/to/project_info.csv \
                        --cut-csv path/to/cut_info.csv \
                        --output-dir path/to/output

# Sample with specified videos directory, CSV paths, and output directory
python rush_generator.py --videos-dir videos \
                        --project-csv project_info.csv \
                        --cut-csv cut_info.csv \
                        --output-dir custom_output
```

### Directory Structure

Place folders for each cut number in the specified video directory:

```
specified directory/
└── A0001/              # Cut number folder
    └── A0001.mov       # Video file
```

Place the video or image file for each cut inside the corresponding cut folder.

### Command Line Options

- `--videos-dir`: Specifies the path to the directory containing video files
  * Default value: `videos` (the 'videos' folder in the current directory)
  * Can specify absolute or relative path
  * An error is displayed if the specified directory does not exist
- `--project-csv`: Specifies the path to the project information CSV file
  * Default value: `project_info.csv` (file in the current directory)
  * Can specify absolute or relative path
  * An error is displayed if the specified file does not exist
- `--cut-csv`: Specifies the path to the cut information CSV file
  * Default value: `cut_info.csv` (file in the current directory)
  * Can specify absolute or relative path
  * An error is displayed if the specified file does not exist
- `--output-dir`: Specifies the path to the directory where output files will be saved
  * Default value: `out` (the 'out' folder in the current directory)
  * Can specify absolute or relative path
  * The directory is automatically created if it does not exist

When executed, the following process takes place:

1. Load settings from project_info.csv and cut_info.csv
2. Process each cut folder in the specified video directory
3. Add caption information to video/image files
4. Combine all cuts
5. Output the result to the out folder (filename: rush_YYYYMMDDHHMM.mp4)

## Output Video Information

The generated video displays the following information:

- Top left: Project name
- Bottom left: Timesheet information
- Top center: Cut number, take number, status
- Center: Total timecode
- Top right: Staff information
- Bottom right: File update date
- Bottom center: Timecode, timesheet, frame number

![rush_202501261504](https://github.com/user-attachments/assets/bd47faff-7a91-49ae-ad51-ec1f3fe52075)

## Notes

- Supported video file formats: .mp4, .avi, .mov
- Supported image file formats: .jpg, .png, .jpeg
- If a cut folder is empty, a solid color video of the specified length will be generated
- If a cut folder does not exist, a solid color video will be generated, just like with an empty folder
