# Anycubic i3 Mega – Experimental Drawing and CNC Tools

This is a small side project with the goal of making the Anycubic i3 Mega / i3 Mega S more useful by experimenting with pen-plotter workflows and image- or vector-based G-Code generation.

**Important: This project is currently made up of beta/experimental prototypes. Nothing here should be considered finished, production-ready, or fully polished.**

A large part of the project has been **vibe-coded**

## What's included

The repository currently contains several separate experiments:

- **`Anycubic CNC V2.py`** – A Tkinter-based SVG-to-CNC tool. It loads SVG geometry, displays a preview, provides positioning and scaling controls, generates toolpaths, and exports G-Code. It works but tolerances are horibble so the only thing its currently useable for is decoration.

- **`PNG-TO-GCODE-V4.py`** – Simple PNG-to-G-Code / plotter GUI experiment. It includes bed positioning and preview controls, image quality options, pen-height settings, and G-Code export.

- **`install.bat`** – Windows helper scripts for checking or installing Python and some dependencies. They are experimental too; check what a script does before running it.

## Contributions and feedback

Bug reports, suggestions, and improvements are welcome. Since this is an early-stage personal side project, please expect rough edges and ongoing changes.

**Try it at your own risk. This project is experimental and is not an officially supported Anycubic product.**
