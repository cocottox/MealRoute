# MealRoute
**Read this in other languages** [Italian](README.it.md)

MealRoute is an open-source desktop application developed in Python and designed to support volunteers in planning and optimizing the logistics of home meal delivery. The software was created with the goal of reducing the kilometers traveled, eliminating overlaps between vehicles, and automating a process that is often managed manually, giving back valuable time to those who dedicate themselves to others.

## Key Functionality
* **Intiutive data managment**: A local file-based JSON database system to save contacts, delivery notes, and manage a dynamic whitelist to quickly select who to include in the day's route.
* **Local and lightweight Geocoding**: To avoid the costs of external APIs or the computational weight of complete OSM (.pbf) files, the system queries a local geospatial database (DataAddress.json) to instantly associate latitude and longitude with each street number.
* **Advanced Routing Algorithm**: Delivery points are evenly distributed among vehicles through a polar sorting calculated relative to the geographical center, avoiding vehicle intersections. Each sub-route is optimized sequentially using the Nearest Neighbor approach combined with a 2-Opt refinement engine rigidly anchored to the starting point. 
* **Graphical User Interface (GUI)**: Developed in Tkinter, it offers real-time street autocompletion, interactive tables (Treeview), and progress bars during processing.
* **Route Visualization**: Native integration of a Matplotlib canvas that graphically maps the generated rounds by color once the lists are created, allowing volunteers an immediate visual check without having to "trust the algorithm blindly".

## **COMPARISON**

---

| RealRoutes |  OptimizedRoutes  |
|:--------:|:--------:|
|![real data graph](<confronti/18-05-2026(non ottimizzato).png>)|![optimized by program](confronti/18-05-2026(ottimizzato).png)|
|![real data graph](<confronti/16-05-2026(non ottimizzato).png>)|![optimized by program](confronti/16-05-2026(ottimizzato).png)|
## Technical Stack
* **Language**: Python 3.x
* **User Interface**: Tkinter / TTK
* **Algorithms and logic**: Math (Polar Sorting, Nearest Neighbor, 2-Opt TSP)
* **Data Visualization**: Matplotlib
* **Data Storage**: JSON / Dataclasses

## Contributions and Philosophy
This software was developed not to replace the experience of volunteers, but to act as a decision support tool. If you want to contribute to optimizing routing algorithms, improving the UI, or adapting the local database to other municipalities, Pull Requests are welcome!
## How to Install and Run the Program
Follow these steps to set up the project locally on your machine.
### 1. Prerequisites
Make sure you have installed on your computer:
* **Python 3.8 or higher** ([Download Python here](https://www.python.org/downloads/))
* **Git** (optional, to clone the repository)
### 2. Guided Installation
Open your terminal (or Command Prompt) and run the following commands:
#### Step 1: Clone the repository (or download the ZIP file)
```bash
git clone [https://github.com/cocottox/MealRoute.git](https://github.com/cocottox/MealRoute.git)
cd MealRoute
```
#### Step 2: Create the virtual environment
* ##### On Windows
```bash
python -m venv venv
.\venv\Scripts\activate
```
* ##### On MacOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
#### Step 3: Install the necessary dependencies
```bash
pip install -r requirements.txt
```
##### Structure of the Required Files
To function correctly, the application needs two data files in the same folder as the .py files. Make sure they are present:
* *DataAddress.json* (The local database with all the addresses of the city)
* *addresses.json* (Your address book, it is created automatically on the first run if missing)
#### Step 4: Starting the Application
Once the installation is complete, you can start the application simply by running the main file:
```bash
python main.py
```
