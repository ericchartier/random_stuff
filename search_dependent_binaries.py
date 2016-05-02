# this script goes through a list of directories containing executables
# and execute ldd on each of them to see who depends on a particular
# shared library object. This is useful in case you want to modify a 
# global shared library but you are not sure of the impact this is going to
# have system wide


import subprocess
import os
import json

searched_shared_lib = ['libvmwareui.so']



LDD_DB_NAME = 'ldd_db.json'
directories_list = ['/bin/', '/sbin', '/lib', '/lib32', '/lib64', '/usr/bin', '/usr/sbin', '/usr/lib', '/usr/lib32', '/usr/libx86_64-linux-gnu', '/usr/local/bin', '/usr/local/lib', '/usr/local/sbin']
#directories_list = directories_list[:2]

def build_ldd_database():
    database = {}
    for folder in directories_list:
        print 'Going through ' + folder
        dirs = set()
        for dirpath, dirnames, filenames in os.walk(folder, True, None, True):
    
            # This is to handle infinite recursion due to symlinks
            st = os.stat(dirpath)
            scandirs = []
            for dirname in dirnames:
                st = os.stat(os.path.join(dirpath, dirname))
                dirkey = st.st_dev, st.st_ino
                if dirkey not in dirs:
                    dirs.add(dirkey)
                    scandirs.append(dirname)
            dirnames[:] = scandirs
    
            for found_file in filenames:
                filepath = os.path.join(dirpath, found_file)
                proc = subprocess.Popen(['ldd', filepath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                proc.wait()
                dependencies = []
                for line in proc.stdout.readlines():
                    dependencies.append(line)
                database[found_file] = {"binary_name": found_file, "path": filepath, "dependencies": dependencies}
    return database

def search_db_for_string(database, searched_lib):
    found_dependents = []
    found_count = 0
    for key in database.keys():
        current_bin = database[key]
        for dependencies in current_bin["dependencies"]:
            if searched_lib in dependencies:
                found_dependents.append(current_bin["path"])
                found_count += 1
    print 'Found ' + str(found_count) + ' dependents / ' + str(search_count) + ' search files'
    for dependent in found_dependents:
        print dependent
    return found_dependents

def load_ldd_db(db_filepath):
    ldd_db = {}
    if os.path.isfile(db_filepath):
        with open(db_filepath, 'r') as f:
            data = f.read()
            ldd_db = json.loads(data)
    else:
        ldd_db = build_ldd_database()
        with open(db_filepath, 'w') as f:
            f.write(json.dumps(ldd_db))

    return ldd_db



def main():
    ldd_db = load_ldd_db(LDD_DB_NAME)
    for lib in searched_shared_lib:
        dependents = search_db_for_string(ldd_db, lib)
        for deplib in dependents:
            libname = os.path.basename(deplib)
            print libname
            search_db_for_string(ldd_db, libname)



if __name__ == '__main__':
    main()


