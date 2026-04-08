import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QLabel, QComboBox, QDialog, QSizePolicy, QLineEdit
from PySide6.QtCore import Qt

# =========================
# SKILL NAME LOOKUP 
# =========================
skills_path = Path(__file__).parent / "SKILLS" / "skills.json"                    # Creates the path to find the correct folder
with open(skills_path, "r", encoding="utf-8") as f:                               # Opens the file in read mode "r"
    skills_data = json.load(f)                                                    # Reads the entire JSON file and converts it to python objects 
            
SKILL_NAME_BY_ID = {}                                                             # Creates an empty dictionary 
            
for skill_key, skill_obj in skills_data.items():                                  # A for loop that gets id and name of skills, combines them together, 
    SKILL_NAME_BY_ID[skill_obj["id"]] = skill_obj["name"]                         # and puts them inside our dictionary
    SKILL_NAME_BY_ID[str(skill_obj["id"])] = skill_obj["name"]

# =========================
# WEAPON ROW CLASS 
# =========================
class WeaponRow(QWidget):                                                         # Creates a custom widget
    def __init__(self, weapon: dict, on_select = None, parent = None):           
        super().__init__(parent)           
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(50)

        self.weapon = weapon                                                      # Stores weapon data for this row
        self.on_select = on_select                                                # Stores function to call when the row is clicked
           
        layout = QHBoxLayout(self)            
        layout.setContentsMargins(8, 2, 8, 2)           
        layout.setSpacing(12)           
           
        name_label = QLabel(self.weapon["name"])                                  # Weapon Name
        rarity_label = QLabel(str(self.weapon["rarity"]))                         # Weapon Rarity
        raw_label = QLabel(str(self.weapon["raw"]))                               # Raw attack value
        aff_label = QLabel(str(self.weapon["affinity"]))                          # Affinity value
                   
        specials = self.weapon.get("specials", [])                                # Gets element/status data
                       
        if not specials:                                                          # If no element/status
            elm_text = "-"                                                        # Display "-"
        else:                                                                     # If element/status exists
            parts = []                                                            # Creates a place to store them
            for s in specials:                                                    # Loops through element/status entries
                if isinstance(s, dict):               
                    elem = s.get("type")                                          # Gets element or status name
                    val  = s.get("value")                                         # Gets element or status value
                    if elem is not None and val is not None:               
                        parts.append(f"{elem.title()} {val}")                     # Example: Thunder 25
            elm_text = ", ".join(parts) if parts else "-"                         # Final element text
                       
        elm_label = QLabel(elm_text)                                              # Element/status label
               
        skills = self.weapon.get("skills", {})                                    # Gets weapon skill 
        if not skills:                                                            # If no skill
            skills_text = "-"                                                     # Displays "-"
        else:                                                                     # If skills
            lines = []                                                            # Creates a place to store them
            for skill_id, level in skills.items():                                # Loops through skill_id and level
                name = SKILL_NAME_BY_ID.get(skill_id, str(skill_id))              # Converts skill_id into skill name
                lines.append(f"{name} {level}")                                   # Example : Attack 3
            skills_text = "\n".join(lines)                                        # Makes it multi line
        skill_label = QLabel(skills_text)                                         # Skill label

        slots = self.weapon["slots"]                                              # Gets slots
        if not slots:                                                             # If no slot
            slots_text = "-"                                                      # Display "-"
        else:
            slots_text = "-".join(str(x) for x in slots)                          # Example : 3-1
        slots_label = QLabel(slots_text)                                          # Slots label

        name_label.setFixedWidth(260)
        rarity_label.setFixedWidth(60)
        raw_label.setFixedWidth(80)
        aff_label.setFixedWidth(80)
        slots_label.setFixedWidth(90)
        elm_label.setFixedWidth(140)
        skill_label.setFixedWidth(220)
        
        rarity_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        raw_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        aff_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        slots_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        elm_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        skill_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        skill_label.setWordWrap(True)

        layout.addWidget(name_label)
        layout.addWidget(rarity_label)
        layout.addWidget(raw_label)
        layout.addWidget(aff_label)
        layout.addWidget(elm_label)
        layout.addWidget(skill_label)
        layout.addWidget(slots_label)
        
    def mousePressEvent(self, event):                                             # Runs when the row is clicked
        if callable(self.on_select):                                              # If a selection function was passed in
            self.on_select(self.weapon)                                           # Sends the weapon data back to the dialog
        else:            
            print(self.weapon)                                                    # Prints weapon data if no function exists (debug)

