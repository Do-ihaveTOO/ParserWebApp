
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os

# Initialize global process variables
processDESP = None
processOA = None
processPO = None
processBS = None
processAM = None

def start_process(command, name):
    process = subprocess.Popen(
        ["python", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output_text.insert(tk.END, f"{name} script started\n")
    threading.Thread(target=read_output, args=(process, name)).start()
    return process

def despatch():
    global processDESP
    processDESP = start_process("N:/REPORTING/Test folder/Parsing/Despatch and invoice/PDFs.py", "Despatch")

def OA():
    global processOA
    processOA = start_process("N:/REPORTING/Test folder/Parsing/Acknowledgement/PDFs.py", "OA")

def PO():
    global processPO
    processPO = start_process("N:/REPORTING/Test folder/Parsing/POs/PDFs.py", "PO")

def BS():
    global processBS
    processBS = start_process("N:/REPORTING/Test folder/Parsing/BS/AUTObsPARSE.py", "BS")

def AM():
    global processAM
    processAM = start_process("N:/REPORTING/Test folder/Parsing/AM/AUTOamPARSE.py", "AM")
    
def des_start():
    global startdes
    startdes = start_process("N:/REPORTING/Test folder/Parsing/Despatch and invoice/Startup.py", "Despatch Startup")
    
def ack_start():
    global startack
    startack = start_process("N:/REPORTING/Test folder/Parsing/Acknowledgement/Startup.py", "OA Startup")
    
def po_start():
    global startpo
    startpo = start_process("N:/REPORTING/Test folder/Parsing/POs/Startup.py", "PO Startup")
    
#def bs_start():
    #global startbs
    #startbs = start_process("N:/REPORTING/Test folder/Parsing/BS/Startup.py", "BS Startup")
    
#def am_start():
    #global startam
    #startam = start_process("N:/REPORTING/Test folder/Parsing/AM/Startup.py", "AM Startup")

def stop_script():
    global processDESP, processOA, processPO, processBS, processAM, startack, startdes, startpo
    for process in [processDESP, processOA, processPO, processBS, processAM, startack,  startdes, startpo]:
        if process:
            process.terminate()
            output_text.insert(tk.END, "Script stopped\n")
    app.quit()

def export_output():
    with open("output.txt", "w") as file:
        file.write(output_text.get("1.0", tk.END))
    os.system("start output.txt")

def read_output(process, name):
    for line in iter(process.stdout.readline, ''):
        output_text.insert(tk.END, f"{name}: {line}")
        output_text.see(tk.END)
    process.stdout.close()

def start_processing_scripts():
    threading.Thread(target=despatch).start()
    threading.Thread(target=OA).start()
    threading.Thread(target=PO).start()
    
def start_initial_scripts():
    threading.Thread(target=des_start).start()
    threading.Thread(target=ack_start).start()
    threading.Thread(target=po_start).start()
    #threading.Thread(target=bs_start).start()
    #threading.Thread(target=am_start).start()

# Create the main application window
app = tk.Tk()
app.title("Parser")

# Frame for the top row of buttons
button_frame = tk.LabelFrame(app, text="Continuous tasks")
button_frame.pack(pady=10, padx=10, fill="x")

inner_frame = tk.Frame(button_frame)
inner_frame.pack(anchor='center')

# Create buttons and add them to the frame
desp_button = tk.Button(inner_frame, text="Despatch", command=despatch)
desp_button.pack(side=tk.LEFT, padx=5)

oa_button = tk.Button(inner_frame, text="OA's", command=OA)
oa_button.pack(side=tk.LEFT, padx=5)

po_button = tk.Button(inner_frame, text="Our PO's", command=PO)
po_button.pack(side=tk.LEFT, padx=5)

button_frame1 = tk.LabelFrame(app, text="One time tasks")
button_frame1.pack(pady=10, padx=10, fill="x")

inner_frame1 = tk.Frame(button_frame1)
inner_frame1.pack(anchor='center')

bs_button = tk.Button(inner_frame1, text="British Steel Order Acknowledgements", command=BS)
bs_button.pack(side=tk.LEFT, padx=5)

am_button = tk.Button(inner_frame1, text="Arcelor Order Acknowledgements", command=AM)
am_button.pack(side=tk.LEFT, padx=5)

# Create a button to export the output
export_button = tk.Button(app, text="Export Output", command=export_output)
export_button.pack(pady=10)

# Create a button to quit the application
stop_button = tk.Button(app, text="Quit", command=stop_script)
stop_button.pack(pady=10)

# Create a text widget to display the output
output_text = scrolledtext.ScrolledText(app, width=50, height=10)
output_text.pack(expand=True, fill="both", padx=10, pady=10)

# Start initial scripts when the application starts
start_initial_scripts()

# Start the main event loop
app.mainloop()
