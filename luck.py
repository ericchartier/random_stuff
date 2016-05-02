import subprocess
import time
import threading
import sys


start_block = None

known_string = None

if len(sys.argv) > 1:
    known_string = sys.argv[1]
 
if len(sys.argv) > 2:
    start_block = sys.argv[2]
   

#start_block = '4277958'
#known_string = 'threading.Thread'
keep_trying = True

def main_loop(block_data, data_lock):

    print 'main_loop'
    while True:
        data_len = len(block_data)
        #print 'data len : ' + str(data_len)
        if data_len < 1:
            time.sleep(5)
            continue
        if known_string in block_data[0]:
            print block_data[0]
            keep_trying = False
            #sys.exit()
        data_lock.acquire()
        del block_data[:1]
        data_lock.release()
        

block_data = []
data_lock = threading.Lock()
t = threading.Thread(None, main_loop, 'fuck_this', [block_data, data_lock])

t.daemon = True
t.start()


proc = subprocess.Popen(['sudo', 'debugfs', '/dev/sda1'], bufsize=1, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
proc.stdin.write( 'dump_unused\n')

readdata = ''
first_find_done = False
block_str = ''
savepoint_reached = False
block_count = 0
last_line = ''
while keep_trying:
    readdata += proc.stdout.read(512)

    for line in readdata.split('\n'):
        last_line = ''
        if 'Unused block' in line:
            if first_find_done:

                data_lock.acquire()
                block_data.append(block_str)
                data_lock.release()
                #first_find_done = False
                block_str = ''

            else:
                if start_block is None:
                    savepoint_reached = True
                elif start_block in line:
                    savepoint_reached = True
                    print 'reached save point : ' + line

            if savepoint_reached:
                first_find_done = True
                block_count += 1
                if block_count == 2000:
                    print line
                    block_count = 0
        if savepoint_reached :
            block_str += line + '\n'
            #block_str += line 
    readdata = last_line

