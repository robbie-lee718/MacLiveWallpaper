# What is LiveWallpaper
LiveWallpaper is a small python script to load your .mp4 as live wallpapers for Mac. This is a free open-source alternative to other live wallpaper apps. If you have a video then you can have a live wallpaper.

** Only works for Mac **

Note: depending on the video (quality, length, etc.) you may experience loss of performance.


# How to Run
### Create venv and install requirements
`Python -m venv .venv`
`source .venv/bin/activate`
`pip install requirements.txt`

### Create Folders
Create a bin folder at `~/bin` (If not already exist)
Create a Movies folder at `~/Movies` (If not already exist)

### Move files into folders
Copy/Move LiveWallpaper Directory into `~/bin`
Move your .mp4 into `~/Movies`

### Move launch script
**IMPORTANT: Change YOU to your users name, and change the python path to the venv's python path**
Copy/Move `com.me.livewallpaper.plist` to `~/Library/LaunchAgents`
*This will allow the script to load at device startup*

To change which .mp4 you want just edit the path to the mp4 in `com.me.livewallpaper.plist`

**See instructions below to load/unload**

## Launch Commands
### Load:
`launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.me.livewallpaper.plist`

### Unload:
`launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.me.livewallpaper.plist`

### Check if Running:
`launchctl list | grep livewallpaper`

### See Errors:
`cat /tmp/livewallpaper.err'


# Requirements
- Python


# Running without Launch script
If you would like to run without using launch commands create a venv and load from requirements.txt. From there just run live_wallpaper.py followed by your file path.
- Create venv: `Python -m venv .venv`
- Load venv: `source .venv/bin/activate`
- Install requirements: `pip install requirements.txt`
- Run LiveWallpaper: `Python live_wallpaper.py ~/your/file/path.mp4`
