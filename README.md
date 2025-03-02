# Waypoint Editor

This is a graphical application to create a waypoints file that can be used by the EEGsynth robots to move over the stage.

It allows reading a stage plan as bitmap image, or you can use one of the template images. The resolution of the image must be specified (in pixels per meter). The default for the built-in templates ios 300 pixels-per-meter.

The bottom of the screen corresponds to the audience, the top of the screen to the back of the stage.

After clicking on a number of points that you want the robot to follow, you have to specify the total duration that the path will take. The application will compute a constant speed over all segments so that the path will be completed withing the requested time. You can also specify a total rotation, which will cause the robot to rotate (also evenly) over the whole path.

Positive x values are to the top of the screen, away from the audience. Positive y values are to the left of the screen and audience. Positive rotations are counter-clock-wise.

## Making a packaged executable

On macOS it is possible to package this into `waypointeditor.app` by using

    pyinstaller --onefile src/waypointeditor.py 

## License

Copyright (C) 2025, Robert Oostenveld

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
