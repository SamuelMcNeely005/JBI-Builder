import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from datetime import datetime
import os 
import json
import re
import sys

def get_resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class StartWindow():
     def __init__(self):
         
         self.icon_path = get_resource_path("job_template_icon.ico")

         self.root = tk.Tk()
         self.root.geometry("400x200")
         self.root.resizable(False, False)
         self.root.title("JBI Builder")
         self.root.iconbitmap(self.icon_path)
         
         self.title_frame = tk.Frame(self.root)
         self.title_frame.pack(padx=20, pady=20)
         self.title_label = tk.Label(self.title_frame, text="JBI Builder", font=('Times', 25), foreground='#0056b9')
         self.title_label.pack(padx=1, pady=1)

         self.button_frame = tk.Frame(self.root)
         self.button_frame.pack(padx=2, pady=2)
         
         self.robot_job_btn = tk.Button(self.button_frame, text="Create Robot Job",  fg='white', bg='#0056b9', command=self.create_robot_job)
         self.robot_job_btn.pack(padx=10, pady=10, side='left')
         
         self.macro_job_btn = tk.Button(self.button_frame, text="Create Macro Job", fg='white', bg='#0056b9', command=self.create_macro_job)
         self.macro_job_btn.pack(padx=10, pady=10, side='left')

         self.robot_win = None
         self.macro_win = None

         self.data_dir = os.path.join(os.path.expanduser("~"), ".jbi_builder")
         self.data_file = os.path.join(self.data_dir, "path_data.json")
        
         self.path_data_list = []
         self.path_setup_required = False

         os.makedirs(self.data_dir, exist_ok=True)


         if os.path.exists(self.data_file):
             with open(self.data_file, "r") as f:
                 json_path_data = json.load(f)
                 for key, value in json_path_data.items():
                     self.path_data_list.append(key)
         else:
             with open(self.data_file, "w") as f:
                 data = {}
                 data["~"] = os.path.expanduser("~")
                 json.dump(data, f, indent=4)
                 self.path_data_list.append("~")
             self.path_setup_required = True

         self.directory_frame = tk.Frame(self.root)
         self.directory_frame.pack(padx=2, pady=2)

         self.directory_btn = tk.Button(self.directory_frame, text="Add Save Directory", command=self.add_path)
         self.directory_btn.configure(fg='white', bg="grey")
         self.directory_btn.pack(padx=1,pady=1)
         
         self.directory_entry = ttk.Combobox(self.directory_frame, values=self.path_data_list, width=20)
         self.directory_entry.set(self.path_data_list[-1])
         self.directory_entry.configure(state='readonly')
         self.directory_entry.pack(padx=1,pady=1)

     def add_path(self):
         directory_path = filedialog.askdirectory(title="Select Folder", initialdir="/")
         if directory_path == "":
             return
         else:
             with open(self.data_file,'r') as f:
                 data = json.load(f)
             with open(self.data_file, 'w') as f:
                 data[os.path.basename(directory_path)] = directory_path
                 json.dump(data, f, indent=4)
             
             self.path_data_list.append(os.path.basename(directory_path))
             self.directory_entry.configure(state='normal')
             self.directory_entry.delete(0, tk.END)
             self.directory_entry['values'] = self.path_data_list
             self.directory_entry.set(self.path_data_list[-1])
             self.directory_entry.configure(state='readonly')

     def create_robot_job(self):
         if self.robot_win and self.robot_win.window.winfo_exists():
             self.robot_win.window.lift() 
         else:
             with open(self.data_file, 'r') as f:
                 data = json.load(f)
             folder = self.directory_entry.get()
             folder_path = data.get(folder)
             self.robot_win = JobWindow(self.root, False, folder_path)


     def create_macro_job(self):
         if self.macro_win and self.macro_win.window.winfo_exists():
             self.macro_win.window.lift() 
         else:
             with open(self.data_file, 'r') as f:
                 data = json.load(f)
             folder = self.directory_entry.get()
             folder_path = data.get(folder)
             self.macro_win = JobWindow(self.root, True, folder_path)
     
