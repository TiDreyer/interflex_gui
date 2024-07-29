# Interflex Work Clock

A simple GUI that can be run as a standalone Windows app to clock in and out of
work without manually using the Interflex WebClient in a browser.
This Version was tested with the Interflex WebClient in Version 1.87.

![Screenshot of version 0.4.0](misc/screenshot.png)


## How does it work?

On the first use, configure the Tool with your companies Interflex WebClient
base URL and your personal credentials for the login.
This data will be saved for the next sessions **in clear text** under the path
`C:\Users\<USERNAME>\AppData\local\interflex_work_clock\`,
so please make sure you are the only one with access to the used Windows
account.

After initial setup, you can use the update and clock in/out buttons to check
your work time and clock in/out.
The Tool will use [Selenium](https://www.selenium.dev/) to open a hidden browser
in the background and perform the necessary actions in the WebClient.
You can activate the "Debug Mode" in the settings to make this browser window
visible and observe the actions in real time.


## How to build it

Checkout the version you want to build, e.g. `0.4.0`:
```bash
git clone git@github.com:TiDreyer/interflex_gui.git
cd interflex_gui
git checkout 0.4.0
```

Install the necessary dependencies and run the build script.
I recommend doing this in a virtual environment.
Notice that the requirements are subject to their own licenses.
```bash
python3.12 -m pip install -r requirements.txt
python3.12 build_project.py
```

This script will run [cx-Freeze](https://pypi.org/project/cx-Freeze/) to create
a Windows executable that can be run without any further requirements.
After a successful build, the `build` directory contains a folder called
`interflex_work_clock_v0.4.0`.
Copy this entire folder to where ever you like on your system.
Run the contained `interflex_work_clock.exe` to start the GUI.


## Want Autostart?

Create a link to your `interflex_work_clock.exe` inside the directory
`C:\Users\<USERNAME>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`.
