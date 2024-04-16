# import modules
import os
import json
import shutil   #   to allow us to do some copy and overwrite operations  
from subprocess import PIPE, run    #   to run any command line 
import sys # access the command line argument


GAME_DIR_PATTERN = "game"   # keyword that we are looking for in different repo\
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

# find all game we are interested from the source directory 
def find_all_game_paths(source):
    game_paths = []

    # give the root, directory, ad files that it's walking through
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)

        break #because we only loop one time

    return game_paths

# what we want our new game directory to be
def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        # split the base path with the remaining 
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)

    return new_names

# create the target repo
def create_dir(path):
    # check if the directory already exists or not 
    if not os.path.exists(path):
        os.mkdir(path)

# copy the source into the destination
def copy_and_overwrite(source, dest):
    # overwrite the directory if it already exists 
    if os.path.exists(dest):
        shutil.rmtree(dest)

    shutil.copytree(source, dest)


# metadata json file
def make_json_metadata_file(path, game_dirs):
    # data i want to write inside the json file
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    # with automatically close the file without memory leak
    with open(path, "w") as f:
        json.dump(data, f)


# compile go code
def compile_go_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(source):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break

    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)


def run_command(command, path):
    cwd = os.getcwd()
    # change directory into the other path 
    os.chdir(path)

    # PIPE bridges the python code and the process used to run the command
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result", result)

    # change back directory
    os.chdir(cwd)

def main(source, target):
    # current directory (where we are running the file from)
    cwd = os.getcwd()     
    # it's common practise to not build yourself the path (C:// + ) because
    # depending on the OS the divider can be different, that's why we use path.join
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)

    game_paths = find_all_game_paths(source_path)
    new_game_dirs = get_name_from_paths(game_paths, "_game")

    # create the target diretory where we want to copy all the games into
    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        #compile_go_code(dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:      #file name - source file - target file
        raise Exception("you must pass a source and target directory - only.")
    
    source, target = args[1:]
    main(source, target)