class JobWindow():
     def __init__(self, root, macro_bool, save_path):
         
         self.icon_path = get_resource_path("job_template_icon.ico")

         self.macro_bool = macro_bool
         self.save_path = save_path
         
         self.root = root
         self.window = tk.Toplevel(self.root)
         self.icon_path = get_resource_path("job_template_icon.ico")
         self.window.iconbitmap(self.icon_path)
         if macro_bool == True:
             self.window.geometry("300x320")
             self.window.title("Macro Job Menu")
         else:
             self.window.geometry("300x280")
             self.window.title("Robot Job Menu")
         
         self.window.resizable(False, False)
         
         # Name
         self.name_entybox_frame = tk.Frame(self.window, highlightbackground="#0056b9", highlightthickness=2)
         self.name_entybox_frame.pack(padx=3,pady=3, fill=None, expand=False)
         self.name_entrybox = EntryBox(self.name_entybox_frame, 25, "Enter Job Name")
         self.name_entrybox.entry.pack(padx=10, pady=10)

         # Control Group 
         self.grp_subwin = None
         self.controlgrp_select_frame = tk.Frame(self.window, highlightbackground="#0056b9",
                                                  highlightthickness=2)
         self.controlgrp_select_frame.pack(padx=3,pady=3,fill=None, expand=False)
         self.controlgrp_select = tk.Button(self.controlgrp_select_frame, text="Select Control Group", 
                                            command=self.open_controlgroup, fg='white', bg='#0056b9')
         self.controlgrp_select.pack(padx=5, pady=5)
         self.controlgrp_result = tk.Entry(self.controlgrp_select_frame, width=20)
         self.controlgrp_result.insert(0, "Waiting...")
         self.controlgrp_result.config(state="readonly") 
         self.controlgrp_result.pack(padx=1,pady=1)

         # Local Variables
         self.lvar_subwin = None
         self.lvar_select_frame = tk.Frame(self.window, highlightbackground='#0056b9', highlightthickness=2)
         self.lvar_select_frame.pack(padx=3,pady=3,fill=None, expand=False)
         self.lvar_select = tk.Button(self.lvar_select_frame, text="Add Local Variables", 
                                      command=self.open_lvars, fg='white',bg='#0056b9') 
         self.lvar_select.pack(padx=5, pady=5)
         self.lvar_result = tk.Entry(self.lvar_select_frame, width=40)
         self.lvar_result.insert(0, "LB:0, LI:0, LD:0, LR:0, LS:0, LP:0, LBP:0, LEX:0")
         self.lvar_raw_result = tk.Entry(self.window, width=40)
         self.lvar_raw_result.insert(0, "None")
         self.lvar_result.config(state="readonly") 
         self.lvar_result.pack(padx=1,pady=1)
         
         # Coordinate Select
         self.job_type_select_frame = tk.Frame(self.window, highlightbackground='#0056b9', highlightthickness=2)
         self.job_type_select_frame.pack(padx=3, pady=3, fill=None, expand=False)
         self.job_type_select_var = tk.BooleanVar()
         self.job_type_select_check = tk.Checkbutton(self.job_type_select_frame, text="Relative Job", 
                                                     variable=self.job_type_select_var, command=self.coord_options)
         self.job_type_select_check.pack(side='left', padx=3, pady=3)

         self.coor_list_standard = ['PULSE']
         self.coor_list_rel = ['ROBOT', 'BASE']
         for i in range(1, 65):
             self.coor_list_rel.append(f"USER {i}")
         self.coor_select = ttk.Combobox(self.job_type_select_frame, state='readonly')
         self.coor_select.configure(state='normal')
         self.coor_select.set(self.coor_list_standard[0])
         self.coor_select.configure(state='readonly')
         self.coor_select.pack(side='left', padx=3, pady=3 )
         
         # Macro Arguments
         self.args_subwin = None        
         if self.macro_bool == True:
             self.arg_setup_frame = tk.Frame(self.window, highlightbackground='#0056b9', highlightthickness=2)
             self.arg_setup_btn = tk.Button(self.arg_setup_frame, text="Add Arguments", fg='white', 
                                            bg='#0056b9', command=self.open_args)
             self.arg_setup_frame.pack(padx=1, pady=1)
             self.arg_setup_btn.pack(padx=3, pady=3)
             self.argset_entry = tk.Entry(self.window, width=40)
             self.argset_entry.insert(0, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
             self.argtype_entry = tk.Entry(self.window, width=40)
             self.argtype_entry.insert(0, ",,,,,,,,,,,,,,,")
             self.tagdisp_entry = tk.Entry(self.window, width=40)
             self.tagdisp_entry.insert(0, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
             self.taginit_entry = tk.Entry(self.window, width=40)
             self.taginit_entry.insert(0, "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

         self.create_btn = tk.Button(self.window, text="Create Job", command=self.create_job, 
                                     fg='white', bg='green')
         self.create_btn.pack(padx=15,pady=15)
     
     def open_controlgroup(self):
         if self.grp_subwin and self.grp_subwin.window.winfo_exists():
             self.grp_subwin.window.lift() 
         else:
             self.grp_subwin = GrpSubWin(self.window, self.controlgrp_result)

     def open_lvars(self):
         if self.lvar_subwin and self.lvar_subwin.window.winfo_exists():
             self.lvar_subwin.window.lift() 
         else:
             self.lvar_subwin = LvarSubWin(self.window, self.lvar_result, self.lvar_raw_result)

     def open_args(self):
         if self.args_subwin and self.args_subwin.window.winfo_exists():
             self.args_subwin.window.lift() 
         else:
             self.args_subwin = ArgSubWin(self.window, self.argset_entry, self.argtype_entry, 
                                          self.tagdisp_entry, self.taginit_entry)

     def coord_options(self):
         flag_state = self.job_type_select_var.get()
         if flag_state == True:
             self.coor_select['values'] = self.coor_list_rel
             self.coor_select.set(self.coor_list_rel[0])
         else:
             self.coor_select['values'] = self.coor_list_standard
             self.coor_select.set(self.coor_list_standard[0])

     def create_job(self):           
         # Handle Name 
         job_name_regex = r"^[A-Z0-9_!-]{1,32}$"
         job_name = self.name_entrybox.entry.get()
         job_name_corrected = job_name.upper().replace(" ", "_")
         if re.fullmatch(job_name_regex, job_name_corrected) == None:
             messagebox.showwarning("Name Error", "Warning! Job name must be between 1-32 characters")
             return
         
         # Handle Control Group
         control_group = self.controlgrp_result.get()
         print(control_group)
         if control_group == "Non Group" or control_group == "Waiting...":
             non_group = True
         else: 
             non_group = False
         
         control_group = control_group.split()
         
         control_group_1 = None
         control_group_2 = None
  
         handler = {

             "R1" : "RB1",
             "R1B1": "RB1,BS1",
             "R1B2" : "RB1,BS1",
             "R2" : "RB2",
             "R2B2": "RB2,BS2",
             "R2B1": "RB2,BS1",
             "R3" : "RB3",
             "R3B1": "RB3,BS1",
             "R3B2": "RB3,BS2",
             "S1" : "ST1",
             "S1B1" : "ST1,BS1",
             "S1B2" : "ST1,BS2",
             "S2" : "ST2",
             "S2B1" : "ST2,BS1",
             "S2B2" : "ST2,BS2",
             "S3" : "ST3",
             "S3B1" : "ST3,BS1",
             "S3B2" : "ST3,BS2",

         }

         if non_group == True:
             control_group_1 = "Non Group"
         elif len(control_group) == 1:
             control_group_1 = handler.get(control_group[0])
             control_group_2 = False
         elif len(control_group) == 3:
             one = handler.get(control_group[0])
             two = handler.get(control_group[2])
             control_group_1 = f"{one},{two}"
             control_group_2 = False
         elif len(control_group) == 5:
             result1 = handler.get(control_group[0])
             result2 = handler.get(control_group[2])
             result3 = handler.get(control_group[4])
             control_group_1 = f"{result1},{result2}"
             control_group_2 = f"{result3}"

         # Handle Lvars
         lvars = self.lvar_raw_result.get()
         if lvars != "None":
             lvars = lvars.split()
             result_string_lvars = f"{lvars[0]},{lvars[1]},{lvars[2]},{lvars[3]},{lvars[4]},{lvars[5]},{lvars[6]},{lvars[7]}"
         else: 
             result_string_lvars = "None"
         
         print(result_string_lvars)
                    
         # Handle Job Type
         job_type = self.coor_select.get()
         relative_flag = False

         if job_type == "ROBOT" or job_type == "BASE" or job_type.startswith('USER'):
             relative_flag = True
         else:
             relative_flag = False


         # Handle Macro Lines

         if self.macro_bool == True:
             argset = self.argset_entry.get()
             argtype = self.argtype_entry.get()
             tag_disp = self.tagdisp_entry.get()
             
             try:
                 argnames = self.args_subwin.arg_names
             except:
                 argnames = [None]

             try:
                 argunits = self.args_subwin.arg_unit
             except:
                 argunits = [None]

             try:
                 tagcomms = self.args_subwin.tag_comms
             except:
                 tagcomms = [None]

        
         # Get Date

         date = datetime.now()
         formatted_date = date.strftime("%Y/%m/%d %H:%M")

         # Build Job
         job_lines = []
         
         job_lines.append("/JOB")
         job_lines.append(f"//NAME {job_name_corrected}")
         job_lines.append("//POS")
         job_lines.append("///NPOS 0,0,0,0,0,0")
         
         if self.macro_bool == True:
             job_lines.append("//MACRO")
             # ATTR
             job_lines.append("///SUSJOB")
             
             if argset == "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0":
                 attr_2 = "0"
             else:
                 attr_2 = "1"
             job_lines.append(f"///ATTR 1,0,{attr_2},0,0,0,0,0")
             
             job_lines.append(f"///ARGSET {argset}")
             job_lines.append(f"///ARGTYPE {argtype}")
             
             if argnames[0] == None: 
                 pass
             else:
                 job_lines.append("///ARGNAME")
                 print(f"names: {argnames}")
                 for name in argnames:
                     job_lines.append(name)

             if argunits[0] == None: 
                 pass
             else:
                 job_lines.append("///ARGUNIT")
                 print(f"units: {argunits}")
                 for unit in argunits:
                     job_lines.append(unit)
             
             job_lines.append(f"///TAGDISP {tag_disp}")
             
             if tagcomms[0] == None: 
                 pass
             else:
                 job_lines.append("///TAGCOMM")
                 print(f"comments: {tagcomms}")
                 for comm in tagcomms:
                     job_lines.append(comm)
             
             job_lines.append("///TAGINIT 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

         job_lines.append("//INST")
         job_lines.append(f"///DATE {formatted_date}")
         
         if relative_flag == True and self.macro_bool == True:
             job_lines.append("///ATTR SC,RW,RJ,MC")
             job_lines.append(f"////FRAME {job_type}")
         elif relative_flag == True and self.macro_bool == False:
             job_lines.append("///ATTR SC,RW,RJ")
             job_lines.append(f"////FRAME {job_type}")
         elif self.macro_bool == True and relative_flag == False:
             job_lines.append("///ATTR SC,RW,MC")
         else:
             job_lines.append("///ATTR SC,RW")

         if control_group_1 == "Non Group":
             pass
         elif control_group_1 and not control_group_2:
             job_lines.append(f"///GROUP1 {control_group_1}")
         elif control_group_1 and control_group_2:
             job_lines.append(f"///GROUP1 {control_group_1}")
             job_lines.append(f"///GROUP2 {control_group_2}")

         if result_string_lvars == "None":
             pass
         else:
             job_lines.append(f"///LVARS {result_string_lvars}")

         job_lines.append("NOP")
         job_lines.append(r"'********************************")
         job_lines.append(rf"' {job_name}")
         job_lines.append(r"'********************************")
         if self.macro_bool == True and argset != "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0":
             job_lines.append(r"' ")
             job_lines.append(r"'================================")
             job_lines.append(r"' Argument Info:")
             job_lines.append(r"' ")
             for info in self.args_subwin.arg_info:
                 job_lines.append(rf"' {info}")
             job_lines.append(r"' ")
             job_lines.append(r"'================================")
         job_lines.append("*TOP")
         job_lines.append(r"'--------------------------------")
         job_lines.append(r"' ")
         job_lines.append(r"' insert code here...")
         job_lines.append(r"' ")
         job_lines.append(r"'--------------------------------")
         job_lines.append("*OUT")
         job_lines.append(r"'********************************")
         job_lines.append("END")

         # build file

         job_path = os.path.join(self.save_path, f"{job_name_corrected}.JBI")
         try:
             with open(job_path, 'w') as f:
                 for line in job_lines:
                     f.write(line)
                     f.write("\n")
                 os.startfile(job_path)
         except:
             messagebox.showerror("File Error", "Issue creating file! (try changing directories)")

class EntryBox():
     
     def __init__(self, root, width, placeholder):
         self.root = root
         self.width = width
         self.placeholder = placeholder
         self.entry = ttk.Entry(self.root, width=self.width)
         self.entry.insert(0, self.placeholder)
         self.entry.bind("<FocusIn>", self.clear_placeholder)
         self.entry.bind("<FocusOut>", self.add_placeholder)

     
     def clear_placeholder(self, event):
         if self.entry.get() == self.placeholder:
             self.entry.delete(0,tk.END)

     def add_placeholder(self, event):
         if not self.entry.get():
             self.entry.insert(0, self.placeholder)

class GrpSubWin():

     def __init__(self, root, entry):
         
         self.root = root
         self.window = tk.Toplevel(self.root)
         self.window.geometry("720x100")
         self.window.resizable(False, False)
         self.window.title("Select Control Group")
         self.icon_path = get_resource_path("job_template_icon.ico")
         self.window.iconbitmap(self.icon_path)

         self.entry = entry

         self.list1 = ["None","R1", "R2", "R3", "S1", "S2", "S3"]
         self.list2 = ["None", "R2", "R3", "S1", "S2", "S3"]         
         self.box1 = ttk.Combobox(self.window, values=self.list1, state='readonly')
         self.box1.set("Group 1")
         self.box1.pack(side='left', padx=5,pady=5)
         self.checkbox_var1 = tk.BooleanVar(value=False)
         self.checkbox1 = tk.Checkbutton(self.window, text="Add Base", variable=self.checkbox_var1)
         self.checkbox1.pack(side='left', padx=2, pady=2)
         self.add_label = tk.Label(self.window, text="+")
         self.add_label.pack(side='left', padx=3, pady=3)
         
         self.box2 = ttk.Combobox(self.window, values=self.list2, state='readonly')
         self.box2.set("Group 2")
         self.box2.pack(side='left',padx=5,pady=5)
         self.checkbox_var2 = tk.BooleanVar()
         self.checkbox2 = tk.Checkbutton(self.window, text="Add Base", variable=self.checkbox_var2)
         self.checkbox2.pack(side='left', padx=2, pady=2)
         self.colon_label = tk.Label(self.window, text=":")
         self.colon_label.pack(side='left', padx=3, pady=3)

         self.box3 = ttk.Combobox(self.window, values=self.list1, state='readonly')
         self.box3.set("Master")
         self.box3.pack(side='left', padx=10,pady=10)

         self.submit_btn = tk.Button(self.window, text="Submit", fg='white',bg='#0056b9', command=self.submit)
         self.submit_btn.pack(side='left', padx=1,pady=1)
         self.result = [] 
         self.result2 = [] 

     def display_group(self, result):
         self.entry.config(state="normal") 
         self.entry.delete(0, tk.END)
         self.entry.insert(0, f"{result}")
         self.entry.config(state="readonly")


     def submit(self):
         
         box1_value = self.box1.get()
         if self.checkbox_var1.get() == True:
             box1_value = box1_value + "B1"
         
         box2_value = self.box2.get()
         if self.checkbox_var2.get() == True:
             box2_value = box2_value + "B2"         
         
         box3_value = self.box3.get()
         
         if box1_value == "Group 1" or box1_value == "None" and box2_value == "None" and box3_value == "None":
             display_result = "Non Group"
             self.display_group(display_result)
         elif box1_value != "Group 1" and box2_value == "Group 2":
             display_result = box1_value
             self.display_group(display_result)
         elif box1_value != "Group 1" and box2_value != "Group 2" and box3_value == "Master":
             display_result = f"{box1_value} + {box2_value}"
             self.display_group(display_result)
         elif box1_value != "Group 1" and box2_value != "Group 2" and box3_value != "Master":
             display_result = f"{box1_value} + {box2_value} : {box3_value}"
             self.display_group(display_result)
         
         self.window.destroy()

class LvarSubWin():
    
     def __init__(self, root, entry, save_entry):
         
         self.root = root
         self.entry = entry
         self.window = tk.Toplevel(self.root)
         self.window.geometry("250x300")
         self.window.resizable(False, False)
         self.window.title("Add Local Variables")
         self.icon_path = get_resource_path("job_template_icon.ico")
         self.window.iconbitmap(self.icon_path)

         self.save_entry = save_entry
         
         self.lb_var_frame = tk.Frame(self.window)
         self.lb_var_frame.pack(fill ='none', expand= False)
         self.lb_var_label = tk.Label(self.lb_var_frame, text="LB:")
         self.lb_var_label.pack(side='left', padx=5, pady=5)
         self.lb_var_entry = tk.Entry(self.lb_var_frame, width=10)
         self.lb_var_entry.pack(side='left', padx=5,pady=5)
         self.lb_range_label = tk.Label(self.lb_var_frame, text=" 0-255" )
         self.lb_range_label.pack(side='right')

         self.li_var_frame = tk.Frame(self.window)
         self.li_var_frame.pack(fill ='none', expand= False)
         self.li_var_label = tk.Label(self.li_var_frame, text="LI: ")
         self.li_var_label.pack(side='left', padx=5, pady=5)
         self.li_var_entry = tk.Entry(self.li_var_frame, width=10)
         self.li_var_entry.pack(side='left', padx=5,pady=5)
         self.li_range_label = tk.Label(self.li_var_frame, text=" 0-255" )
         self.li_range_label.pack(side='right')
            
         self.ld_var_frame = tk.Frame(self.window)
         self.ld_var_frame.pack(fill ='none', expand= False)
         self.ld_var_label = tk.Label(self.ld_var_frame, text="LD:")
         self.ld_var_label.pack(side='left', padx=5, pady=5)
         self.ld_var_entry = tk.Entry(self.ld_var_frame, width=10)
         self.ld_var_entry.pack(side='left', padx=5,pady=5)
         self.ld_range_label = tk.Label(self.ld_var_frame, text=" 0-255" )
         self.ld_range_label.pack(side='right')

         self.lr_var_frame = tk.Frame(self.window)
         self.lr_var_frame.pack(fill ='none', expand= False)
         self.lr_var_label = tk.Label(self.lr_var_frame, text="LR:")
         self.lr_var_label.pack(side='left', padx=5, pady=5)
         self.lr_var_entry = tk.Entry(self.lr_var_frame, width=10)
         self.lr_var_entry.pack(side='left', padx=5,pady=5)
         self.lr_range_label = tk.Label(self.lr_var_frame, text=" 0-255" )
         self.lr_range_label.pack(side='right')

         self.ls_var_frame = tk.Frame(self.window)
         self.ls_var_frame.pack(fill ='none', expand= False)
         self.ls_var_label = tk.Label(self.ls_var_frame, text="LS: ")
         self.ls_var_label.pack(side='left', padx=5, pady=5)
         self.ls_var_entry = tk.Entry(self.ls_var_frame, width=10)
         self.ls_var_entry.pack(side='left', padx=5,pady=5)
         self.ls_range_label = tk.Label(self.ls_var_frame, text=" 0-255" )
         self.ls_range_label.pack(side='right')

         self.lp_var_frame = tk.Frame(self.window)
         self.lp_var_frame.pack(fill ='none', expand= False)
         self.lp_var_label = tk.Label(self.lp_var_frame, text="LP: ")
         self.lp_var_label.pack(side='left', padx=5, pady=5)
         self.lp_var_entry = tk.Entry(self.lp_var_frame, width=10)
         self.lp_var_entry.pack(side='left', padx=5,pady=5)
         self.lp_range_label = tk.Label(self.lp_var_frame, text=" 0-255" )
         self.lp_range_label.pack(side='right')

         self.lbp_var_frame = tk.Frame(self.window)
         self.lbp_var_frame.pack(fill ='none', expand= False)
         self.lbp_var_label = tk.Label(self.lbp_var_frame, text="LBP:")
         self.lbp_var_label.pack(side='left', padx=5, pady=5)
         self.lbp_var_entry = tk.Entry(self.lbp_var_frame, width=10)
         self.lbp_var_entry.pack(side='left', padx=5,pady=5)
         self.lbp_range_label = tk.Label(self.lbp_var_frame, text=" 0-255" )
         self.lbp_range_label.pack(side='right')

         self.lex_var_frame = tk.Frame(self.window)
         self.lex_var_frame.pack(fill ='none', expand= False)
         self.lex_var_label = tk.Label(self.lex_var_frame, text="LEX:")
         self.lex_var_label.pack(side='left', padx=5, pady=5)
         self.lex_var_entry = tk.Entry(self.lex_var_frame, width=10)
         self.lex_var_entry.pack(side='left', padx=5,pady=5)
         self.lex_range_label = tk.Label(self.lex_var_frame, text=" 0-255" )
         self.lex_range_label.pack(side='right')

         self.submit_btn = tk.Button(self.window, text="Submit", fg='white',bg='#0056b9', command=self.submit)
         self.submit_btn.pack(padx=10, pady=10)

     def display_lvar(self, result):
         self.entry.config(state="normal") 
         self.entry.delete(0, tk.END)
         self.entry.insert(0, f"{result}")
         self.entry.config(state="readonly")

     def submit(self):
         lb_set = self.lb_var_entry.get()
         li_set = self.li_var_entry.get()
         ld_set = self.ld_var_entry.get()
         lr_set = self.lr_var_entry.get()
         ls_set = self.ls_var_entry.get()
         lp_set = self.lp_var_entry.get()
         lbp_set = self.lbp_var_entry.get()
         lex_set = self.lex_var_entry.get()
         
         lvar_list = [lb_set, li_set, ld_set, lr_set, ls_set, lp_set, lbp_set, lex_set]
        
         for index, lvar in enumerate(lvar_list):
             if lvar == "":
                 lvar_list[index] = "0"
         
         print(lvar_list)
         results = []
         
         check_total = 0

         for lvar in lvar_list:
             lvar = int(lvar)
             check_total = check_total + lvar

         for lvar in lvar_list:
             try:
                 lvar = int(lvar)
                 if lvar < 0 or lvar > 255:
                     lvar = 0
                     results.append(lvar)
                 else:
                     results.append(lvar)

             except:
                 lvar = 0
                 results.append(lvar)

         if check_total > 0:
             self.save_entry.delete(0, tk.END)
             self.save_entry.insert(0, results)
         else:
             self.save_entry.delete(0, tk.END)
             self.save_entry.insert(0, 'None')
             
         
         result_string = f"LB:{results[0]}, LI:{results[1]}, LD:{results[2]}, LR:{results[3]}, LS:{results[4]}, LP:{results[5]}, LBP:{results[6]}, LEX:{results[7]}"
         
         self.display_lvar(result_string)
         self.window.destroy()

class ArgSubWin():
     def __init__(self, root, arg_set, arg_type, tag_disp, tag_init):
         self.root = root
         self.window = tk.Toplevel(self.root)
         self.window.geometry("600x525")
         self.window.title("Set Arguments")
         self.icon_path = get_resource_path("job_template_icon.ico")
         self.window.iconbitmap(self.icon_path)
         self.window.resizable(False, False)

         self.arg_set = arg_set
         self.arg_type = arg_type
         self.arg_names = [None]
         self.arg_unit = [None]
         self.tag_disp = tag_disp
         self.tag_init = tag_init

         self.arg1 = ArgSelect(self.window, 1)
         self.arg2 = ArgSelect(self.window, 2)
         self.arg3 = ArgSelect(self.window, 3)
         self.arg4 = ArgSelect(self.window, 4)
         
         self.arg5 = ArgSelect(self.window, 5)
         self.arg6 = ArgSelect(self.window, 6)     
         self.arg7 = ArgSelect(self.window, 7)
         self.arg8 = ArgSelect(self.window, 8)
         
         self.arg9 = ArgSelect(self.window, 9)
         self.arg10 = ArgSelect(self.window, 10)
         self.arg11 = ArgSelect(self.window, 11)
         self.arg12 = ArgSelect(self.window, 12) 

         self.arg13 = ArgSelect(self.window, 13)
         self.arg14 = ArgSelect(self.window, 14)
         self.arg15 = ArgSelect(self.window, 15)   
         self.arg16 = ArgSelect(self.window, 16)
         
         self.submit_frame = tk.Frame(self.window)
         self.submit_btn = tk.Button(self.submit_frame, text='Submit', background='green', foreground='white', command=self.submit)
         self.submit_frame.pack(padx=3, pady=3)
         self.submit_btn.pack(padx=10, pady=10)

     def display(self, result, entry):
         entry.config(state="normal") 
         entry.delete(0, tk.END)
         entry.insert(0, f"{result}")
         entry.config(state="readonly")
     
     def submit(self):
         
         self.arg_info = []
         self.arg_add_info = []
         self.arg_type_info = []
         self.arg_name_info = []
         self.arg_unit_info = []

         self.arg_list = [self.arg1, self.arg2, self.arg3, self.arg4, self.arg5, self.arg6, self.arg7, 
                          self.arg8, self.arg9, self.arg10, self.arg11, self.arg12, self.arg13, self.arg14, 
                          self.arg15, self.arg16]
         
         # Arg Set
         self.argset_list = []
         for arg in self.arg_list:
             used = arg.arg_checkvar.get()
             if used == True:
                 self.argset_list.append("1")
                 self.arg_add_info.append(f"IARG#{arg.arg}")
             else:
                 self.argset_list.append("0")

         self.argset_result = ",".join(self.argset_list)         
         self.display(self.argset_result, self.arg_set)

         # Arg Type
         self.arg_type_handler = {
             
             "BYTE"       : "B",
             "INTEGER"    : "I",
             "DOUBLE"     : "D",
             "REAL"       : "R",
             "STRING"     : "S",
             "RB POS"     : "C",
             "BS POS"     : "BC",
             "RB VAR/POS" : "P",
             "BS VAR/POS" : "BP",
             "ST POS"     : "EC",
             "ST VAR/POS" : "EX", 
         }
         
         type_result = []
         for index, args in enumerate(self.argset_list):
             if args == "1":
                 current_type = self.arg_list[index].argtype.get()
                 self.arg_type_info.append(current_type)
                 
                 if current_type == "Type":
                     print(current_type)
                     messagebox.showerror("Argument Error",f"Error: Argument {index + 1} used but has no type")
                     return
                 else:
                     current_type = self.arg_type_handler.get(current_type)
                     type_result.append(current_type)
             elif args == "0" or args == None:
                 type_result.append("")
             else:
                 type_result.append("")
         
         raw_type_result = ",".join(type_result)
         self.display(raw_type_result, self.arg_type)

         self.arg_names = ["","","","","","","","","","","","","","","",""]
         
         for index, args in enumerate(self.arg_list):
             name = args.arg_name.entry.get()
             self.arg_name_info.append(name)

             name_regex = r"^.{0,16}$"
             arg_adress = args.arg
             check = args.arg_checkvar.get()
             
             if re.fullmatch(name_regex, name) == None:
                 messagebox.showwarning("Argument Error", f"ERROR: Argument {arg_adress} name must be between 1-16 characters")
                 return

             if name == "Name":
                 continue
             elif name != "Name":
                 if check == False:
                     messagebox.showerror("Argument Error", f"ERROR: Argument {arg_adress} given name but not used")
                     return
                 else:
                     self.arg_names[index] = name

         name_empty_count = 0
         for name in self.arg_names:
             if name == "":
                 name_empty_count += 1
         
         if name_empty_count == 16:
             self.arg_names = [None]
         else:
             self.arg_names.reverse()
             name_stop_index = None
             for index, name in enumerate(self.arg_names):
                 print(name, index)
                 if name != "":
                     name_stop_index = index
                     break
             
             name_result = self.arg_names[name_stop_index::]
             print(f"normal: {name_result}")
             name_result.reverse()
             print(f"reversed: {name_result}")
             self.arg_names.clear()
             for name in name_result:
                 self.arg_names.append(name)

         # Arg Unit
         self.arg_unit = ["","","","","","","","","","","","","","","",""]
         
         for index, args in enumerate(self.arg_list):
             unit = args.arg_unit.entry.get()
             self.arg_unit_info.append(unit)

             print(f"current unit{unit}")
             unit_regex = r"^.{0,8}$"
             arg_adress = args.arg
             check = args.arg_checkvar.get()
             
             if re.fullmatch(unit_regex, unit) == None:
                 messagebox.showwarning("Argument Error", f"ERROR: Argument {arg_adress} unit must be between 1-8 characters")
                 return

             if unit == "Unit":
                 continue
             elif unit != "Unit":
                 if check == False:
                     messagebox.showerror("Argument Error", f"ERROR: Argument {arg_adress} given unit but not used")
                     return
                 else:
                     self.arg_unit[index] = unit

         unit_empty_count = 0
         for unit in self.arg_unit:
             if unit == "":
                 unit_empty_count += 1
         
         if unit_empty_count == 16:
             self.arg_unit = [None]
         else:
             self.arg_unit.reverse()
             unit_stop_index = None
             for index, unit in enumerate(self.arg_unit):
                 print(unit, index)
                 if unit != "":
                     unit_stop_index = index
                     break
             
             unit_result = self.arg_unit[unit_stop_index::]
             unit_result.reverse()
             print(f"unit result {unit_result}")
             self.arg_unit.clear()
             for unit in unit_result:
                 self.arg_unit.append(unit)
         
         # Tag Display
         self.tagdisp_list = []
         for arg in self.arg_list:
             used = arg.arg_tag_display.get()
             if used == "ON":
                 self.tagdisp_list.append("1")
             else:
                 self.tagdisp_list.append("0")

         print(self.tagdisp_list)

         self.tag_disp_result = ",".join(self.tagdisp_list)
         self.display(self.tag_disp_result, self.tag_disp)

         # Tag Comment 
         self.tag_comms = ["","","","","","","","","","","","","","","",""]
         
         for index, args in enumerate(self.arg_list):
             comm = args.arg_expresn.entry.get()

             comm_regex = r"^.{0,8}$"
             arg_adress = args.arg
             check = args.arg_checkvar.get()
             
             if re.fullmatch(comm_regex, comm) == None:
                 messagebox.showwarning("Argument Error", f"ERROR: Argument {arg_adress} tag comment must be between 1-8 characters")
                 return

             if comm == "Expres'n":
                 continue
             elif comm != "Expres'n":
                 if check == False:
                     messagebox.showerror("Argument Error", f"ERROR: Argument {arg_adress} given tag_comment but not used")
                     return
                 else:
                     self.tag_comms[index] = comm

         comm_empty_count = 0
         for comm in self.tag_comms:
             if comm == "":
                 comm_empty_count += 1
         
         if comm_empty_count == 16:
             self.tag_comms = [None]
         else:
             self.tag_comms.reverse()
             comm_stop_index = None
             for index, comm in enumerate(self.tag_comms):
                 print(comm, index)
                 if comm != "":
                     comm_stop_index = index
                     break
             
             comm_result = self.tag_comms[comm_stop_index::]
             print(f"normal: {comm_result}")
             comm_result.reverse()
             print(f"reversed: {comm_result}")
             self.tag_comms.clear()
             for comm in comm_result:
                 self.tag_comms.append(comm)

         # Compile argument info for job comments
         loop_count = len(self.arg_add_info)
         print("start")
         for i in range(loop_count):
             self.arg_info.append(f"{self.arg_add_info[i]} ({self.arg_type_info[i]}) = {self.arg_name_info[i]}")
         print(f"end {self.arg_info}")
         
         # End
         self.window.destroy()

class ArgSelect():
    def __init__(self, root, arg):
         self.root = root
         self.arg = arg
         
         self.argtype_list = ["BYTE", "INTEGER", "DOUBLE", "REAL", "STRING",
                                 "RB POS", "RB VAR/POS", "BS POS", "BS VAR/POS", 
                                 "ST POS", "ST VAR/POS"]
         self.onoff_list = ["ON", "OFF"]
         
         self.arg_frame = tk.Frame(self.root)
         self.arg_frame.pack(padx=1, pady=1)
         self.arg_checkvar = tk.BooleanVar()
         self.arg_check = tk.Checkbutton(self.arg_frame, variable=self.arg_checkvar)
         self.arg_check.pack(padx=1, pady=1, side='left')
         if self.arg < 10:
             self.arg_title = tk.Label(self.arg_frame, text=f"Arg   {self.arg}:")
         else:
             self.arg_title = tk.Label(self.arg_frame, text=f"Arg {self.arg}:") 
         self.arg_title.pack(padx=1, pady=1, side='left')
         self.arg_name = EntryBox(self.arg_frame, 10, "Name")
         self.arg_name.entry.pack(padx=3, pady=3, side='left')
         self.argtype = ttk.Combobox(self.arg_frame, values=self.argtype_list, state='readonly')
         self.argtype.set("Type")
         self.argtype.pack(padx=1, pady=1, side='left')
         self.arg_unit = EntryBox(self.arg_frame, 8, "Unit")
         self.arg_unit.entry.pack(padx=3, pady=3, side='left')
         self.arg_tag_display = ttk.Combobox(self.arg_frame, values=self.onoff_list, state='readonly')
         self.arg_tag_display.set("Display")
         self.arg_tag_display.pack(padx=3, pady=3, side='left')
         self.arg_expresn = EntryBox(self.arg_frame, 8, "Expres'n")
         self.arg_expresn.entry.pack(padx=3, pady=3, side='left')

def main():
     startwindow = StartWindow()
     startwindow.root.mainloop()

if __name__ == "__main__":
     main()