
import tkinter as tk


def say_hello():
    """Update the greeting when the button is clicked."""
    message_label.config(text="Hello! Have a wonderful day.")
    greet_button.config(text="Greeted!")


# Main window
window = tk.Tk()
window.title("Welcome App | Tkinter")
window.geometry("450x320")
window.configure(bg="#F4F7FC")
window.resizable(True, True)

# Main content
container = tk.Frame(window, bg="#F4F7FC")
container.pack(expand=True, fill="both", padx=35, pady=30)

# Heading
title_label = tk.Label(
    container,
    text="Welcome!",
    font=("Segoe UI", 24, "bold"),
    bg="#F4F7FC",
    fg="#1E3A8A"
)
title_label.pack(pady=(15, 10))

# Instruction
instruction_label = tk.Label(
    container,
    text="Press the button to receive a greeting.",
    font=("Segoe UI", 11),
    bg="#F4F7FC",
    fg="#475569"
)
instruction_label.pack(pady=5)

# Greeting message
message_label = tk.Label(
    container,
    font=("Segoe UI", 12),
    bg="#F4F7FC",
    fg="#2563EB"
)
message_label.pack(pady=20)

# Action button
greet_button = tk.Button(
    container,
    text="Say Hello",
    command=say_hello,
    font=("Segoe UI", 11, "bold"),
    bg="#2563EB",
    fg="white",
    activebackground="#1D4ED8",
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    padx=25,
    pady=10
)
greet_button.pack(pady=10)

# Start event loop
window.mainloop()
