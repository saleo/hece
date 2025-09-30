"""
HEMouse Build Script
Creates standalone executable using PyInstaller
"""
import PyInstaller.__main__
import os
import sys


def build():
    """Build HEMouse executable"""
    print("=" * 60)
    print("HEMouse Build Script")
    print("=" * 60)

    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found!")
        print("   Please run this script from the hemouse/ directory")
        sys.exit(1)

    print("\n🔨 Building HEMouse.exe...")

    # PyInstaller arguments
    args = [
        'main.py',
        '--onefile',                    # Single executable
        '--windowed',                   # No console window
        '--name=HEMouse',              # Output name
        '--clean',                      # Clean cache
        '--noconfirm',                  # Overwrite without asking

        # Hidden imports (explicitly include modules)
        '--hidden-import=win32api',
        '--hidden-import=win32con',
        '--hidden-import=win32gui',
        '--hidden-import=pywinauto',
        '--hidden-import=pywinauto.application',
        '--hidden-import=pywinauto.controls',
        '--hidden-import=pywinauto.controls.uiawrapper',

        # Add data files (if any)
        # '--add-data=assets;assets',
    ]

    # Add icon if exists
    if os.path.exists('assets/icon.ico'):
        args.append('--icon=assets/icon.ico')
        print("✅ Using custom icon")
    else:
        print("⚠️ No icon found (assets/icon.ico)")

    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("✅ Build completed successfully!")
        print("=" * 60)
        print("\n📦 Output: dist/HEMouse.exe")
        print(f"📊 Size: {os.path.getsize('dist/HEMouse.exe') / (1024*1024):.2f} MB")
        print("\n🚀 To run: dist\\HEMouse.exe\n")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    build()