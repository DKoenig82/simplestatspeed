#!/bin/sh
# Create a folder (named dmg) to prepare our DMG in (if it doesn't already exist).
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/SimpleStatSpeed.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/SimpleStatSpeed.dmg" && rm "dist/SimpleStatSpeed.dmg"
create-dmg \
  --volname "SimpleStatSpeed" \
  --volicon "media/icon.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "SimpleStatSpeed.app" 175 120 \
  --hide-extension "SimpleStatSpeed.app" \
  --app-drop-link 425 120 \
  "dist/SimpleStatSpeed.dmg" \
  "dist/dmg/"