# =========================                          
#  ARMOR ROW CLASS 
# =========================
class ArmorRow(QWidget):                                                          # Creates a custom widget
    def __init__(self, armor: dict, on_select = None, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(50)

        self.armor = armor                                                        # Stores armor data for this row
        self.on_select = on_select                                                # Stores function to call when the row is clicked

        layout = QHBoxLayout(self)                                                # Horizontal layout for armor columns
        layout.setContentsMargins(8, 2, 8, 2)                                     # Padding inside the row
        layout.setSpacing(12)                                                     # Space between columns

        name_label = QLabel(self.armor["name"])                                   # Armor name
        rarity_label = QLabel(str(self.armor["rarity"]))                          # Armor rarity
        def_label = QLabel(str(self.armor["defense"]))                            # Armor defense (max defense from DataLoader)

        skills = self.armor.get("skills", {})                                     # Gets armor skills dict (skill_id -> level)
        if not skills:                                                            # If no skills
            skills_text = "-"                                                     # Display "-"
        else:
            lines = []                                                            # Stores formatted skill lines
            for skill_id, level in skills.items():                                # Loops through skill_id and level
                name = SKILL_NAME_BY_ID.get(skill_id, str(skill_id))              # Converts skill_id into skill name
                lines.append(f"{name} {level}")                                   # Example: Attack Boost 2
            skills_text = "\n".join(lines)                                        # Makes multi-line skill display

        skills_label = QLabel(skills_text)                                        # Skills label
        skills_label.setWordWrap(True)                                            # Allows multi-line skills

        slots = self.armor.get("slots", [])                                       # Gets slots list
        if not slots:                                                             # If no slots
            slots_text = "-"                                                      # Display "-"
        else:
            slots_text = "-".join(str(x) for x in slots)                          # Example: 3-1
        slots_label = QLabel(slots_text)                                          # Slots label

        name_label.setFixedWidth(260)
        rarity_label.setFixedWidth(60)
        def_label.setFixedWidth(80)
        skills_label.setFixedWidth(320)
        slots_label.setFixedWidth(90)

        rarity_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        def_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        skills_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        slots_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        layout.addWidget(name_label)
        layout.addWidget(rarity_label)
        layout.addWidget(def_label)
        layout.addWidget(skills_label)
        layout.addWidget(slots_label)

    def mousePressEvent(self, event):                                             # Runs when the row is clicked
        if callable(self.on_select):                                              # If a selection function was passed in
            self.on_select(self.armor)                                            # Sends the armor data back to the dialog
        else:
            print(self.armor)                                                     # Debug fallback

# =========================                          
# DECO CLASS 
# =========================
class DecoRow(QWidget):
    def __init__(self, deco: dict, on_select = None, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(50)

        self.deco = deco
        self.on_select = on_select

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        name = deco.get("name", "Unknown")
        level = deco.get("level", 0)

        if "[" in name and "]" in name:
            title_text = name
        else:
            title_text = f"{name} [{level}]"
        
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        skills = deco.get("skills", {})
        if not skills:
            skills_text = "-"
        else:
            skill_names = []
            for skill_id in skills.keys():
                skill_name = SKILL_NAME_BY_ID.get(skill_id, str(skill_id))
                skill_names.append(skill_name)
            skills_text = ", ".join(skill_names)

        skills_label = QLabel(skills_text)
        skills_label.setStyleSheet("color: gray;")
        skills_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(title_label)
        layout.addWidget(skills_label)

    def mousePressEvent(self, event):
        if callable(self.on_select):
            self.on_select(self.deco)

# =========================                          
#  MAIN                              
# =========================  
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
    QLabel { font-size: 12px; }
    QPushButton { font-size: 12px; padding: 4px 8px; }
    QComboBox { font-size: 12px; padding: 2px 6px; }
    """)

    window = QWidget()
    window.setWindowTitle("MHW App v1.0")
    window.resize(1200, 900)

    # =========================
    # DATA / LISTS  (NEW SYSTEM)
    # =========================
    from data_store import load_data                                              # Imports your data loading function
    WEAPONS, ARMOR, ACCESSORIES = load_data("WEAPONS", "ARMOR", "ACCESSORIES")    # Loads all weapons, armor, and decorations into lists                                                               
      
    ARMOR_BY_KIND = {}                                                            # Creates a dictionary to group armor by kind (head/chest/arms/waist/legs)
    for a in ARMOR:                                                               # Loops through every armor piece
        armor_kind = a["kind"]                                                    # Gets armor kind (ex: "head")
            
        if armor_kind not in ARMOR_BY_KIND:                                       # If this kind doesn't exist in the dictionary yet
            ARMOR_BY_KIND[armor_kind] = []                                        # Create an empty list for this kind
            
        ARMOR_BY_KIND[armor_kind].append(a)                                       # Adds this armor piece into its kind list
            
    WEAPONS_BY_KIND = {}                                                          # Creates a dictionary to group weapons by kind (long-sword, great-sword, etc.)
    for w in WEAPONS:                                                             # Loops through every weapon
        weapon_kind = w["kind"]                                                   # Gets weapon kind (ex: "long-sword")
            
        if weapon_kind not in WEAPONS_BY_KIND:                                    # If this kind doesn't exist in the dictionary yet
            WEAPONS_BY_KIND[weapon_kind] = []                                     # Create an empty list for this kind
            
        WEAPONS_BY_KIND[weapon_kind].append(w)                                    # Adds this weapon into its kind list
    
    # =========================
    # HELPER FUNCTIONS
    # =========================
    def kind_to_display(kind: str) -> str:                                        # Turns internal names in UI friendly text
        return kind.replace("-", " ").title()                                     # Example: long-sword = Long Sword
    
    def clear_layout(layout: QVBoxLayout):                                        # Removes all widget from a layout
        while layout.count() > 0:                                                 # Loops until layout is empty
            item = layout.takeAt(0)                                               # Takes an item out of layout
            w = item.widget()                                                     # Gets widget from item
            if w is not None:
                w.deleteLater()                                                   # Safely deletes the widget
    
    def populate_weapons(scroll_layout: QVBoxLayout, weapons, on_select):         # Adds weapon rows to a scroll layout
        for w in weapons:                                                         # Loops through all weapons
            row = WeaponRow(w, on_select = on_select)                             # Creates a clickable row
            scroll_layout.addWidget(row)                                          # Adds row to layout
        scroll_layout.addStretch()                                                # Pushes row to the top

  
    def populate_armor(scroll_layout: QVBoxLayout, armors, on_select):            # Adds armor row to scroll layout
        for a in armors:                                                          # Loops through all armor
            row = ArmorRow(a, on_select = on_select)                              # Creates a clickable row
            scroll_layout.addWidget(row)                                          # Adds row to layout      
        scroll_layout.addStretch()                                                # Pushes row to the top

    # =========================
    # MAIN LAYOUT
    # =========================
    main_layout = QHBoxLayout()                                                   # Main layout is horizontal (left panel + right panel)
    window.setLayout(main_layout)                                                 # Sets main layout onto the window

    # =========================
    # LEFT PANEL (MAIN)
    # =========================
    left_panel = QWidget()                                                        # Creates left panel container
    left_layout = QVBoxLayout()                                                   # Left panel is vertically stacked
    left_layout.setContentsMargins(6, 6, 6, 6)
    left_layout.setSpacing(6)
    left_panel.setLayout(left_layout)                                             # Applies vertical layout to left panel
    main_layout.addWidget(left_panel)                                             # Adds left panel to the main horizontal layout

    weapons_btn = QPushButton("Select Weapon")                                    # Button Creation        
    weapons_btn.setFixedHeight(30)
    helm_btn = QPushButton("Select Helm")                                         # Button Creation
    helm_btn.setFixedHeight(30)
    chest_btn = QPushButton("Select Chest")                                       # Button Creation
    chest_btn.setFixedHeight(30)
    arms_btn = QPushButton("Select Arms")                                         # Button Creation
    arms_btn.setFixedHeight(30)
    waist_btn = QPushButton("Select Waist")                                       # Button Creation
    waist_btn.setFixedHeight(30)
    legs_btn = QPushButton("Select Legs")                                         # Button Creation
    legs_btn.setFixedHeight(30)
    selected_weapon = None                                                        # Stores the currently selected weapon for display

    selected_armor = {                                                            # Stores selected armor piece by slot
    "head": None,
    "chest": None,
    "arms": None,
    "waist": None,
    "legs": None,
    }   

    selected_decos = {                                                            # Stores decorations
    "weapon": [None, None, None],
    "head": [None, None, None],
    "chest": [None, None, None],
    "arms": [None, None, None],
    "waist": [None, None, None],
    "legs": [None, None, None],
    }
    
    # =========================
    # DECOS & BUTTONS (WEAPONS)
    # =========================
    left_layout.addWidget(QLabel("Weapon"))                                      # Title label
    left_layout.addWidget(weapons_btn)                                           # Button
    weapon_deco_container = QWidget()                                            # Creats deco container
    weapon_deco_layout = QHBoxLayout(weapon_deco_container)                      # Gives the container a vertical layout
    weapon_deco_layout.setContentsMargins(0, 0, 0, 0)
    weapon_deco_layout.setSpacing(4)
    left_layout.addWidget(weapon_deco_container)                                 # Adds the container to the left layout

    left_layout.addWidget(QLabel("Helm"))                                        # Title label
    left_layout.addWidget(helm_btn)                                              # Button
    helm_deco_container = QWidget()                                              # Creats deco container
    helm_deco_layout = QHBoxLayout(helm_deco_container)                          # Gives the container a vertical layout
    helm_deco_layout.setContentsMargins(0, 0, 0, 0)
    helm_deco_layout.setSpacing(4)
    left_layout.addWidget(helm_deco_container)                                   # Adds the container to the left layout

    left_layout.addWidget(QLabel("Chest"))                                       # Title label
    left_layout.addWidget(chest_btn)                                             # Button
    chest_deco_container = QWidget()                                             # Creats deco container
    chest_deco_layout = QHBoxLayout(chest_deco_container)                        # Gives the container a vertical layout
    chest_deco_layout.setContentsMargins(0, 0, 0, 0)
    chest_deco_layout.setSpacing(4)
    left_layout.addWidget(chest_deco_container)                                  # Adds the container to the left layout

    left_layout.addWidget(QLabel("Arms"))                                        # Title label
    left_layout.addWidget(arms_btn)                                              # Button
    arms_deco_container = QWidget()                                              # Creats deco container
    arms_deco_layout = QHBoxLayout(arms_deco_container)                          # Gives the container a vertical layout
    arms_deco_layout.setContentsMargins(0, 0, 0, 0)
    arms_deco_layout.setSpacing(4)
    left_layout.addWidget(arms_deco_container)                                   # Adds the container to the left layout

    left_layout.addWidget(QLabel("Waist"))                                       # Title label
    left_layout.addWidget(waist_btn)                                             # Button
    waist_deco_container = QWidget()                                             # Creats deco container
    waist_deco_layout = QHBoxLayout(waist_deco_container)                        # Gives the container a vertical layout
    waist_deco_layout.setContentsMargins(0, 0, 0, 0)
    waist_deco_layout.setSpacing(4)
    left_layout.addWidget(waist_deco_container)                                  # Adds the container to the left layout

    left_layout.addWidget(QLabel("Legs"))                                        # Title label
    left_layout.addWidget(legs_btn)                                              # Button
    legs_deco_container = QWidget()                                              # Creats deco container
    legs_deco_layout = QHBoxLayout(legs_deco_container)                          # Gives the container a vertical layout
    legs_deco_layout.setContentsMargins(0, 0, 0, 0)
    legs_deco_layout.setSpacing(4)
    left_layout.addWidget(legs_deco_container)                                   # Adds the container to the left layout

    ARMOR_DECO_LAYOUT_BY_KIND = {
        "head": helm_deco_layout,
        "chest": chest_deco_layout,
        "arms": arms_deco_layout,
        "waist": waist_deco_layout,
        "legs": legs_deco_layout,
    }
    
    left_layout.addStretch()                                                     # Pushes buttons up

    # =========================
    # LEFT PANEL ACTIONS (WEAPONS)
    # =========================
    def open_weapon_dialog():                                                    # Opens a popup window for weapons
        dialog = QDialog(window)                                                 # Creates a dialog attached to window
        dialog_layout = QVBoxLayout()                                            # Makes the dialog a vertical layout for rows
        dialog.setLayout(dialog_layout)                                          # Applies vertical layout to dialog
    
        # =========================
        # FILTER AREA (WEAPONS)
        # =========================
        weapon_filter_layout = QHBoxLayout()                                     # Filter row layout, Horizontal
        weapon_filter_dropdown = QComboBox()                                     # Dropdown for weapons
    
        for kind in sorted(WEAPONS_BY_KIND.keys()):                              # Loops through all weapon kinds
            display = kind_to_display(kind)                                      # Converts to readble UI
            weapon_filter_dropdown.addItem(display, kind)                        # Adds to dropdown

        weapons_rarity_dropdown = QComboBox()                                    # Dropdown for rarity filter
        for r in range(1, 9):                                                    # A for loop with a range of 9 (1-8)
            weapons_rarity_dropdown.addItem(f"R{r}", r)                          # Adds dropdown items
        weapons_rarity_dropdown.setCurrentIndex(7)                               # Defaults to R8


        weapon_filter_layout.addWidget(weapon_filter_dropdown)                   # Adds weapon kind dropdown to filter row
        weapon_filter_layout.addWidget(weapons_rarity_dropdown)                  # Adds rarity dropdown to filter row
        dialog_layout.addLayout(weapon_filter_layout)                            # Adds filter row to dialog
    
        # =========================
        # TITLE (WEAPONS) 
        # =========================
        header_row = QHBoxLayout()                                               # Horizontal layout for column headers
        header_row.setContentsMargins(8, 0, 8, 0)                                # Spacing
        header_row.setSpacing(12)                                                 
    
        header_title = QLabel("Name")                                            # Column titles  
        header_rarity = QLabel("Rarity")                                         # Column titles 
        header_raw = QLabel("Raw")                                               # Column titles 
        header_affinity = QLabel("Affinity")                                     # Column titles 
        header_element = QLabel("Element")                                       # Column titles 
        header_skills = QLabel("Skills")                                         # Column titles 
        header_slots = QLabel("Slots")                                           # Column titles 
    
        header_title.setFixedWidth(260)                                            
        header_rarity.setFixedWidth(60)                                            
        header_raw.setFixedWidth(80)                                            
        header_affinity.setFixedWidth(80)                                            
        header_slots.setFixedWidth(90)                                            
        header_element.setFixedWidth(140)
        header_skills.setFixedWidth(220)
 
        header_raw.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header_affinity.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header_slots.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header_rarity.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header_element.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header_skills.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
    
        header_row.addWidget(header_title)                                        # Adds header
        header_row.addWidget(header_rarity)                                       # Adds header
        header_row.addWidget(header_raw)                                          # Adds header
        header_row.addWidget(header_affinity)                                     # Adds header
        header_row.addWidget(header_element)                                      # Adds header
        header_row.addWidget(header_skills)                                       # Adds header
        header_row.addWidget(header_slots)                                        # Adds header
        
        dialog_layout.addLayout(header_row)                                       # Adds header row to dialog layout
    
        # =========================
        # SCROLLABLE PART (WEAPONS)
        # =========================
        scroll_area = QScrollArea()                                               # Makes a scroll area
        dialog_layout.addWidget(scroll_area)                                      # Adds widget too dialog
        scroll_area.setWidgetResizable(True)                                      # Makes scroll contents resize with dialog
    
        scroll_content = QWidget()                                                # A widget that lives inside the scroll area
        scroll_layout = QVBoxLayout(scroll_content)                               # Vertical layout that holds WeaponRow widgets
        scroll_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(scroll_content)                                     # Sets the scroll content widget inside the scroll area

        def select_weapon(w):                                                     # Runs when a WeaponRow is clicked
            nonlocal dialog                                                       # Allows this function to close the dialog
            nonlocal selected_weapon                                              # Allows this function to update selected_weapon (from main)
            selected_weapon = w                                                   # Saves the selected weapon dict
            weapons_btn.setText(w.get("name", "Select Weapon"))                   # Updates left panel button text

            clear_layout(weapon_deco_layout)                                      # Clears layout everytime a new weapon is selected

            slots = w.get("slots", [])                                            # Gets slots
            for i, level in enumerate(slots):                                     # Loops through slots
                btn = QPushButton(f"Slot[{level}]")                               # Create the button
                btn.setFixedHeight(28)                                            # Add the height
                weapon_deco_layout.addWidget(btn)                                 # Add it to the layout
                btn.clicked.connect(lambda checked = False, i = i, level = level, btn = btn: open_deco_dialog("weapon", i, level, btn))

            dialog.accept()                                                       # Closes the dialog (selection complete)     

        # =========================
        # FILTER LOGIC (WEAPONS)
        # =========================     
        def load_current_filter():                                                # Refreshes weapon list based on current filters
            kind = weapon_filter_dropdown.currentData()                           # Gets selected weapon kind (ex: "long-sword")
            rarity = weapons_rarity_dropdown.currentData()                        # Gets selected rarity value (1–8)
             
            weapons = WEAPONS_BY_KIND.get(kind, [])                               # Gets all weapons of the selected kind
            weapons = [w for w in weapons if w["rarity"] == rarity]               # Filters weapons by selected rarity
             
            clear_layout(scroll_layout)                                           # Clears old weapon rows from the scroll area
            populate_weapons(                                                     # Re-populates scroll area with filtered weapons
                scroll_layout,
                weapons,
                on_select = select_weapon
            )
        
        weapon_filter_dropdown.currentIndexChanged.connect(load_current_filter)   # Reloads list when weapon kind changes
        weapons_rarity_dropdown.currentIndexChanged.connect(load_current_filter)  # Reloads list when rarity changes
        load_current_filter()                                                     # Initial load when dialog opens
        
        dialog.setWindowTitle("Select Weapon")                                    # Sets dialog title
        dialog.resize(1100, 720)                                                  # Sets dialog size
        dialog.exec()                                                             # Shows dialog and blocks until closed
  
    weapons_btn.clicked.connect(open_weapon_dialog)                               # Button Connection 

    # =========================
    # LEFT PANEL ACTIONS (ARMOR)
    # =========================
    def open_armor_dialog(kind_name):                                             # Opens a popup window to select armor for a specific slot
        dialog = QDialog(window)                                                  # Creates a dialog attached to the main window
        dialog_layout = QVBoxLayout()                                             # Dialog layout is vertical
        dialog.setLayout(dialog_layout)                                           # Applies the vertical layout to the dialog
         
        # =========================       
        # FILTER AREA (ARMOR)       
        # =========================       
        armor_filter_layout = QHBoxLayout()                                       # Filter row layout (horizontal)
        armor_rarity_dropdown = QComboBox()                                       # Dropdown for rarity filter
         
        for r in range(1, 9):                                                     # Adds rarity options 1 through 8
            armor_rarity_dropdown.addItem(f"R{r}", r)                             # Adds dropdown option (text shown, data stored)
        armor_rarity_dropdown.setCurrentIndex(7)                                  # Defaults to R8 (index 7)
         
        armor_filter_layout.addWidget(armor_rarity_dropdown)                      # Adds rarity dropdown to filter row
        dialog_layout.addLayout(armor_filter_layout)                              # Adds the filter row to the dialog
         
        # =========================       
        # TITLE (ARMOR)       
        # =========================       
        header_row = QHBoxLayout()                                                # Horizontal layout for column headers
        header_row.setContentsMargins(8, 0, 8, 0)                                 # Small horizontal padding
        header_row.setSpacing(12)                                                 # Space between header columns
         
        header_name = QLabel("Name")                                              # Column header: armor name
        header_rarity = QLabel("Rarity")                                          # Column header: rarity
        header_def = QLabel("DEF")                                                # Column header: defense
        header_skills = QLabel("Skills")                                          # Column header: armor skills
        header_slots = QLabel("Slots")                                            # Column header: decoration slots
         
        header_name.setFixedWidth(260)                                            # Matches ArmorRow name width
        header_rarity.setFixedWidth(60)                                           # Matches rarity column width
        header_def.setFixedWidth(80)                                              # Matches defense column width
        header_skills.setFixedWidth(320)                                          # Matches skills column width
        header_slots.setFixedWidth(90)                                            # Matches slots column width
         
        header_rarity.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)             # Centers rarity header
        header_def.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)                # Centers DEF header
        header_skills.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)                # Left-align skills header
        header_slots.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)              # Centers slots header
         
        header_row.addWidget(header_name)                                         # Adds name header
        header_row.addWidget(header_rarity)                                       # Adds rarity header
        header_row.addWidget(header_def)                                          # Adds DEF header
        header_row.addWidget(header_skills)                                       # Adds skills header
        header_row.addWidget(header_slots)                                        # Adds slots header
         
        dialog_layout.addLayout(header_row)                                       # Adds header row to dialog layout

        # =========================
        # SCROLLABLE PART (ARMOR)
        # =========================
        scroll_area = QScrollArea()                                               # Creates a scroll area for armor rows
        dialog_layout.addWidget(scroll_area)                                      # Adds scroll area to the dialog
        scroll_area.setWidgetResizable(True)                                      # Makes scroll content resize with the dialog
            
        scroll_content = QWidget()                                                # Widget that will live inside the scroll area
        scroll_layout = QVBoxLayout(scroll_content)                               # Vertical layout that holds ArmorRow widgets
        scroll_layout.setAlignment(Qt.AlignTop)
            
        scroll_area.setWidget(scroll_content)                                     # Sets the scroll content widget inside the scroll area
            
        def select_armor(a):                                                      # Runs when an ArmorRow is clicked
            selected_armor[kind_name] = a                                         # Saves selected armor into correct slot
            name = a.get("name", kind_name.title())                               # Button text
        
            if kind_name == "head":
                helm_btn.setText(name)
                target_layout = ARMOR_DECO_LAYOUT_BY_KIND.get(kind_name)
            elif kind_name == "chest":
                chest_btn.setText(name)
                target_layout = ARMOR_DECO_LAYOUT_BY_KIND.get(kind_name)
            elif kind_name == "arms":
                arms_btn.setText(name)
                target_layout = ARMOR_DECO_LAYOUT_BY_KIND.get(kind_name)
            elif kind_name == "waist":
                waist_btn.setText(name)
                target_layout = ARMOR_DECO_LAYOUT_BY_KIND.get(kind_name)
            elif kind_name == "legs":
                legs_btn.setText(name)
                target_layout = ARMOR_DECO_LAYOUT_BY_KIND.get(kind_name)
            else:
                target_layout = None                                              # Safety fallback
        
            if target_layout is not None:
                clear_layout(target_layout)                                       # Clear ONLY this armor piece's deco area
                target_layout.setAlignment(Qt.AlignLeft)
                slots = a.get("slots", [])                                        # Armor slots come from a (NOT w)
                for i, level in enumerate(slots):
                    btn = QPushButton(f"Slot[{level}]")                       
                    btn.setFixedSize(185, 28)                                        
                    target_layout.addWidget(btn)   
                    btn.clicked.connect(lambda checked = False, k = kind_name, i = i, level = level, btn = btn: open_deco_dialog(k, i, level, btn))     

            dialog.accept()                                                       # Close dialog

        # =========================
        # FILTER LOGIC (ARMOR)
        # =========================
        def load_current_slot():                                                  # Refreshes armor list based on current rarity
            rarity = armor_rarity_dropdown.currentData()                          # Gets selected rarity value (1–8)
            
            armors = ARMOR_BY_KIND.get(kind_name, [])                             # Gets all armor of this kind (ex: head)
            armors = [a for a in armors if a["rarity"] == rarity]                 # Filters armor list by rarity
            
            clear_layout(scroll_layout)                                           # Clears old armor rows from the scroll area
            populate_armor(scroll_layout, armors, on_select = select_armor)       # Re-populates scroll area with filtered armor
            
        armor_rarity_dropdown.currentIndexChanged.connect(load_current_slot)      # Reloads list when rarity changes
        load_current_slot()                                                       # Initial load when dialog opens
            
        dialog.setWindowTitle(f"Select {kind_name}")                              # Sets dialog title
        dialog.resize(1100, 720)                                                  # Sets dialog size
        dialog.exec()                                                             # Shows dialog and blocks until closed

    helm_btn.clicked.connect(lambda checked = False: open_armor_dialog("head"))   # Button Connection
    chest_btn.clicked.connect(lambda checked = False: open_armor_dialog("chest")) # Button Connection
    arms_btn.clicked.connect(lambda checked = False: open_armor_dialog("arms"))   # Button Connection
    waist_btn.clicked.connect(lambda checked = False: open_armor_dialog("waist")) # Button Connection
    legs_btn.clicked.connect(lambda checked = False: open_armor_dialog("legs"))   # Button Connection

    # =========================
    # LEFT PANEL ACTIONS (DECOS)
    # =========================
    def open_deco_dialog(gear_key, slot_index, slot_level, button):
        dialog = QDialog(window)                                                  # Creates a dialog attached to the main window
        dialog_layout = QVBoxLayout()                                             # Dialog layout is vertical
        dialog.setLayout(dialog_layout)                                           # Applies the vertical layout to the dialog

        # =========================
        # FILTER AREA (DECOS)
        # =========================
        search_box = QLineEdit()
        search_box.setPlaceholderText("Search decorations...")
        dialog_layout.addWidget(search_box)

        # =========================
        # SCROLLABLE PART (DECOS)
        # =========================
        scroll_area = QScrollArea()
        dialog_layout.addWidget(scroll_area)
        scroll_area.setWidgetResizable(True)
    
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(scroll_content)

        if gear_key == "weapon":
            allowed_target = "weapon"
        else:
            allowed_target = "armor"

        filtered_decos = []

        for deco in ACCESSORIES:
            if deco.get("allowed_on") != allowed_target:
                continue

            if deco.get("level", 0) > slot_level:
                continue
    
            filtered_decos.append(deco)

        def select_deco(deco: dict):
            selected_decos[gear_key][slot_index] = deco
            button.setText(deco.get("name", "Unknown Deco"))
            dialog.accept()
        
        def render_decos(query: str = ""):
            clear_layout(scroll_layout)
    
            q = query.strip().lower()
    
            for deco in filtered_decos:
                name = deco.get("name", "")
                skills = deco.get("skills", {}) or {}
    
                skill_names = [SKILL_NAME_BY_ID.get(sid, str(sid)) for sid in skills.keys()]
                haystack = (name + " " + " ".join(skill_names)).lower()
    
                if q and q not in haystack:
                    continue
    
                row = DecoRow(deco, on_select=select_deco)
                scroll_layout.addWidget(row)
    
            scroll_layout.addStretch()
    
        search_box.textChanged.connect(render_decos)
    
        render_decos("")
    
        dialog.setWindowTitle("Select Decoration")
        dialog.resize(900, 650)
        dialog.exec()
        
    # =========================
    # RIGHT PANEL (ADDED TO MAIN)
    # =========================
    right_panel = QWidget()
    right_layout = QVBoxLayout()
    right_panel.setLayout(right_layout)
    main_layout.addWidget(right_panel)

    # =========================
    # END STUFF
    # =========================
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()