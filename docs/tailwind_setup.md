# Tailwind CSS Setup for BTG

This document explains how Tailwind CSS and DaisyUI are set up in the Build Together (BTG) project.

## Overview

BTG is transitioning from Bootstrap 5 to Tailwind CSS + DaisyUI incrementally. During the migration, both frameworks will coexist to ensure a smooth transition.

## Setup Components

1. **Tailwind CSS Standalone CLI**: We use the standalone CLI to avoid Node.js dependencies, making it easier to package BTG as a pip package.
2. **DaisyUI**: Added via CDN for consistent component styling with a dark theme by default.
3. **Build Script**: A simple shell script (`build_tailwind.sh`) to compile Tailwind CSS.

## Development Workflow

### Initial Setup

1. Download the Tailwind CSS standalone CLI:
   ```bash
   # For macOS ARM (M1/M2)
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
   chmod +x tailwindcss-macos-arm64
   
   # For macOS Intel
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-x64
   chmod +x tailwindcss-macos-x64
   
   # For Linux
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
   chmod +x tailwindcss-linux-x64
   
   # For Windows
   # Download from https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-windows-x64.exe
   # Rename to tailwindcss.exe
   ```

### Developing with Tailwind CSS

1. Run the build script in watch mode to automatically rebuild when files change:
   ```bash
   ./build_tailwind.sh --watch
   ```

2. Make changes to your HTML templates using Tailwind CSS classes.

3. The Flask server will automatically detect changes to the compiled CSS file.

### Building for Production

1. Run the build script with the production flag to generate minified CSS:
   ```bash
   ./build_tailwind.sh --production
   ```

2. The minified CSS will be output to `app/static/css/tailwind.css`.

## Packaging for pip

When packaging BTG for pip installation:

1. Build the production version of Tailwind CSS:
   ```bash
   ./build_tailwind.sh --production
   ```

2. Include the compiled CSS file in your package's MANIFEST.in:
   ```
   include app/static/css/tailwind.css
   ```

3. No Node.js or other non-Python dependencies are required for installation.

## Migration Strategy

1. Components are being migrated incrementally from Bootstrap to Tailwind CSS + DaisyUI.
2. Both frameworks will coexist during the migration.
3. Bootstrap will be removed only after all components have been successfully migrated.

## File Structure

- `tailwind.config.js`: Configuration for Tailwind CSS
- `app/static/css/tailwind/input.css`: Source CSS file with Tailwind directives
- `app/static/css/tailwind.css`: Compiled Tailwind CSS output
- `build_tailwind.sh`: Build script for compiling Tailwind CSS

## Troubleshooting

- If styles aren't updating, try a hard refresh in your browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows).
- Check the Flask debug console for any CSS-related errors.
- Ensure the build script has executable permissions: `chmod +x build_tailwind.sh`
