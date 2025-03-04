# Waypoint Editor

This is a graphical application to create a waypoints file that can be used by the EEGsynth robots to move over the stage according to a predefined list of waypoints.

You can use one of the template images for the stage, or read a stage plan from a bitmap file. 

The bottom of the image that will be displayed corresponds to the audience, the top of the screen to the back of the stage. Positive x values are to the top of the screen, away from the audience. Positive y values are to the left of the screen and audience. Positive rotations are counter-clock-wise.

When reading the stage plan from a file, you must specify the resolution of the image as pixels-per_meter. The default for the built-in templates is 300 pixels-per-meter. To determine the resolution in your image or drawing, you can click two known points in the image to make a path that consists of a single segment, look at the number of pixels that the path corresponds to, and divide that by the known distance.

Press Z to clear the last point. Press C to clear all points.

After clicking on the points that you want the robot to travel along, you have to specify in the settings tab the "total duration" (in seconds) that the path will take. The application will compute a constant speed over all segments that corresponds with the requested duration. You can also specify the "total rotation", which will cause the robot to rotate (also evenly distributed) over the whole path.

To insert a pause or to change the robot to go faster or slower over some segments of the specified path, you will have to importy the waypoints into Excel or Numbers and edit the table there.  

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
