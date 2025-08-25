# PulsePC
PulsePC is a privacy-focused system monitoring tool. It displays all your system info (CPU, RAM, storage, etc.) in a clean interface. The best part? No data is collected or shared. It runs entirely locally and securely.

# PulsePC - System Information Utility

<img width="1024" height="1024" alt="pcm" src="https://github.com/user-attachments/assets/f8881506-b8e4-4f89-8181-bf72cd74a793" />


PulsePC is a modern, clean system information and monitoring tool for Windows, built with Python and CustomTkinter. It provides a detailed overview of your computer's hardware and software components through a user-friendly and intuitive interface.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)](https://github.com/TomSchimansky/CustomTkinter)

## 📖 About The Project

This project was created to offer a straightforward way to access complex system data. Whether you are a tech enthusiast curious about your hardware, a developer needing quick system stats, or a user diagnosing an issue, PulsePC presents the information you need in a clear and organized manner.

The application leverages powerful Python libraries to fetch real-time data directly from your system's core.

## ✨ Features

PulsePC provides detailed information across various system categories:

*   🖥️ **System Summary:** A dashboard with a quick overview of your OS, CPU, RAM, and real-time performance metrics.
*   ⚙️ **Operating System:** Detailed information about your Windows installation, including version, build number, and architecture.
*   🧠 **Processor (CPU):** View processor model, core count, clock speed, and live usage and temperature data.
*   💾 **Memory (RAM):** See total, used, and available RAM, along with detailed specs for each installed memory module.
*   🎨 **Graphics (GPU):** Lists all detected graphics cards with details on drivers, memory, and real-time temperature and load (where available).
*   💽 **Storage:** A comprehensive look at your storage devices, including model, size, interface, and partition usage.
*   🔧 **Motherboard:** Displays manufacturer, model, serial number, and BIOS information.
*   🔌 **Peripherals & Devices:** Lists connected USB devices, keyboards, audio devices, and more.
*   🌐 **Network:** Shows all network adapters with their IP/MAC addresses, status, and speed.

## 📸 Screenshots

<img width="1192" height="826" alt="scpu" src="https://github.com/user-attachments/assets/a0a073ac-d44c-4728-bfec-8a741e99192d" />
<img width="1182" height="820" alt="sauido" src="https://github.com/user-attachments/assets/a1c0002d-ad44-4a40-a782-c35bc86a4064" />
<img width="1177" height="810" alt="summary" src="https://github.com/user-attachments/assets/59f41625-4e62-4097-89d5-88991faf11e2" />
<img width="1185" height="818" alt="storage" src="https://github.com/user-attachments/assets/24a3a157-e4de-43b4-80c6-a2bf2f3698bc" />
<img width="1183" height="815" alt="sram" src="https://github.com/user-attachments/assets/2a66b4d1-ba1f-4f59-bd9b-83deb6d6f2ab" />
<img width="1193" height="820" alt="speripherals" src="https://github.com/user-attachments/assets/3644f2f5-b016-421a-8aeb-3a8a4ddfa7da" />
<img width="1183" height="812" alt="sop" src="https://github.com/user-attachments/assets/089adf06-d086-43a7-a610-af38e75a1c98" />
<img width="1163" height="802" alt="snetwork" src="https://github.com/user-attachments/assets/cc391a34-b02a-45ad-927d-fdcefc247b51" />
<img width="1188" height="821" alt="smb" src="https://github.com/user-attachments/assets/2dd83dd5-0cfa-4503-94f1-a95a427a83aa" />
<img width="1187" height="812" alt="sgraphics" src="https://github.com/user-attachments/assets/3848d173-2178-467d-bc07-2eadd55e4bdb" />

## 🛠️ Tech Stack

*   **Language:** Python
*   **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
*   **System Data:**
    *   [psutil](https://github.com/giampaolo/psutil): For cross-platform system metrics (CPU, RAM, Disk, Network).
    *   [WMI](https://pypi.org/project/WMI/): For in-depth Windows-specific information (Motherboard, BIOS, Peripherals).
    *   [GPUtil](https://github.com/anderskm/gputil): For NVIDIA GPU statistics.
    *   [pywin32](https://pypi.org/project/pywin32/): For native Windows API access.

## 📝 License

This project is distributed under the Apache License 2.0. See the `LICENSE` file for more information.


Copyright 2025 Atakan Ekşi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
