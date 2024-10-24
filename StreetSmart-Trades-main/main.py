import tkinter as tk
import threading
import subprocess
import sys
import os
import time

class TradingBotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Window")
        self.master.geometry("600x400")

        self.welcome_label = tk.Label(master, text="Welcome to StreetSmart Trades: Trading Bot!", font=('TkDefaultFont', 14))
        self.welcome_label.pack(pady=10)

        # Create a Text widget to display output
        self.output_text = tk.Text(master, wrap=tk.WORD, height=15)
        self.output_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Buttons for the trading strategies
        self.range_button = tk.Button(master, text="Range Trading", command=self.open_range_window)
        self.range_button.pack(pady=10)

        self.trend_button = tk.Button(master, text="Trend Trading", command=self.open_trend_window)
        self.trend_button.pack(pady=10)

    def append_output(self, output):
        # Append output to the text widget and print to the terminal
        self.output_text.insert(tk.END, output + '\n')
        self.output_text.see(tk.END)  # Scroll to the end
        print(output)  # Print to terminal

    def open_range_window(self):
        threading.Thread(target=self.run_range_trading).start()

    def run_range_trading(self):
        self.append_output("Running range trading algorithm...")
        script_path = os.path.join(os.path.dirname(__file__), "rangetrade.py")
        
        # Start the trading script as a subprocess
        process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Continuously check for output
        while True:
            output = process.stdout.readline()  # Read output line by line
            if output == '' and process.poll() is not None:
                break  # Exit the loop if process has finished
            if output:  # If there's output, append it
                self.append_output(output.strip())

        # Wait for the process to complete and handle any remaining output
        return_code = process.wait()
        self.append_output("Range trading algorithm has completed with return code: {}".format(return_code))

    def open_trend_window(self):
        threading.Thread(target=self.run_trend_trading).start()

    def run_trend_trading(self):
        self.append_output("Running trend trading algorithm...")
        script_path = os.path.join(os.path.dirname(__file__), "trade.py")
        
        # Start the trading script as a subprocess
        process = subprocess.Popen([sys.executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Continuously check for output
        while True:
            output = process.stdout.readline()  # Read output line by line
            if output == '' and process.poll() is not None:
                break  # Exit the loop if process has finished
            if output:  # If there's output, append it
                self.append_output(output.strip())

        # Wait for the process to complete and handle any remaining output
        return_code = process.wait()
        self.append_output("Trend trading algorithm has completed with return code: {}".format(return_code))

# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotApp(root)
    root.mainloop()

