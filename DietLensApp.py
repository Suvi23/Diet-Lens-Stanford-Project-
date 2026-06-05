# dietlens.py - COMPLETE VERSION with AI connected
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import threading  # Needed so UI doesn't freeze during AI call

# Import our AI function from ai_engine.py
from ai_engine import analyze_food_label

# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Diet-Lens App")
app.geometry("900x600")

# Global variable to store selected image path
selected_image_path = None

# ─────────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────────

def upload_image():
    """Called when Upload Label button is clicked"""
    global selected_image_path

    # Open file picker
    file_path = filedialog.askopenfilename(
        title="Select a Food Label Image",
        filetypes=[("Image File", "*.png *.jpg *.jpeg")]
    )

    if file_path:
        selected_image_path = file_path
        print(f"Image selected: {file_path}")

        # Show image preview in left frame
        pil_image = Image.open(file_path)
        ctk_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(200, 180)
        )
        image_label.configure(image=ctk_image, text="")
        image_label.image = ctk_image  # prevent garbage collection

        # Enable the Analyze button now
        analyze_button.configure(state="normal")

        # Update status
        status_label.configure(text="✅ Image loaded! Click Analyze.")


def get_selected_conditions():
    """
    Read all checkboxes and return a list of checked ones.

    Returns list like: ["Diabetic", "Gluten Free"]
    """
    conditions = []

    # checkbox.get() returns 1 if checked, 0 if not
    if checkbox_diabetic.get() == 1:
        conditions.append("Diabetic")
    if checkbox_gluten.get() == 1:
        conditions.append("Gluten Free")
    if checkbox_vegan.get() == 1:
        conditions.append("Vegan")
    if checkbox_nut.get() == 1:
        conditions.append("Nut Allergy")
    if checkbox_hfcs.get() == 1:
        conditions.append("No HFCS")
    if checkbox_dairy.get() == 1:
        conditions.append("Dairy Free")
    if checkbox_veg.get() == 1:
        conditions.append("Vegetarian")
    if checkbox_sodium.get() == 1:
        conditions.append("Low Sodium")

    return conditions


def analyze_image():
    """Called when Analyze button is clicked"""

    # Check if image is uploaded
    if selected_image_path is None:
        status_label.configure(text="⚠️ Please upload an image first!")
        return

    # Get selected conditions
    conditions = get_selected_conditions()
    print(f"Analyzing with conditions: {conditions}")

    # Disable button while analyzing (prevent double clicks)
    analyze_button.configure(state="disabled", text="Analyzing...")

    # Show loading message in results box
    results_textbox.configure(state="normal")
    results_textbox.delete("1.0", "end")
    results_textbox.insert("1.0", "⏳ AI is analyzing your food label...\nPlease wait a few seconds.")
    results_textbox.configure(state="disabled")

    # Update status
    status_label.configure(text="⏳ Sending to AI...")

    # Run AI in background thread so UI doesn't freeze
    def run_ai():
        try:
            # Call the AI engine function
            result = analyze_food_label(selected_image_path, conditions)

            # Update UI with result (must use app.after for thread safety)
            app.after(0, lambda: show_results(result))

        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n\nCheck your API key in .env file."
            app.after(0, lambda: show_results(error_msg))

    # Start background thread
    thread = threading.Thread(target=run_ai, daemon=True)
    thread.start()


def show_results(result_text):
    """Display AI results in the right frame text box"""

    # Re-enable analyze button
    analyze_button.configure(state="normal", text="🔍 Analyze Ingredients")

    # Update status
    status_label.configure(text="✅ Analysis complete!")

    # Show result in textbox
    results_textbox.configure(state="normal")   # Enable editing temporarily
    results_textbox.delete("1.0", "end")        # Clear old content
    results_textbox.insert("1.0", result_text)  # Insert new result
    results_textbox.configure(state="disabled") # Make read-only again

    print("Results displayed!")


# ─────────────────────────────────────────────
# MAIN APP GRID LAYOUT
# ─────────────────────────────────────────────
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)   # Left panel - smaller
app.grid_columnconfigure(1, weight=2)   # Right panel - bigger

