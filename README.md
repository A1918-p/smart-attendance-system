# 📝 Smart Attendance System

An AI-powered web application built with Python and Computer Vision that digitizes physical, handwritten attendance sheets. 

Instead of manually entering data, educators can upload a photograph of a signed attendance sheet alongside a master class roster. The system analyzes the signatures, digitally filters out red "Absent" markers, and automatically generates an accurate, downloadable Excel file.

## ✨ Key Features
* **No OCR Errors:** Uses a Spatial Mapping + Master List approach to guarantee 0% typos in student names and roll numbers.
* **Red Ink Filter:** Automatically detects and erases red pen marks (commonly used by teachers to mark absents) before calculating ink density.
* **Inner-Box Cropping:** Shaves off the edges of every grid box to completely ignore thick table lines and paper warping.
* **Interactive Visual Chart:** Plots the ink density of every student on a live bar chart, allowing the user to set a perfect, custom threshold for any lighting condition.

## 🛠️ Tech Stack
* **Python** (Core Logic)
* **Streamlit** (Web Interface & Interactive UI)
* **OpenCV / NumPy** (Image Processing, Color Masking, Binarization)
* **Pandas / OpenPyXL** (Data Handling & Excel Generation)

---

## 🚀 How to Run This Project Locally

If you want to run this software on your own machine, follow these steps:

### 1. Prerequisites
Make sure you have [Python](https://www.python.org/downloads/) (3.8+) and [Git](https://git-scm.com/downloads) installed on your computer.

### 2. Clone the Repository
Open your terminal or Command Prompt and run:
```bash
git clone [https://github.com/A1918-p/smart-attendance-system.git](https://github.com/A1918-p/smart-attendance-system.git)
cd smart-attendance-system
