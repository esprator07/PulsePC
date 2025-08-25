import customtkinter as ctk
import psutil
import platform
import socket
import threading
import time

from datetime import datetime
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
try:
    import win32api
    import win32file
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import subprocess
    import json
    SUBPROCESS_AVAILABLE = True
except ImportError:
    SUBPROCESS_AVAILABLE = False

class SystemInfoApp:
    def __init__(self):
        # Main window settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        

        self.root = ctk.CTk()
        self.root.title("System Information")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        try:
            self.root.iconbitmap("pcm.ico")   # aynı klasörde olmalı
        except Exception as e:
            print("Error:", e)

        # WMI connection
        if WMI_AVAILABLE:
            try:
                self.c = wmi.WMI()
            except:
                self.c = None
        else:
            self.c = None
        
        # Update control
        self.updating = False
        self.current_page = None
        self.update_widgets = {}  # Store widgets that need updating
        
        # Main frames
        self.create_main_layout()
        
        # Sidebar
        self.create_sidebar()
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Show summary by default
        self.show_summary()
        
        # Start update thread
        self.start_update_thread()
        
    def start_update_thread(self):
        """Start the background update thread"""
        def update_loop():
            while True:
                if self.updating and self.current_page in ['summary', 'cpu', 'ram', 'graphics']:
                    try:
                        self.root.after(0, self.update_dynamic_content)
                    except:
                        pass
                time.sleep(2)  # Update every 2 seconds
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def update_dynamic_content(self):
        """Update dynamic content based on current page"""
        try:
            if self.current_page == 'summary':
                self.update_summary_values()
            elif self.current_page == 'cpu':
                self.update_cpu_values()
            elif self.current_page == 'ram':
                self.update_ram_values()
            elif self.current_page == 'graphics':
                self.update_graphics_values()
        except:
            pass
    
    def update_summary_values(self):
        """Update summary page dynamic values"""
        if 'cpu_usage' in self.update_widgets:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.update_widgets['cpu_usage'].configure(text=f"CPU Usage: {cpu_percent:.1f}%")
        
        if 'ram_usage' in self.update_widgets:
            memory = psutil.virtual_memory()
            self.update_widgets['ram_usage'].configure(text=f"RAM Usage: {memory.percent:.1f}%")
        
        if 'available_ram' in self.update_widgets:
            memory = psutil.virtual_memory()
            self.update_widgets['available_ram'].configure(text=f"Available RAM: {memory.available / (1024**3):.1f} GB")
        
        if 'active_processes' in self.update_widgets:
            self.update_widgets['active_processes'].configure(text=f"Active Processes: {len(psutil.pids())}")
        
        if 'uptime' in self.update_widgets:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            self.update_widgets['uptime'].configure(text=f"System Uptime: {str(uptime).split('.')[0]}")
    
    def update_cpu_values(self):
        """Update CPU page dynamic values"""
        if 'cpu_progress' in self.update_widgets:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.update_widgets['cpu_progress'].set(cpu_percent / 100)
            self.update_widgets['cpu_label'].configure(text=f"Total: {cpu_percent:.1f}%")
        
        # Update CPU temperature if available
        if 'cpu_temp_frame' in self.update_widgets:
            try:
                temperatures = self.get_system_temperatures()
                temp_frame = self.update_widgets['cpu_temp_frame']
                
                # Clear existing temperature widgets
                for widget in temp_frame.winfo_children():
                    if hasattr(widget, 'temp_label'):
                        widget.destroy()
                
                # Add new temperature readings
                if temperatures:
                    for sensor_name, temp_value in temperatures.items():
                        temp_widget = ctk.CTkFrame(temp_frame)
                        temp_widget.pack(fill="x", padx=5, pady=2)
                        temp_widget.temp_label = True  # Mark as temperature widget
                        
                        ctk.CTkLabel(temp_widget, text=f"🌡️ {sensor_name}: {temp_value}", 
                                   anchor="w").pack(fill="x", padx=10, pady=5)
                else:
                    # Show "not available" message
                    temp_widget = ctk.CTkFrame(temp_frame)
                    temp_widget.pack(fill="x", padx=5, pady=2)
                    temp_widget.temp_label = True
                    
                    ctk.CTkLabel(temp_widget, text="🌡️ Temperature: Not available", 
                               anchor="w").pack(fill="x", padx=10, pady=5)
            except:
                pass
    
    def update_ram_values(self):
        """Update RAM page dynamic values"""
        memory = psutil.virtual_memory()
        
        if 'ram_progress' in self.update_widgets:
            self.update_widgets['ram_progress'].set(memory.percent / 100)
        
        if 'ram_usage_label' in self.update_widgets:
            used_gb = memory.used / (1024**3)
            total_gb = memory.total / (1024**3)
            self.update_widgets['ram_usage_label'].configure(
                text=f"Used: {used_gb:.1f} GB / {total_gb:.1f} GB ({memory.percent:.1f}%)")
    
    def update_graphics_values(self):
        """Update Graphics page dynamic values"""
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    if f'gpu_load_{i}' in self.update_widgets:
                        self.update_widgets[f'gpu_load_{i}'].configure(text=f"GPU Load: {gpu.load * 100:.1f}%")
                    if f'gpu_memory_{i}' in self.update_widgets:
                        self.update_widgets[f'gpu_memory_{i}'].configure(text=f"Memory Usage: {gpu.memoryUsed} MB / {gpu.memoryTotal} MB")
                    if f'gpu_temp_{i}' in self.update_widgets:
                        self.update_widgets[f'gpu_temp_{i}'].configure(text=f"Temperature: {gpu.temperature}°C")
            except:
                pass
        
    def create_main_layout(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.main_frame, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(self.sidebar, text="Pc Manager", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=(20, 30))
        
        # Sections
        self.buttons = {}
        sections = [
            ("📊", "Summary", self.show_summary),
            ("🖥️", "Operating System", self.show_os),
            ("⚙️", "CPU", self.show_cpu),
            ("💾", "RAM", self.show_ram),
            ("🔧", "Motherboard", self.show_motherboard),
            ("🎮", "Graphics", self.show_graphics),
            ("💿", "Storage", self.show_storage),
            ("💽", "Optical Drives", self.show_optical),
            ("🔊", "Audio", self.show_audio),
            ("🔌", "Peripherals", self.show_peripherals),
            ("🌐", "Network", self.show_network)
        ]
        
        for icon, text, command in sections:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon} {text}",
                command=command,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=12)
            )
            btn.pack(pady=5, padx=10, fill="x")
            self.buttons[text] = btn
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.update_widgets.clear()
    
    def show_summary(self):
        self.current_page = 'summary'
        self.updating = True
        self.clear_content()
        
        # Title
        title = ctk.CTkLabel(self.content_frame, text="📊 System Summary", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        # Main info frame
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # System information
        system_info = self.get_system_summary()
        
        # Left column
        left_frame = ctk.CTkFrame(info_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        ctk.CTkLabel(left_frame, text="💻 System Information", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        
        for key, value in system_info["system"].items():
            frame = ctk.CTkFrame(left_frame)
            frame.pack(fill="x", padx=10, pady=2)
            label = ctk.CTkLabel(frame, text=f"{key}: {value}", anchor="w")
            label.pack(fill="x", padx=10, pady=5)
            
            # Store dynamic labels for updates
            if key == "Available RAM":
                self.update_widgets['available_ram'] = label
        
        # Right column
        right_frame = ctk.CTkFrame(info_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        ctk.CTkLabel(right_frame, text="📈 Performance", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        
        for key, value in system_info["performance"].items():
            frame = ctk.CTkFrame(right_frame)
            frame.pack(fill="x", padx=10, pady=2)
            label = ctk.CTkLabel(frame, text=f"{key}: {value}", anchor="w")
            label.pack(fill="x", padx=10, pady=5)
            
            # Store dynamic labels for updates
            if key == "CPU Usage":
                self.update_widgets['cpu_usage'] = label
            elif key == "RAM Usage":
                self.update_widgets['ram_usage'] = label
            elif key == "Active Processes":
                self.update_widgets['active_processes'] = label
            elif key == "System Uptime":
                self.update_widgets['uptime'] = label
    
    def show_os(self):
        self.current_page = 'os'
        self.updating = False
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="🖥️ Operating System", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        os_info = self.get_os_info()
        
        # Scrollable frame
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for key, value in os_info.items():
            frame = ctk.CTkFrame(scrollable)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=key, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
            ctk.CTkLabel(frame, text=str(value), wraplength=800).pack(anchor="w", padx=10, pady=(0, 10))
    
    def show_cpu(self):
        self.current_page = 'cpu'
        self.updating = True
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="⚙️ Processor (CPU)", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        cpu_info = self.get_cpu_info()
        
        # Main frame
        main_frame = ctk.CTkFrame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - information
        left_frame = ctk.CTkScrollableFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        for key, value in cpu_info.items():
            if key != "usage_per_core":
                frame = ctk.CTkFrame(left_frame)
                frame.pack(fill="x", padx=5, pady=3)
                
                ctk.CTkLabel(frame, text=key, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 2))
                ctk.CTkLabel(frame, text=str(value)).pack(anchor="w", padx=10, pady=(0, 5))
        
        # Right side - CPU usage
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="y", padx=(5, 10), pady=10)
        
        ctk.CTkLabel(right_frame, text="💹 CPU Usage", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # CPU percentage
        cpu_percent = psutil.cpu_percent(interval=1)
        progress = ctk.CTkProgressBar(right_frame)
        progress.pack(padx=20, pady=10)
        progress.set(cpu_percent / 100)
        
        cpu_label = ctk.CTkLabel(right_frame, text=f"Total: {cpu_percent:.1f}%")
        cpu_label.pack()
        
        # Store for updates
        self.update_widgets['cpu_progress'] = progress
        self.update_widgets['cpu_label'] = cpu_label
        
        # Add temperature section
        temp_section = ctk.CTkFrame(right_frame)
        temp_section.pack(fill="x", padx=10, pady=(20, 10))
        
        ctk.CTkLabel(temp_section, text="🌡️ Temperatures", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5))
        
        # Temperature readings frame
        temp_frame = ctk.CTkFrame(temp_section)
        temp_frame.pack(fill="x", padx=10, pady=5)
        
        # Initial temperature reading
        temperatures = self.get_system_temperatures()
        if temperatures:
            for sensor_name, temp_value in temperatures.items():
                temp_widget = ctk.CTkFrame(temp_frame)
                temp_widget.pack(fill="x", padx=5, pady=2)
                temp_widget.temp_label = True  # Mark as temperature widget
                
                ctk.CTkLabel(temp_widget, text=f"🌡️ {sensor_name}: {temp_value}", 
                           anchor="w").pack(fill="x", padx=10, pady=5)
        else:
            temp_widget = ctk.CTkFrame(temp_frame)
            temp_widget.pack(fill="x", padx=5, pady=2)
            temp_widget.temp_label = True
            
            ctk.CTkLabel(temp_widget, text="🌡️ Temperature: Not available", 
                       anchor="w").pack(fill="x", padx=10, pady=5)
        
        # Store temperature frame for updates
        self.update_widgets['cpu_temp_frame'] = temp_frame
    
    def show_ram(self):
        self.current_page = 'ram'
        self.updating = True
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="💾 Memory (RAM)", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        ram_info = self.get_ram_info()
        
        main_frame = ctk.CTkFrame(self.content_frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top section - general info
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # RAM usage
        memory = psutil.virtual_memory()
        used_gb = memory.used / (1024**3)
        total_gb = memory.total / (1024**3)
        
        ctk.CTkLabel(top_frame, text="💾 Memory Usage", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        progress = ctk.CTkProgressBar(top_frame, width=400)
        progress.pack(pady=10)
        progress.set(memory.percent / 100)
        
        usage_label = ctk.CTkLabel(top_frame, 
                    text=f"Used: {used_gb:.1f} GB / {total_gb:.1f} GB ({memory.percent:.1f}%)")
        usage_label.pack(pady=5)
        
        # Store for updates
        self.update_widgets['ram_progress'] = progress
        self.update_widgets['ram_usage_label'] = usage_label
        
        # Bottom section - detailed info
        bottom_frame = ctk.CTkScrollableFrame(main_frame)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for key, value in ram_info.items():
            if not isinstance(value, dict):
                frame = ctk.CTkFrame(bottom_frame)
                frame.pack(fill="x", padx=5, pady=3)
                
                ctk.CTkLabel(frame, text=key, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 2))
                ctk.CTkLabel(frame, text=str(value)).pack(anchor="w", padx=10, pady=(0, 5))
            else:
                # Memory modules
                module_frame = ctk.CTkFrame(bottom_frame)
                module_frame.pack(fill="x", padx=5, pady=5)
                
                ctk.CTkLabel(module_frame, text=key, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
                
                for subkey, subvalue in value.items():
                    ctk.CTkLabel(module_frame, text=f"  {subkey}: {subvalue}").pack(anchor="w", padx=20, pady=2)
    
    def show_motherboard(self):
        self.current_page = 'motherboard'
        self.updating = False
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="🔧 Motherboard", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        mb_info = self.get_motherboard_info()
        
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for key, value in mb_info.items():
            frame = ctk.CTkFrame(scrollable)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=key, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
            ctk.CTkLabel(frame, text=str(value), wraplength=800).pack(anchor="w", padx=10, pady=(0, 10))
    
    def show_graphics(self):
        self.current_page = 'graphics'
        self.updating = True
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="🎮 Graphics Cards", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        gpu_info = self.get_graphics_info()
        
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, gpu in enumerate(gpu_info):
            gpu_frame = ctk.CTkFrame(scrollable)
            gpu_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(gpu_frame, text=f"🎮 Graphics Card {i+1}", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            
            for key, value in gpu.items():
                info_frame = ctk.CTkFrame(gpu_frame)
                info_frame.pack(fill="x", padx=10, pady=2)
                
                label = ctk.CTkLabel(info_frame, text=f"{key}: {value}", anchor="w")
                label.pack(fill="x", padx=10, pady=5)
                
                # Store dynamic labels for updates
                if key == "GPU Load":
                    self.update_widgets[f'gpu_load_{i}'] = label
                elif key == "Memory Usage":
                    self.update_widgets[f'gpu_memory_{i}'] = label
                elif key == "Temperature":
                    self.update_widgets[f'gpu_temp_{i}'] = label
    
    def show_storage(self):
        self.current_page = 'storage'
        self.updating = False
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="💿 Storage Devices", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        storage_info = self.get_storage_info()
        
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for disk in storage_info:
            disk_frame = ctk.CTkFrame(scrollable)
            disk_frame.pack(fill="x", padx=10, pady=10)
            
            disk_name = disk.get('Model', disk.get('Drive', 'Unknown Device'))
            ctk.CTkLabel(disk_frame, text=f"💿 {disk_name}", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            
            for key, value in disk.items():
                if not isinstance(value, dict):
                    info_frame = ctk.CTkFrame(disk_frame)
                    info_frame.pack(fill="x", padx=10, pady=2)
                    ctk.CTkLabel(info_frame, text=f"{key}: {value}", anchor="w").pack(fill="x", padx=10, pady=5)
                else:
                    # Partitions
                    partition_frame = ctk.CTkFrame(disk_frame)
                    partition_frame.pack(fill="x", padx=10, pady=5)
                    
                    ctk.CTkLabel(partition_frame, text=key, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(5, 2))
                    
                    for subkey, subvalue in value.items():
                        ctk.CTkLabel(partition_frame, text=f"  {subkey}: {subvalue}").pack(anchor="w", padx=20, pady=1)
    
    def show_optical(self):
        self.current_page = 'optical'
        self.updating = False
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="💽 Optical Drives", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        optical_info = self.get_optical_drives_info()
        
        if not optical_info:
            ctk.CTkLabel(self.content_frame, text="No optical drives found.", 
                        font=ctk.CTkFont(size=16)).pack(pady=50)
            return
        
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, drive in enumerate(optical_info):
            drive_frame = ctk.CTkFrame(scrollable)
            drive_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(drive_frame, text=f"💽 Optical Drive {i+1}", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            
            for key, value in drive.items():
                info_frame = ctk.CTkFrame(drive_frame)
                info_frame.pack(fill="x", padx=10, pady=2)
                
                ctk.CTkLabel(info_frame, text=f"{key}: {value}", anchor="w").pack(fill="x", padx=10, pady=5)
    
    def show_audio(self):
        self.current_page = 'audio'
        self.updating = False
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="🔊 Audio Devices", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        audio_info = self.get_audio_info()
        
        if not audio_info:
            ctk.CTkLabel(self.content_frame, text="No audio devices found.", 
                        font=ctk.CTkFont(size=16)).pack(pady=50)
            return
        
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, device in enumerate(audio_info):
            device_frame = ctk.CTkFrame(scrollable)
            device_frame.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(device_frame, text=f"🔊 Audio Device {i+1}", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            
            for key, value in device.items():
                info_frame = ctk.CTkFrame(device_frame)
                info_frame.pack(fill="x", padx=10, pady=2)
                
                ctk.CTkLabel(info_frame, text=f"{key}: {value}", anchor="w").pack(fill="x", padx=10, pady=5)
    
    def show_peripherals(self):
        self.current_page = 'peripherals'
        self.updating = False
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="🔌 Peripherals", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        peripheral_info = self.get_peripherals_info()
        
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for category, devices in peripheral_info.items():
            if devices:
                cat_frame = ctk.CTkFrame(scrollable)
                cat_frame.pack(fill="x", padx=10, pady=10)
                
                ctk.CTkLabel(cat_frame, text=category, 
                            font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
                
                for i, device in enumerate(devices):
                    device_frame = ctk.CTkFrame(cat_frame)
                    device_frame.pack(fill="x", padx=10, pady=5)
                    
                    for key, value in device.items():
                        ctk.CTkLabel(device_frame, text=f"{key}: {value}", anchor="w").pack(anchor="w", padx=10, pady=2)
    
    def show_network(self):
        self.current_page = 'network'
        self.updating = False
        self.clear_content()
        
        title = ctk.CTkLabel(self.content_frame, text="🌐 Network Adapters", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(0, 20))
        
        network_info = self.get_network_info()
        
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, adapter in enumerate(network_info):
            adapter_frame = ctk.CTkFrame(scrollable)
            adapter_frame.pack(fill="x", padx=10, pady=10)
            
            adapter_name = adapter.get('Name', f'Network Adapter {i+1}')
            ctk.CTkLabel(adapter_frame, text=f"🌐 {adapter_name}", 
                        font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
            
            for key, value in adapter.items():
                info_frame = ctk.CTkFrame(adapter_frame)
                info_frame.pack(fill="x", padx=10, pady=2)
                
                ctk.CTkLabel(info_frame, text=f"{key}: {value}", anchor="w").pack(fill="x", padx=10, pady=5)
    
    # Information gathering methods
    def get_system_summary(self):
        uname = platform.uname()
        memory = psutil.virtual_memory()
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        # Get proper Windows version
        os_name = self.get_windows_version()
        
        return {
            "system": {
                "Computer Name": uname.node,
                "Operating System": os_name,
                "Processor": uname.processor or "Unknown",
                "Total RAM": f"{memory.total / (1024**3):.1f} GB",
                "Available RAM": f"{memory.available / (1024**3):.1f} GB"
            },
            "performance": {
                "CPU Usage": f"{psutil.cpu_percent(interval=1):.1f}%",
                "RAM Usage": f"{memory.percent:.1f}%",
                "Disk Usage": f"{psutil.disk_usage('/').percent:.1f}%" if psutil.disk_usage('/') else "N/A",
                "Active Processes": len(psutil.pids()),
                "System Uptime": str(uptime).split('.')[0]
            }
        }
    
    def get_windows_version(self):
        """Get accurate Windows version including Windows 11 detection"""
        try:
            # Try to get version from WMI first
            if self.c and WMI_AVAILABLE:
                for os_data in self.c.Win32_OperatingSystem():
                    if os_data.Caption:
                        return os_data.Caption
            
            # Fallback to platform info with Windows 11 detection
            import sys
            if sys.platform == "win32":
                try:
                    # Check Windows 11 by build number
                    version_info = platform.version()
                    if "10.0.22000" in version_info or "10.0.22" in version_info:
                        return "Microsoft Windows 11"
                    elif "10.0" in version_info:
                        return "Microsoft Windows 10"
                    else:
                        return f"Microsoft Windows {platform.release()}"
                except:
                    return f"{platform.system()} {platform.release()}"
            else:
                return f"{platform.system()} {platform.release()}"
        except:
            return f"{platform.system()} {platform.release()}"
    
    def get_os_info(self):
        uname = platform.uname()
        
        os_info = {
            "Operating System": self.get_windows_version(),
            "Version": uname.version,
            "Architecture": uname.machine,
            "Computer Name": uname.node,
            "Processor": uname.processor or "Unknown"
        }
        
        if self.c and WMI_AVAILABLE:
            try:
                for os_data in self.c.Win32_OperatingSystem():
                    os_info.update({
                        "Operating System": os_data.Caption or os_info["Operating System"],
                        "Version": os_data.Version or os_info["Version"],
                        "Build Number": os_data.BuildNumber or "Unknown",
                        "Manufacturer": os_data.Manufacturer or "Unknown",
                        "Registered User": os_data.RegisteredUser or "Unknown",
                        "System Directory": os_data.SystemDirectory or "Unknown",
                        "Windows Directory": os_data.WindowsDirectory or "Unknown"
                    })
                    break
            except:
                pass
        
        return os_info
    
    def get_cpu_info(self):
        cpu_info = {
            "Processor": platform.processor() or "Unknown",
            "Physical Cores": psutil.cpu_count(logical=False),
            "Logical Cores": psutil.cpu_count(logical=True),
            "CPU Usage": f"{psutil.cpu_percent(interval=1):.1f}%"
        }
        
        # Add temperature information
        temperatures = self.get_system_temperatures()
        if temperatures:
            for sensor_name, temp_value in temperatures.items():
                cpu_info[f"Temperature - {sensor_name}"] = temp_value
        
        if self.c and WMI_AVAILABLE:
            try:
                for processor in self.c.Win32_Processor():
                    cpu_info.update({
                        "Processor Name": processor.Name or "Unknown",
                        "Manufacturer": processor.Manufacturer or "Unknown",
                        "Architecture": self.get_architecture_name(processor.Architecture) if processor.Architecture else "Unknown",
                        "Physical Cores": processor.NumberOfCores or cpu_info["Physical Cores"],
                        "Logical Cores": processor.NumberOfLogicalProcessors or cpu_info["Logical Cores"],
                        "Max Clock Speed": f"{processor.MaxClockSpeed} MHz" if processor.MaxClockSpeed else "Unknown",
                        "Current Clock Speed": f"{processor.CurrentClockSpeed} MHz" if processor.CurrentClockSpeed else "Unknown",
                        "L2 Cache Size": f"{processor.L2CacheSize} KB" if processor.L2CacheSize else "Unknown",
                        "L3 Cache Size": f"{processor.L3CacheSize} KB" if processor.L3CacheSize else "Unknown",
                        "Processor ID": processor.ProcessorId or "Unknown",
                        "Socket": processor.SocketDesignation or "Unknown",
                        "Voltage": f"{processor.CurrentVoltage / 10:.1f}V" if processor.CurrentVoltage else "Unknown"
                    })
                    break
            except:
                pass
        
        return cpu_info
    
    def get_cpu_temperature(self):
        """Get CPU temperature using multiple methods"""
        temperature_data = {}
        
        # Method 1: WMI Temperature sensors
        if self.c and WMI_AVAILABLE:
            try:
                # Try MSAcpi_ThermalZoneTemperature (most common)
                for temp in self.c.MSAcpi_ThermalZoneTemperature():
                    if temp.CurrentTemperature:
                        # Convert from Kelvin to Celsius
                        temp_celsius = (temp.CurrentTemperature / 10.0) - 273.15
                        if 0 < temp_celsius < 150:  # Sanity check
                            temperature_data[f"Thermal Zone {temp.InstanceName}"] = f"{temp_celsius:.1f}°C"
            except:
                pass
            
            # Try Win32_TemperatureProbe
            try:
                for temp in self.c.Win32_TemperatureProbe():
                    if temp.CurrentReading:
                        temp_celsius = (temp.CurrentReading / 10.0) - 273.15
                        if 0 < temp_celsius < 150:
                            temperature_data[f"Temperature Probe {temp.DeviceID}"] = f"{temp_celsius:.1f}°C"
            except:
                pass
        
        # Method 2: Try reading from system files (Linux-style, some Windows systems support this)
        try:
            import os
            if os.path.exists("/sys/class/hwmon"):
                for hwmon in os.listdir("/sys/class/hwmon"):
                    try:
                        temp_file = f"/sys/class/hwmon/{hwmon}/temp1_input"
                        if os.path.exists(temp_file):
                            with open(temp_file, 'r') as f:
                                temp = int(f.read().strip()) / 1000.0
                                temperature_data[f"CPU Core ({hwmon})"] = f"{temp:.1f}°C"
                    except:
                        continue
        except:
            pass
        
        # Method 3: Try using PowerShell to get temperature
        if SUBPROCESS_AVAILABLE and not temperature_data:
            try:
                # PowerShell command to get thermal information
                powershell_cmd = [
                    "powershell", "-Command",
                    "Get-WmiObject -Namespace 'root/wmi' -Class MSAcpi_ThermalZoneTemperature | Select-Object CurrentTemperature, InstanceName"
                ]
                result = subprocess.run(powershell_cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[2:]:  # Skip header lines
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 1:
                                try:
                                    temp_raw = float(parts[0])
                                    temp_celsius = (temp_raw / 10.0) - 273.15
                                    if 0 < temp_celsius < 150:
                                        temperature_data["CPU Temperature"] = f"{temp_celsius:.1f}°C"
                                        break
                                except:
                                    continue
            except:
                pass
        
        # Method 4: Try reading from registry (some systems store thermal info here)
        if WIN32_AVAILABLE and not temperature_data:
            try:
                import winreg
                # Check for thermal information in registry
                reg_paths = [
                    r"SYSTEM\CurrentControlSet\Services\Thermal",
                    r"SYSTEM\CurrentControlSet\Control\Power\Profile\Events"
                ]
                for reg_path in reg_paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                        # This is a simplified check - real implementation would be more complex
                        winreg.CloseKey(key)
                    except:
                        continue
            except:
                pass
        
        return temperature_data
    
    def get_system_temperatures(self):
        """Get all available temperature sensors"""
        all_temps = {}
        
        # Get CPU temperature
        cpu_temps = self.get_cpu_temperature()
        all_temps.update(cpu_temps)
        
        # Get GPU temperature (if available)
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    if gpu.temperature and gpu.temperature > 0:
                        all_temps[f"GPU {i+1} ({gpu.name[:20]}...)"] = f"{gpu.temperature}°C"
            except:
                pass
        
        # Get disk temperatures (some systems provide this)
        if self.c and WMI_AVAILABLE:
            try:
                for disk in self.c.Win32_DiskDrive():
                    # Some disks report temperature in their SMART data
                    # This is a placeholder - actual implementation would need SMART data parsing
                    pass
            except:
                pass
        
        return all_temps
        
    
    def get_ram_info(self):
        memory = psutil.virtual_memory()
        
        ram_info = {
            "Total RAM": f"{memory.total / (1024**3):.2f} GB",
            "Available": f"{memory.available / (1024**3):.2f} GB",
            "Used": f"{memory.used / (1024**3):.2f} GB",
            "Usage Percentage": f"{memory.percent:.1f}%",
            "Free": f"{memory.free / (1024**3):.2f} GB"
        }
        
        if self.c and WMI_AVAILABLE:
            try:
                for memory_device in self.c.Win32_PhysicalMemory():
                    location = memory_device.DeviceLocator or f"Module {len([k for k in ram_info.keys() if 'Module' in k]) + 1}"
                    ram_info[f"RAM Module - {location}"] = {
                        "Capacity": f"{int(memory_device.Capacity) / (1024**3):.0f} GB" if memory_device.Capacity else "Unknown",
                        "Speed": f"{memory_device.Speed} MHz" if memory_device.Speed else "Unknown",
                        "Manufacturer": memory_device.Manufacturer or "Unknown",
                        "Part Number": memory_device.PartNumber or "Unknown",
                        "Serial Number": memory_device.SerialNumber or "Unknown"
                    }
            except:
                pass
        
        return ram_info
    
    def get_motherboard_info(self):
        motherboard_info = {"Motherboard Info": "Information not available"}
        
        if self.c and WMI_AVAILABLE:
            try:
                for board in self.c.Win32_BaseBoard():
                    motherboard_info.update({
                        "Manufacturer": board.Manufacturer or "Unknown",
                        "Model": board.Product or "Unknown",
                        "Serial Number": board.SerialNumber or "Unknown",
                        "Version": board.Version or "Unknown"
                    })
                    break
                
                for bios in self.c.Win32_BIOS():
                    motherboard_info.update({
                        "BIOS Manufacturer": bios.Manufacturer or "Unknown",
                        "BIOS Version": bios.SMBIOSBIOSVersion or "Unknown",
                        "BIOS Date": bios.ReleaseDate or "Unknown"
                    })
                    break
            except:
                pass
        
        return motherboard_info
    
    def get_graphics_info(self):
        graphics_info = []
        
        if self.c and WMI_AVAILABLE:
            try:
                for gpu in self.c.Win32_VideoController():
                    if gpu.Name:
                        graphics_info.append({
                            "Name": gpu.Name,
                            "RAM": f"{gpu.AdapterRAM / (1024**3):.1f} GB" if gpu.AdapterRAM else "Unknown",
                            "Driver Version": gpu.DriverVersion or "Unknown",
                            "Resolution": f"{gpu.CurrentHorizontalResolution}x{gpu.CurrentVerticalResolution}" if gpu.CurrentHorizontalResolution else "Unknown",
                            "Color Depth": f"{gpu.CurrentBitsPerPixel} bit" if gpu.CurrentBitsPerPixel else "Unknown",
                            "Status": gpu.Status or "Unknown"
                        })
            except:
                pass
        
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    graphics_info.append({
                        "Name": gpu.name,
                        "GPU Load": f"{gpu.load * 100:.1f}%",
                        "Memory Usage": f"{gpu.memoryUsed} MB / {gpu.memoryTotal} MB",
                        "Temperature": f"{gpu.temperature}°C",
                        "Driver": gpu.driver
                    })
            except:
                pass
        
        if not graphics_info:
            graphics_info = [{"Graphics Card": "Information not available"}]
        
        return graphics_info
    
    def get_storage_info(self):
        storage_info = []
        
        if self.c and WMI_AVAILABLE:
            try:
                for disk in self.c.Win32_DiskDrive():
                    disk_info = {
                        "Model": disk.Model or "Unknown",
                        "Size": f"{int(disk.Size) / (1024**3):.1f} GB" if disk.Size else "Unknown",
                        "Interface": disk.InterfaceType or "Unknown",
                        "Serial Number": disk.SerialNumber.strip() if disk.SerialNumber else "Unknown",
                        "Status": disk.Status or "Unknown"
                    }
                    
                    # Get partitions for this disk
                    try:
                        partitions = psutil.disk_partitions()
                        for partition in partitions:
                            try:
                                usage = psutil.disk_usage(partition.mountpoint)
                                disk_info[f"Partition {partition.device}"] = {
                                    "File System": partition.fstype,
                                    "Total": f"{usage.total / (1024**3):.1f} GB",
                                    "Used": f"{usage.used / (1024**3):.1f} GB",
                                    "Free": f"{usage.free / (1024**3):.1f} GB",
                                    "Usage": f"{(usage.used / usage.total) * 100:.1f}%"
                                }
                            except (PermissionError, FileNotFoundError):
                                pass
                    except:
                        pass
                    
                    storage_info.append(disk_info)
            except:
                pass
        
        # Fallback method using psutil
        if not storage_info:
            try:
                partitions = psutil.disk_partitions()
                for partition in partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        storage_info.append({
                            "Drive": partition.device,
                            "File System": partition.fstype,
                            "Total": f"{usage.total / (1024**3):.1f} GB",
                            "Used": f"{usage.used / (1024**3):.1f} GB",
                            "Free": f"{usage.free / (1024**3):.1f} GB",
                            "Usage": f"{(usage.used / usage.total) * 100:.1f}%"
                        })
                    except (PermissionError, FileNotFoundError):
                        pass
            except:
                storage_info = [{"Storage": "Information not available"}]
        
        return storage_info
    
    def get_optical_drives_info(self):
        optical_info = []
        
        if self.c and WMI_AVAILABLE:
            try:
                for drive in self.c.Win32_CDROMDrive():
                    optical_info.append({
                        "Name": drive.Name or "Unknown",
                        "Drive Letter": drive.Drive or "Unknown",
                        "Manufacturer": drive.Manufacturer or "Unknown",
                        "Media Type": drive.MediaType or "Unknown",
                        "Status": drive.Status or "Unknown",
                        "Transfer Rate": f"{drive.TransferRate} KB/s" if drive.TransferRate else "Unknown"
                    })
            except:
                pass
        
        return optical_info
    
    def get_audio_info(self):
        audio_info = []
        
        if self.c and WMI_AVAILABLE:
            try:
                for device in self.c.Win32_SoundDevice():
                    if device.Name:
                        audio_info.append({
                            "Name": device.Name,
                            "Manufacturer": device.Manufacturer or "Unknown",
                            "Status": device.Status or "Unknown",
                            "Device ID": device.DeviceID or "Unknown"
                        })
            except:
                pass
        
        return audio_info
    
    def get_peripherals_info(self):
        peripheral_info = {
            "USB Devices": [],
            "Keyboards": [],
            "Mice": [],
            "Printers": [],
            "Other Devices": []
        }
        
        if self.c and WMI_AVAILABLE:
            try:
                # USB Devices
                for device in self.c.Win32_USBHub():
                    if device.Name:
                        peripheral_info["USB Devices"].append({
                            "Name": device.Name,
                            "Device ID": device.DeviceID or "Unknown",
                            "Status": device.Status or "Unknown"
                        })
                
                # Keyboards
                for keyboard in self.c.Win32_Keyboard():
                    if keyboard.Name:
                        peripheral_info["Keyboards"].append({
                            "Name": keyboard.Name,
                            "Device ID": keyboard.DeviceID or "Unknown",
                            "Status": keyboard.Status or "Unknown"
                        })
                
                # Mice
                for mouse in self.c.Win32_PointingDevice():
                    if mouse.Name:
                        peripheral_info["Mice"].append({
                            "Name": mouse.Name,
                            "Device ID": mouse.DeviceID or "Unknown",
                            "Status": mouse.Status or "Unknown",
                            "Number of Buttons": mouse.NumberOfButtons or "Unknown"
                        })
                
                # Printers
                for printer in self.c.Win32_Printer():
                    if printer.Name:
                        peripheral_info["Printers"].append({
                            "Name": printer.Name,
                            "Status": printer.PrinterStatus or "Unknown",
                            "Port": printer.PortName or "Unknown",
                            "Driver": printer.DriverName or "Unknown"
                        })
                
                # Other PnP Devices
                for device in self.c.Win32_PnPEntity():
                    if device.Name and not any(keyword in device.Name.lower() for keyword in ['usb', 'keyboard', 'mouse', 'printer', 'audio', 'video']):
                        if len(peripheral_info["Other Devices"]) < 10:  # Limit to prevent overflow
                            peripheral_info["Other Devices"].append({
                                "Name": device.Name,
                                "Device ID": device.DeviceID or "Unknown",
                                "Status": device.Status or "Unknown"
                            })
            except:
                pass
        
        return peripheral_info
    
    def get_network_info(self):
        network_info = []
        
        # Get network interfaces using psutil
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface_name, addresses in interfaces.items():
            interface_info = {
                "Name": interface_name,
                "Status": "Up" if stats.get(interface_name, {}).isup else "Down" if interface_name in stats else "Unknown"
            }
            
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    interface_info["IPv4 Address"] = addr.address
                    interface_info["Netmask"] = addr.netmask
                elif addr.family == socket.AF_INET6:
                    interface_info["IPv6 Address"] = addr.address
                elif addr.family == psutil.AF_LINK:
                    interface_info["MAC Address"] = addr.address
            
            if interface_name in stats:
                interface_info["Speed"] = f"{stats[interface_name].speed} Mbps" if stats[interface_name].speed > 0 else "Unknown"
                interface_info["MTU"] = stats[interface_name].mtu
            
            network_info.append(interface_info)
        
        # Enhanced info using WMI
        if self.c and WMI_AVAILABLE:
            try:
                wmi_adapters = {}
                for adapter in self.c.Win32_NetworkAdapter():
                    if adapter.NetConnectionID and adapter.MACAddress:
                        wmi_adapters[adapter.NetConnectionID] = {
                            "Manufacturer": adapter.Manufacturer or "Unknown",
                            "Product Name": adapter.ProductName or "Unknown",
                            "MAC Address": adapter.MACAddress,
                            "Adapter Type": adapter.AdapterType or "Unknown",
                            "Speed": f"{adapter.Speed / 1000000:.0f} Mbps" if adapter.Speed else "Unknown"
                        }
                
                # Merge WMI info with psutil info
                for interface in network_info:
                    interface_name = interface["Name"]
                    if interface_name in wmi_adapters:
                        interface.update(wmi_adapters[interface_name])
            except:
                pass
        
        return network_info

    def run(self):
        """Start the application"""
        self.root.mainloop()

# Example usage and main execution
if __name__ == "__main__":
    try:
        app = SystemInfoApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure you have the required dependencies installed:")
        print("pip install customtkinter psutil")
        print("Optional dependencies for enhanced features:")
        print("pip install wmi GPUtil pywin32")
        input("Press Enter to exit...")
