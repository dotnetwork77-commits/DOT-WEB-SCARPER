import tkinter as tk
from tkinter import ttk
import injector
import detector

def launch():
    """Launch the floating toggle window."""
    # Create main window
    window = tk.Tk()
    window.title('WebSearch Toggle')
    window.geometry('300x200')
    window.attributes('-topmost', True)
    window.resizable(False, False)
    
    # Service detection
    service_info = detector.check_services()
    service_name = service_info['service'] or 'Not detected'
    
    # Mode selection
    mode_frame = ttk.LabelFrame(window, text='How are you using it?', padding=10)
    mode_frame.pack(fill='x', padx=10, pady=5)
    
    mode = tk.StringVar(value='proxy')
    
    ttk.Radiobutton(mode_frame, text='Open WebUI / Any LLM', 
                     variable=mode, value='proxy').pack(anchor='w')
    ttk.Radiobutton(mode_frame, text='LM Studio / Direct', 
                     variable=mode, value='clipboard').pack(anchor='w')
    
    # Toggle button
    toggle_frame = ttk.Frame(window)
    toggle_frame.pack(fill='x', padx=10, pady=10)
    
    toggle_button = ttk.Button(toggle_frame, text='Web Search: OFF', 
                              command=lambda: toggle_button_click())
    toggle_button.pack(fill='x', pady=5)
    
    # Status label
    status_label = ttk.Label(window, text=f'Service: {service_name}')
    status_label.pack(pady=5)
    
    # Update status periodically
    def update_status():
        service_info = detector.check_services()
        status_label.config(text=f'Service: {service_info["service"] or "Not detected"}')
        window.after(5000, update_status)
    
    update_status()
    
    def toggle_button_click():
        """Handle toggle button click."""
        current_state = 'ON' if 'ON' in toggle_button['text'] else 'OFF'
        new_state = 'OFF' if current_state == 'ON' else 'ON'
        
        toggle_button.config(text=f'Web Search: {new_state}')
        
        if new_state == 'ON':
            toggle_button.config(style='Green.TButton')
        else:
            toggle_button.config(style='TButton')
        
        injector.set_toggle(new_state == 'ON')
        
        # Start the appropriate mode
        if mode.get() == 'proxy':
            import threading
            threading.Thread(target=injector.start_proxy, 
                           args=(service_info['port'],), daemon=True).start()
        else:
            import threading
            threading.Thread(target=injector.clipboard_mode, daemon=True).start()
    
    # Style for toggle button
    style = ttk.Style()
    style.configure('Green.TButton', background='#4CAF50', foreground='white')
    
    # Start the mode based on initial selection
    if mode.get() == 'proxy':
        import threading
        threading.Thread(target=injector.start_proxy, 
                       args=(service_info['port'],), daemon=True).start()
    else:
        import threading
        threading.Thread(target=injector.clipboard_mode, daemon=True).start()
    
    # Run the window
    window.mainloop()

if __name__ == "__main__":
    launch()