# ─────────────────────────────────────────────
# LEFT FRAME
# ─────────────────────────────────────────────
left_frame = ctk.CTkFrame(app, fg_color="gray90")
left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_columnconfigure(1, weight=1)

# Title
left_label = ctk.CTkLabel(
    left_frame,
    text="Select Your Conditions",
    font=("Arial", 12, "bold")
)
left_label.grid(row=0, column=0, columnspan=2, pady=(15, 10))

# ── Checkboxes Column 1 ──
checkbox_diabetic = ctk.CTkCheckBox(left_frame, text="Diabetic")
checkbox_diabetic.grid(row=1, column=0, sticky="w", padx=15, pady=5)

checkbox_gluten = ctk.CTkCheckBox(left_frame, text="Gluten Free")
checkbox_gluten.grid(row=2, column=0, sticky="w", padx=15, pady=5)

checkbox_vegan = ctk.CTkCheckBox(left_frame, text="Vegan")
checkbox_vegan.grid(row=3, column=0, sticky="w", padx=15, pady=5)

checkbox_nut = ctk.CTkCheckBox(left_frame, text="Nut Allergy")
checkbox_nut.grid(row=4, column=0, sticky="w", padx=15, pady=5)

# ── Checkboxes Column 2 ──
checkbox_hfcs = ctk.CTkCheckBox(left_frame, text="No HFCS")
checkbox_hfcs.grid(row=1, column=1, sticky="w", padx=15, pady=5)

checkbox_dairy = ctk.CTkCheckBox(left_frame, text="Dairy Free")
checkbox_dairy.grid(row=2, column=1, sticky="w", padx=15, pady=5)

checkbox_veg = ctk.CTkCheckBox(left_frame, text="Vegetarian")
checkbox_veg.grid(row=3, column=1, sticky="w", padx=15, pady=5)

checkbox_sodium = ctk.CTkCheckBox(left_frame, text="Low Sodium")
checkbox_sodium.grid(row=4, column=1, sticky="w", padx=15, pady=5)

# Image Preview
image_label = ctk.CTkLabel(
    master=left_frame,
    text="No Image Uploaded",
    fg_color="gray80",
    corner_radius=8,
    width=200,
    height=180
)
image_label.grid(row=5, column=0, columnspan=2, padx=20, pady=15)

# Upload Button
upload_button = ctk.CTkButton(
    master=left_frame,
    text="📂 Upload Label",
    command=upload_image
)
upload_button.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 8))

# Analyze Button (disabled until image is uploaded)
analyze_button = ctk.CTkButton(
    master=left_frame,
    text="🔍 Analyze Ingredients",
    command=analyze_image,
    state="disabled",          # Disabled by default
    fg_color="green",
    hover_color="darkgreen"
)
analyze_button.grid(row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 8))

# Status Label
status_label = ctk.CTkLabel(
    left_frame,
    text="Upload an image to begin",
    font=("Arial", 10),
    text_color="gray40"
)
status_label.grid(row=8, column=0, columnspan=2, pady=(0, 15))

# ─────────────────────────────────────────────
# RIGHT FRAME
# ─────────────────────────────────────────────
right_frame = ctk.CTkFrame(app, fg_color="gray85")
right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

right_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

# Results title
right_title = ctk.CTkLabel(
    right_frame,
    text="📊 Analysis Results",
    font=("Arial", 14, "bold")
)
right_title.grid(row=0, column=0, pady=(15, 5))

# Results TextBox (read only, scrollable)
results_textbox = ctk.CTkTextbox(
    right_frame,
    font=("Arial", 12),
    wrap="word",               # Wrap long lines
    state="disabled"           # Read only by default
)
results_textbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))

# Show welcome message in results box
results_textbox.configure(state="normal")
results_textbox.insert(
    "1.0",
    "Welcome to DietLens! 🔍\n\n"
    "Steps:\n"
    "1. Select your dietary conditions on the left\n"
    "2. Click 'Upload Label' to choose a food photo\n"
    "3. Click 'Analyze Ingredients'\n"
    "4. Your personalized results will appear here!\n\n"
    "The AI will flag harmful ingredients based on YOUR specific needs."
)
results_textbox.configure(state="disabled")

# ─────────────────────────────────────────────
# START THE APP
# ─────────────────────────────────────────────
app.mainloop()