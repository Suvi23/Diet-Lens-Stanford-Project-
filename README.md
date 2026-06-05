# Diet-Lens-Stanford-Project-
"Diet Lens" is an AI-powered Food Label Analyzer that helps people make healthier food choices. It understands the food ingredients and provides personalized health insights based on the user's dietary preferences.
DEMONSTRATION VIDEO LINK : https://youtu.be/eEeat332pV8

To Run the project we need to Run the DietLensApp.py file.


About the 3 project files:

1️⃣ DietLensApp.py → 🖥️ User Interface (Frontend)
=======>>>What it does:Handles everything the user sees and interacts with.

Contains:

CustomTkinter window layout
Image upload button
Diet condition checkboxes (Vegetarian, Vegan, Nut Allergy, etc.)
“Analyze” button
Results display panel
Calls ai_engine.analyze_food_label()
Role in system:    User → UI → Sends image + conditions to ai_engine
It does zero food logic. Only handles display and interaction.

2️⃣ ai_engine.py → 🤖 AI Processing Layer
=======>>>What it does:Talks to Groq Vision AI to read the food label image.

Contains:

Groq API connection
Image → Base64 conversion
Prompt builder (tells AI how to extract ingredients)
Removes AI-written verdict
Calls verdict_checker.py
Combines AI analysis + Python verdict
Formats output nicely
Role in system:    UI → AI Engine → AI extracts ingredients
                            ↓
                   verdict_checker decides SAFE/NOT SAFE
AI never decides the final verdict — Python does.

3️⃣ verdict_checker.py → 🧠 Rule Engine (Core Logic)
=======>>> What it does:  This is the brain of your system.

Contains:

Condition rules (Vegetarian, Vegan, Diabetic, Nut Allergy, etc.)
Keyword lists
Regex-based ingredient detection
Sodium checker
Final verdict builder
Reason generator
Role in system:         Receives AI text → Applies strict rule logic → Returns final verdict
✅ Deterministic
✅ No randomness
✅ No AI decision making


