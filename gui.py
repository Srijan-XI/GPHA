import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from pathlib import Path
import sys

# Import GPHA components
from gpha.analyzer import HealthAnalyzer
from gpha.config import Config
from gpha.cli import format_text_report

class GPHAGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Project Health Analyzer (GPHA)")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="Input Settings", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Repository
        ttk.Label(input_frame, text="Repository (owner/repo):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.repo_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.repo_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Token
        ttk.Label(input_frame, text="GitHub Token (optional):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.token_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.token_var, width=40, show="*").grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Config File
        ttk.Label(input_frame, text="Config File (optional):").grid(row=2, column=0, sticky=tk.W, pady=2)
        config_frame = ttk.Frame(input_frame)
        config_frame.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        self.config_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.config_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(config_frame, text="Browse", command=self.browse_config).pack(side=tk.LEFT, padx=(5, 0))
        
        # Output File
        ttk.Label(input_frame, text="Output File (optional):").grid(row=3, column=0, sticky=tk.W, pady=2)
        output_frame = ttk.Frame(input_frame)
        output_frame.grid(row=3, column=1, sticky=tk.W, pady=2, padx=5)
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT, padx=(5, 0))
        
        # --- Options Section ---
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Format
        ttk.Label(options_frame, text="Format:").pack(side=tk.LEFT, padx=(0, 5))
        self.format_var = tk.StringVar(value="text")
        ttk.Radiobutton(options_frame, text="Text", variable=self.format_var, value="text").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(options_frame, text="JSON", variable=self.format_var, value="json").pack(side=tk.LEFT, padx=5)
        
        # Save Report Checkbox
        self.save_report_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Save detailed report to reports dir", variable=self.save_report_var).pack(side=tk.LEFT, padx=20)
        
        # Analyze Button
        self.analyze_btn = ttk.Button(options_frame, text="Analyze Repository", command=self.start_analysis)
        self.analyze_btn.pack(side=tk.RIGHT, padx=5)
        
        # --- Output Section ---
        output_label_frame = ttk.LabelFrame(main_frame, text="Analysis Output", padding="10")
        output_label_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(output_label_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Consolas", 10))
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
        
        # Progress Bar (indeterminate)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        # hidden initially
        
    def browse_config(self):
        filename = filedialog.askopenfilename(
            title="Select Configuration File",
            filetypes=(("YAML files", "*.yaml;*.yml"), ("All files", "*.*"))
        )
        if filename:
            self.config_var.set(filename)
            
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Select Output File",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.output_var.set(filename)
            
    def start_analysis(self):
        repo = self.repo_var.get().strip()
        if not repo or "/" not in repo:
            messagebox.showerror("Error", "Please enter a valid repository in 'owner/repo' format.")
            return
            
        # Disable button and show progress
        self.analyze_btn.config(state=tk.DISABLED)
        self.progress.pack(fill=tk.X, pady=(5, 0))
        self.progress.start()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Starting analysis for {repo}...\n\n")
        
        # Run in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self.run_analysis, args=(repo,))
        thread.daemon = True
        thread.start()
        
    def run_analysis(self, repo_str):
        try:
            owner, repo = repo_str.split("/", 1)
            
            config_path = self.config_var.get().strip() or None
            config = Config(config_path=config_path)
            
            token = self.token_var.get().strip()
            if token:
                config.config["github"]["token"] = token
                
            analyzer = HealthAnalyzer(config)
            
            report = analyzer.analyze_repository(owner, repo)
            
            format_type = self.format_var.get()
            if format_type == "json":
                output_str = json.dumps(report.to_dict(), indent=2)
            else:
                output_str = format_text_report(report)
                
            output_file = self.output_var.get().strip()
            if output_file:
                Path(output_file).write_text(output_str)
                output_str += f"\n\nReport saved to: {output_file}"
                
            if self.save_report_var.get():
                reports_dir = Path(config.get("output.reports_dir", "reports"))
                reports_dir.mkdir(exist_ok=True)
                
                filename = f"{owner}_{repo}_{report.analyzed_at.strftime('%Y%m%d_%H%M%S')}.json"
                report_path = reports_dir / filename
                
                report_path.write_text(json.dumps(report.to_dict(), indent=2))
                output_str += f"\nDetailed report saved to: {report_path}"
                
            # Update GUI
            self.root.after(0, self.analysis_complete, output_str, report.health_score.overall)
            
        except Exception as e:
            self.root.after(0, self.analysis_error, str(e))
            
    def analysis_complete(self, output_str, score):
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state=tk.NORMAL)
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, output_str)
        
        if score < 60:
            self.result_text.insert(tk.END, "\n\nWARNING: Project needs attention (score < 60).")
            
    def analysis_error(self, error_msg):
        self.progress.stop()
        self.progress.pack_forget()
        self.analyze_btn.config(state=tk.NORMAL)
        
        self.result_text.insert(tk.END, f"Error: {error_msg}")
        messagebox.showerror("Analysis Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = GPHAGUI(root)
    root.mainloop()
