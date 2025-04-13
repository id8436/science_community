import subprocess

with open('requirements_window.txt') as f:
    for line in f:
        pkg = line.strip()
        if not pkg or pkg.startswith('#'):
            continue
        print(f"Installing: {pkg}")
        try:
            subprocess.check_call(['pip', 'install', pkg])
        except subprocess.CalledProcessError:
            print(f"Failed to install: {pkg}")