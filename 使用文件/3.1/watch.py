from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import threading
dcmp_file_list={}
def file_op(kerninfo_name):
	
    f=open('/home/pdy/kernel_info/'+kerninfo_name,"r");
    info=f.read()
    print(info)
    f_status=info[:info.find(',')]
    f.close()
    if f_status=="rd":
        f_path=info[info.find(',')+1:]
        df_path=f_path[:f_path.rfind('/')+1]+'.'+f_path[f_path.rfind('/')+1:]+'.dcmp'
        os.system('mv {} {}'.format(f_path,f_path+'.cmp'))
        os.system('./fqz_comp -d {} {}'.format(f_path+'.cmp',df_path))
        os.system('mv {} {}'.format(f_path+'.cmp',f_path))
        f=open('/home/pdy/kernel_op/'+kerninfo_name,"w")
        print("KERN DEBUG")
        f.write("1")
        f.close()
        dcmp_file_list[df_path]='{},{},{},{}'.format(time.time(),kerninfo_name,"rd",f_path)
    elif f_status=="wt":
        f_path=info[info.find(',')+1:]
        df_path=f_path[:f_path.rfind('/')+1]+'.'+f_path[f_path.rfind('/')+1:]+'.dcmp'
        f=open('/home/pdy/kernel_op/'+kerninfo_name,"w")
        f.write("1")
        f.close()
        dcmp_file_list[df_path]='{},{},{},{}'.format(time.time(),kerninfo_name,"wt",f_path)
    elif f_status=="mv":
        old_path,f_path=info[info.find(',')+1:].split(',')
        if old_path[old_path.rfind('.')+1:]=='fq':
            df_path=old_path[:old_path.rfind('/')+1]+'.'+old_path[old_path.rfind('/')+1:]+'.dcmp'
            if os.path.exists(df_path):
                new_df_path=f_path[:f_path.rfind('/')+1]+'.'+f_path[f_path.rfind('/')+1:]+'.dcmp'
                os.system('mv {} {}'.format(df_path,new_df_path))
                os.system('mv {} {}'.format(old_path,old_path+'.cmp'))
                os.system('mv {} {}'.format(old_path+'.cmp',f_path))
                old_kerninfo_name=old_path.replace('/','%')+'.kernel'
                #os.system('rm {}'.format('/home/pdy/kernel_op/'+old_kerninfo_name))
                del dcmp_file_list[df_path]
                f=open('/home/pdy/kernel_op/'+kerninfo_name,"w")
                f.write("1")
                f.close()
                dcmp_file_list[new_df_path]='{},{},{},{}'.format(time.time(),kerninfo_name,"mv",f_path)
            else:
                del dcmp_file_list[df_path]
                os.system('mv {} {}'.format(old_path,old_path+'.cmp'))
                os.system('mv {} {}'.format(old_path+'.cmp',f_path))
                dcmp_file_list[new_df_path]='{},{},{},{}'.format(time.time(),kerninfo_name,"mv",f_path)
        else:
            df_path=f_path[:f_path.rfind('/')+1]+'.'+f_path[f_path.rfind('/')+1:]+'.dcmp'
            os.system('mv {} {}'.format(old_path,df_path))
            os.system('./fqz_comp {} {}'.format(df_path,f_path+'.cmp'))
            os.system('mv {} {}'.format(f_path+'.cmp',f_path))
            f=open('/home/pdy/kernel_op/'+kerninfo_name,"w")
            f.write("1")
            f.close()
            dcmp_file_list[df_path]='{},{},{},{}'.format(time.time(),kerninfo_name,"mv",f_path)

    #os.system('rm {}'.format('/home/pdy/kernel_info/'+kerninfo_name))

def check_dcmp_file():
    end_time=time.time()
    del_needed=[]
    for df_path in dcmp_file_list:
        start_time,kerninfo_name,op,f_path=dcmp_file_list[df_path].split(',')
        start_time=float(start_time)
        if end_time-start_time>10:
            if  os.path.exists(f_path) and os.path.getsize(f_path)==0:
                os.system('./fqz_comp {} {}'.format(df_path,f_path+'.cmp'))
                os.system('mv {} {}'.format(f_path+'.cmp',f_path))
            os.system('rm {}'.format(df_path))
            f=open('/home/pdy/kernel_op/'+kerninfo_name,"w")
            f.write("0")
            f.close()
            del_needed.append(df_path)
    for df_path in del_needed:
        del dcmp_file_list[df_path]
    global timer
    timer=threading.Timer(30,check_dcmp_file)
    timer.start()
class MyDirEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))

    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))
            kerninfo_path=event.src_path
            kerninfo_name=kerninfo_path[kerninfo_path.rfind('/'):][1:]
            file_op(kerninfo_name)

if __name__=='__main__':
    observer=Observer()
    fileHandler=MyDirEventHandler()
    observer.schedule(fileHandler,"/home/pdy/kernel_info",True)
    observer.start()
    timer=threading.Timer(30,check_dcmp_file)
    timer.start()
    try:
        while True:
            time.sleep(0.00001)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
    timer.join()
