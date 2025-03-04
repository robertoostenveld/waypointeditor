#!/bin/sh

if [ ! -d "dist/Waypoint Editor.app" ]; then
  echo Error: The app bundle does not exist, you should build it first.
  exit 1
fi

# Create a folder that will be converted to a disk image.
mkdir -p dist/dmg

# Empty the dmg folder.
rm -rf dist/dmg/*

# If the disk image already exists, delete it.
[ -f "dist/Waypoint Editor.dmg" ] && rm "dist/Waypoint Editor.dmg"

# Copy the app bundle to the dmg folder.
cp -r "dist/Waypoint Editor.app" dist/dmg

create-dmg \
  --volname "Waypoint Editor" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "Waypoint Editor.app" 175 120 \
  --hide-extension "Waypoint Editor.app" \
  --app-drop-link 425 120 \
  "dist/Waypoint Editor.dmg" \
  "dist/dmg/"
