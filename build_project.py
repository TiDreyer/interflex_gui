from cx_Freeze import setup, Executable

from work_clock import APP_NAME_CODE, APP_NAME, APP_VERSION, APP_DESCRIPTION, VERSION_FILE_PATH


def build_app():
    app = Executable(
        script="work_clock/__main__.py",
        target_name=APP_NAME_CODE,
        base="Win32GUI",
    )

    with open(VERSION_FILE_PATH, 'w') as version_file:
        version_file.write(APP_VERSION)

    build_exe_options = {
        "build_exe": f"build/{APP_NAME_CODE}_v{APP_VERSION}",
        "include_files": [VERSION_FILE_PATH],
        "packages": ['requests', 'selenium'],
        "excludes": [
            'unittest', 'pytest',
            'cx_Freeze', 'setuptools', 'distutils',
            'ctypes', 'lib2to3', 'html',
        ],
        "optimize": 2,
    }

    # the git tag based version number might have a form like `0.1.2-15-g45c54ca-dirty`,
    # which does not follow PEP 440 and thus needs to be cleaned
    split_version_number = APP_VERSION.split('-')
    cleaned_version_number = split_version_number[0]
    if len(split_version_number) > 1:
        cleaned_version_number += f'.dev{split_version_number[1]}'

    setup(
        name=APP_NAME,
        version=cleaned_version_number,
        description=APP_DESCRIPTION,
        executables=[app],
        options={'build_exe': build_exe_options}
    )


if __name__ == '__main__':
    print(f"Building {APP_NAME} {APP_VERSION}")
    build_app()
    print(f"Done: Building {APP_NAME} {APP_VERSION}")
