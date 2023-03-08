import tkinter as tk
from tkinter.filedialog import *
from tkinter import ttk, font
import os, configparser
from threading import Thread, Event
from CreateFormattedCsv import *
from TelegramHandler import TelegramHandler
from SimDataHandler import SimDataHandler
import zipfile

class SimulatorUI:
    def __init__(self):
        self.window = tk.Tk()
        self.client = None
        self.is_connected = False
        self.run_simulation = True
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
        self.window.title(f'Telegram Simulator')
        self.window.configure(bg = bg_color)
        self.window.geometry('550x650')
        self.window.resizable(False, False)

        try:
            self.window.wm_iconbitmap('sms-logo-transparent.ico')
            # p1 = tk.PhotoImage(file = 'sms-logo-transparent.png')
            # self.window.iconphoto(False, p1)
        except Exception:
            pass
        # file variables
        self.frame = tk.Frame(self.window)
        self.host_address_str = tk.StringVar()
        self.host_port_str = tk.StringVar()
        self.csv_path_str = tk.StringVar()
        self.csv_filename_str = tk.StringVar()
        self.xml_path_str = tk.StringVar()
        self.xml_filename_str = tk.StringVar()
        self.time_interval_str = tk.StringVar()
        self.is_host_address_set = False
        self.is_host_port_set = False
        
        # try loading config
        try:
            config = configparser.ConfigParser()
            config.read('config.INI')
            self.host_address_str.set(config['DEFAULT']['host'])
            self.host_port_str.set(config['DEFAULT']['port'])
            self.csv_path_str.set(config['DEFAULT']['csvpath'])
            self.csv_filename_str.set(os.path.basename(self.csv_path_str.get()))
            self.xml_path_str.set(config['DEFAULT']['xmlpath'])
            self.xml_filename_str.set(os.path.basename(self.xml_path_str.get()))
            self.time_interval_str.set(config['DEFAULT']['interval'])
        except Exception as ex:
            print(f"failed to load config. message:{ex}")
        
        row = 0
        column = 0
        self.host_address_label = tk.Label(self.window, text = "Host Address", font=label_font)
        self.host_address_label.grid(row = row, column = column, sticky = tk.E, padx=20, pady=20)
        self.host_address_label.config(bg= bg_color, fg= label_font_color)
        
        column += 1
        self.host_address_entry = ttk.Entry(self.window, textvariable=self.host_address_str, state='normal')
        self.host_address_entry.grid(row = row, column = column, sticky = tk.W, padx=5, pady=20)
        
        column += 1
        self.host_address_button = ttk.Button(self.window, text = "Set Host", command = self.set_host_address)
        self.host_address_button.grid(row = row, column = column)
        
        row += 1
        column = 0
        self.host_port_label = tk.Label(self.window, text = "Port", font=label_font)
        self.host_port_label.grid(row = row, column = column, sticky = tk.E, padx=20, pady=20)
        self.host_port_label.config(bg= bg_color, fg= label_font_color)
        
        column += 1  
        self.host_port_entry = ttk.Entry(self.window, textvariable=self.host_port_str, state='normal')
        self.host_port_entry.grid(row = row, column = column, sticky = tk.W, padx=5, pady=20)
        
        column += 1
        self.host_port_button = ttk.Button(self.window, text = "Set Port", command = self.set_host_port)
        self.host_port_button.grid(row = row, column = column)
        
        row += 1
        column = 0
        self.connect_status_label = tk.Label(self.window, text = "", font=label_font)
        self.connect_status_label.grid(row = row, column = column, sticky = tk.E, padx=20, pady=20)
        self.connect_status_label.config(bg= bg_color, fg= label_font_color)
        
        column += 1
        self.connect_button = ttk.Button(self.window, text = "Connect", command=self.connect)
        self.connect_button.grid(row = row, column = column, columnspan=2, sticky = tk.W, padx=20, pady=20)
        self.connect_button["state"] = "disabled"
        
        row += 1
        column = 0
        self.tel_config_label = tk.Label(self.window, text = "Telegram Config", font=label_font)
        self.tel_config_label.grid(row = row, column = column, sticky = tk.E, padx=20, pady=20)
        self.tel_config_label.config(bg= bg_color, fg= label_font_color)
        
        column += 1  
        self.tel_config_entry = ttk.Entry(self.window, textvariable=self.xml_filename_str, state='disabled')
        self.tel_config_entry.grid(row = row, column = column, sticky = tk.W, padx=5, pady=20)
        
        column += 1  
        self.tel_config_button = ttk.Button(self.window, text = "Tel Config", command=self.set_tel_config)
        self.tel_config_button.grid(row = row, column = column, padx=20, pady=20)

        row += 1
        column = 0
        self.sim_config_label = tk.Label(self.window, text = "Simu Config", font=label_font)
        self.sim_config_label.grid(row = row, column = column, sticky = tk.E, padx=20, pady=20)
        self.sim_config_label.config(bg= bg_color, fg= label_font_color)
        
        column += 1  
        self.sim_config_entry = ttk.Entry(self.window, textvariable=self.csv_filename_str, state='disabled')
        self.sim_config_entry.grid(row = row, column = column, sticky = tk.W, padx=5, pady=20)
        
        column += 1  
        self.sim_config_button = ttk.Button(self.window, text = "Sim Config", command=self.set_sim_config)
        self.sim_config_button.grid(row = row, column = column, padx=20, pady=20)
        
        row += 1
        column = 0
        self.time_interval_label = tk.Label(self.window, text = "Time Interval", font=label_font)
        self.time_interval_label.grid(row = row, column = column, sticky = tk.E, padx=20, pady=20)
        self.time_interval_label.config(bg= bg_color, fg= label_font_color)
        
        column += 1  
        self.time_interval_dropdown = ttk.Combobox(self.window, width = 10, textvariable = self.time_interval_str)
        self.time_interval_dropdown.grid(row = row, column = column, sticky = tk.W, padx=5, pady=20)
        self.time_interval_dropdown['values'] = ('0.5', '1.0', '1.5', '2.0', '5.0', '10.0', '20.0')
        
        row += 1
        column = 0
        self.save_last_config = ttk.Button(self.window, text = "Save Config", command=self.save_config)
        self.save_last_config.grid(row = row, column = column,sticky = tk.W, padx=20, pady=20)
        
        column += 1 
        self.start_sim_button = ttk.Button(self.window, text = "Start Simulation", command=self.start_simulation)
        self.start_sim_button.grid(row = row, column = column,sticky = tk.W, padx=20, pady=20)
        self.start_sim_button["state"] = "disabled"

        column += 1
        self.stop_sim_button = ttk.Button(self.window, text = "Stop Simulation", command=self.stop_simulation)
        self.stop_sim_button.grid(row = row, column = column, sticky = tk.W, padx=20, pady=20)
        self.stop_sim_button["state"] = "disabled"
        
        row += 1
        column = 0
        self.message_box = tk.Text(self.window, height=8, width=60, state='disabled')
        self.scroll = tk.Scrollbar(self.window)
        self.message_box.configure(yscrollcommand=self.scroll.set)
        self.message_box.grid(row = row, column = column, columnspan = 3, sticky = tk.W, padx=20, pady=20)
        
    def save_config(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = dict()
        config['DEFAULT']['host'] = self.host_address_str.get()
        config['DEFAULT']['port'] = self.host_port_str.get()
        config['DEFAULT']['csvpath'] = self.csv_path_str.get()
        config['DEFAULT']['xmlpath'] = self.xml_path_str.get()
        config['DEFAULT']['interval'] = self.time_interval_str.get()
        with open('config.INI', 'w') as configfile:
            config.write(configfile)
            
    def set_tel_config(self):
        filepath = askopenfilename(initialdir = "/",
                                    title = "Select a File",
                                    filetypes = [("XML files",
                                                    "*.xsbt.xml")])
        filename = os.path.basename(filepath)
        self.xml_path_str.set(filepath)
        self.xml_filename_str.set(filename)
        self.update_buttons()
        
    def set_sim_config(self):
        filepath = askopenfilename(initialdir = "/",
                                    title = "Select a File",
                                    filetypes = [("CSV files",
                                                    "*.csv")])
        filename = os.path.basename(filepath)
        self.csv_path_str.set(filepath)
        self.csv_filename_str.set(filename)
        self.update_buttons()
        
    def set_host_address(self):
        self.is_host_address_set = True
        if self.is_host_port_set:
            self.connect_button["state"] = "normal"
        self.reset()
        
    def set_host_port(self):
        self.is_host_port_set = True
        if self.is_host_address_set:
            self.connect_button["state"] = "normal"
        self.reset()
        
    def log_message(self, message):
        self.message_box.config(state=tk.NORMAL)
        self.message_box.insert(tk.END, message + '\n')
        line_number = int(self.message_box.index(tk.END).split('.')[0])
        if line_number >= 100:
            self.message_box.delete('1.0', '2.0')
        self.message_box.config(state=tk.DISABLED)
        self.message_box.see(tk.END)
        
    def connect(self):
        host_address = self.host_address_str.get()
        host_port = int(self.host_port_str.get())
        self.client = TelegramHandler(TCP_IP=host_address, TCP_PORT=host_port)
        status = self.client.start_client()
        if status==0:
            self.connect_status_label['text'] = 'Connected !'
            self.is_connected = True
        elif status==1:
            self.connect_status_label['text'] = 'Disconnected !'
        elif status==2:
            self.connect_status_label['text'] = 'Error !'
        self.update_buttons()
            
    def update_buttons(self):
        if self.is_connected and len(self.xml_path_str.get()) > 0 and len(self.csv_path_str.get()) > 0:
            self.start_sim_button["state"] = "normal"
            self.stop_sim_button["state"] = "normal"
    
    def reset(self):
        if self.client != None:
            self.client = None
            self.connect_status_label['text'] = 'Disconnected !'
            self.is_connected = False
        self.update_buttons()
            
    def start_simulation(self):
        self.start_sim_button["state"] = "disabled"
        self.simulation_thread = Thread(target=self.simulation, daemon=True)
        self.simulation_thread.start()
        
    def simulation(self):
        datahandler = SimDataHandler(self.xml_path_str.get(), self.csv_path_str.get())
        while self.run_simulation:
            strPayload, bytePayload, jsonPayload = datahandler.prepare_telegram_data()
            self.log_message(f'Sending telegram...Count: {datahandler.seq}')
            try:
                ret = self.client.send(bytePayload)
            except Exception as ex:
                self.log_message(f"Error in sending. message: {ex}")
            finally:
                datahandler.seq += 1
                time.sleep(float(self.time_interval_str.get()))
            filename = 'file_' + datetime.datetime.now().strftime("%m%d%Y%H%M%S") + '.json'
            archivename = 'teldump_' + datetime.datetime.now().strftime("%m%d%Y%H") + '.zip'
            with open(filename, 'w+') as jsonfile:
                jsonfile.write(json.dumps(jsonPayload, indent=4))
            with zipfile.ZipFile(archivename,'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                zipf.write(filename, os.path.basename(filename))
            os.remove(filename)
            if not ret == None:
                self.reset()
                self.connect()
                self.log_message(f"Reconnecting...")
                time.sleep(5)
    
    def stop_simulation(self):
        self.run_simulation = False
        self.simulation_thread.join()
        self.run_simulation = True
        if not self.simulation_thread.is_alive():
            self.start_sim_button["state"] = "normal"
        
    def Run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.Close)
        self.window.mainloop()
    
    def Close(self):
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.window.destroy()
            os.remove("temp.csv")
if __name__ == '__main__':
    ui = SimulatorUI()
    ui.Run()