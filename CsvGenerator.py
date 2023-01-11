import tkinter as tk
from tkinter.filedialog import *
from tkinter import ttk, font
import os
from CreateFormattedCsv import *

class CsvGenerator:
    def __init__(self):
        self.window = tk.Tk()
        #s = ttk.Style(self.window)
        # themes ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
        #s.theme_use('alt')

        # global settings
        bg_color = '#daf7a6'
        label_font_color = '#e56039'
        btn_color = '#39e546'
        bold_font = font.Font(size=12, weight='bold')
        label_font = font.Font(size=12)
        style = ttk.Style()
        style.theme_use('winnative')
        style.configure("BW.TLabel", background=bg_color)
        style.configure('TButton', font=('American typewriter', 14), background='#232323', foreground='red')
        self.window.title(f'Csv Generator')
        self.window.configure(bg = bg_color)
        self.window.geometry('520x160')
        self.window.resizable(False, False)
        
        try:
            self.window.wm_iconbitmap('sms-logo-transparent.ico')
            # p1 = tk.PhotoImage(file = 'sms-logo-transparent.png')
            # self.window.iconphoto(False, p1)
        except Exception:
            pass
        
        # file variables
        self.frame = tk.Frame(self.window)
        self.xml_path_str = tk.StringVar()
        self.xml_filename_str = tk.StringVar()
        self.csv_filename_str = tk.StringVar()
        
        row = 0
        column = 0
        self.xml_upload_label = tk.Label(self.window, text = "XML Upload", font=label_font)
        self.xml_upload_label.grid(row = row, column = column, sticky = tk.E, padx=20, pady=20)
        self.xml_upload_label.config(bg= bg_color, fg= label_font_color)
        
        column += 1  
        self.xml_upload_entry = ttk.Entry(self.window, textvariable=self.xml_filename_str, state='disabled')
        self.xml_upload_entry.grid(row = row, column = column, padx=5, pady=20)
        
        column += 1
        self.xml_upload_button = ttk.Button(self.window, text = "Set XML Path", command = self.browseXmlFiles)
        self.xml_upload_button.grid(row = row, column = column)
        
        row += 1
        column = 0
        self.generate_button = ttk.Button(self.window, text = "Generate", command=self.GenerateCsv)
        self.generate_button.grid(row = row, column = column, sticky = tk.W, pady=20, padx=20)
        self.generate_button["state"] = "disabled"
        
        column += 1
        self.download_button = ttk.Button(self.window, text = "Download", command=self.Downloadsv)
        self.download_button.grid(row = row, column = column, sticky = tk.W, padx=20)
        self.download_button["state"] = "disabled"
        
    def browseXmlFiles(self):
        filepath = askopenfilename(initialdir = "/",
                                            title = "Select a File",
                                            filetypes = [("XML files",
                                                            "*.xsbt.xml")])
        filename = os.path.basename(filepath)
        self.xml_path_str.set(filepath)
        self.xml_filename_str.set(filename)
        self.generate_button["state"] = "normal"
    
    def GenerateCsv(self):
        file_name = CreateCsv(self.xml_path_str.get())
        self.csv_filename_str.set(file_name + '.csv')
        self.download_button["state"] = "normal"

    def Downloadsv(self):
        with open(self.csv_filename_str.get(), mode='r') as source_file:
            content = source_file.read()
        file = asksaveasfile(mode='w', initialfile = self.csv_filename_str.get(), defaultextension='csv')
        if file is not None:
            file.write(content)
            file.close()
            
    def Run(self):
        self.window.mainloop()
    
if __name__ == '__main__':
    ui = CsvGenerator()
    ui.Run()
    