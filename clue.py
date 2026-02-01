#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mystery Game Generator - Windows Compatible
A command-line mystery game where you investigate a crime.
"""

import os
import shutil
from pathlib import Path
import random
import sys
import time

# Check Python version
if sys.version_info < (3, 6):
    print("Error: This script requires Python 3.6 or higher.")
    print("Your version: {}.{}".format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)

structure = {
  "town hall": {
    "offices": {
      "records": {
        "archives": {}
      },
      "meeting rooms": {
        "council chamber": {}
      }
    }
  },
  "park": {
    "playground": {
      "sandbox": {}
    },
    "pond": {
      "dock": {}
    },
    "gazebo": {}
  },
  "shops": {
    "bakery": {
      "kitchen": {},
      "storage": {}
    },
    "market": {
      "aisles": {},
      "stockroom": {}
    },
    "cafe": {}
  },
  "Residential Area": {
    "mansion": {
      "library": {
        "study": {}
      },
      "garden": {
        "greenhouse": {}
      }
    },
    "cottage": {
      "living room": {},
      "cellar": {}
    }
  },
  "school": {
    "classrooms": {
      "science lab": {},
      "art room": {}
    },
    "gymnasium": {},
    "cafeteria": {
      "kitchen": {}
    }
  }
}

class MysteryGame:
  def __init__(self):
    # All possible people who might be in the town
    self.all_people = [
      "The Librarian", "The Shopkeeper", "The Gardener", "The Teacher", "The Mayor", "The Chef",
      "The Postman", "The Baker", "The Police Officer", "The Doctor", "The Artist", "The Musician",
      "The Carpenter", "The Tailor", "The Banker", "The Journalist", "The Florist", "The Clockmaker",
      "The Blacksmith", "The Innkeeper","The Jocker", "The Engineer"
    ]

    self.students = [
      "Ludwing", "Nadissa"
    ]

    # All possible objects that might be found
    self.all_objects = [
      "Garden Shears", "Kitchen Knife", "Heavy Book", "Bronze Trophy", "Glass Bottle", "Letter Opener",
      "Walking Stick", "Brass Candlestick", "Old Key", "Fountain Pen", "Silver Watch", "Magnifying Glass",
      "Antique Compass", "Paint Brush", "Crystal Vase", "Iron Poker", "Leather Gloves", "Brass Bell",
      "Steel Ruler", "Wooden Box"
    ]

    # We'll populate these during game generation
    self.suspects = []        # The 6 chosen suspects
    self.weapons = []         # The 6 chosen weapons
    self.guilty_suspect = ""  # The answer
    self.murder_weapon = ""   # The answer
    self.murder_location = "" # The answer

    # Will store our clue distribution
    self.room_contents = {}   # Will map room paths to their contents

    # Get all possible room paths
    self.all_rooms = self._get_all_rooms()

  def _get_all_rooms(self):
    """Gets all possible room paths from our directory structure."""
    def get_paths(structure, current_path=""):
      paths = []
      for name, substructure in structure.items():
        new_path = "{}/{}".format(current_path, name) if current_path else name
        paths.append(new_path)
        if substructure:  # If there are subdirectories
          paths.extend(get_paths(substructure, new_path))
      return paths
    return get_paths(structure)

  def _get_leaf_rooms(self):
    """Gets only room paths that have no subdirectories."""
    def get_leafs(structure, current_path=""):
        leafs = []
        for name, substructure in structure.items():
            new_path = "{}/{}".format(current_path, name) if current_path else name
            if not substructure:
                leafs.append(new_path)
            else:
                leafs.extend(get_leafs(substructure, new_path))
        return leafs
    return get_leafs(structure)

  def generate_mystery(self, num_suspects=6, num_weapons=6):
    """
    Generates all elements of our mystery game.

    Args:
        num_suspects (int): Number of suspects to include in the game. 
                           Must be between 3 and len(all_people).
        num_weapons (int): Number of weapons to include in the game.
                          Must be between 3 and len(all_objects).
    """
    # Input validation to ensure the game is solvable
    num_suspects = max(3, min(num_suspects, len(self.all_people)))
    num_weapons = max(3, min(num_weapons, len(self.all_objects)))

    # Select our random suspects and weapons based on the parameters
    self.suspects = random.sample(self.all_people, num_suspects)
    self.weapons = random.sample(self.all_objects, num_weapons)

    # Choose our answers
    self.guilty_suspect = random.choice(self.suspects)
    self.murder_weapon = random.choice(self.weapons)
    
    # Ensure murder location is a specific room (leaf node)
    leaf_rooms = self._get_leaf_rooms()
    self.murder_location = random.choice(leaf_rooms)

    # Remove answers from distribution pools
    available_suspects = [s for s in self.suspects if s != self.guilty_suspect]
    available_weapons = [w for w in self.weapons if w != self.murder_weapon]
    available_rooms = [r for r in self.all_rooms if r != self.murder_location]

    # Scale the number of extra people and objects based on the game difficulty
    extra_people_count = min(
      len(available_rooms) - len(available_suspects),
      round((20 - num_suspects) * 0.5)
    )
    extra_objects_count = min(
      len(available_rooms) - len(available_weapons),
      round((20 - num_weapons) * 0.5)
    )

    # Create pools for distribution with scaled red herrings
    distribution_people = available_suspects + random.sample(
      [p for p in self.all_people if p not in self.suspects],
      extra_people_count
    )

    distribution_objects = available_weapons + random.sample(
      [o for o in self.all_objects if o not in self.weapons],
      extra_objects_count
    )

    # Initialize all rooms as empty
    self.room_contents = {room: {"people": [], "objects": []} for room in self.all_rooms}

    # Distribute items
    for person in distribution_people:
      room = random.choice(available_rooms)
      self.room_contents[room]["people"].append(person)

    for obj in distribution_objects:
      room = random.choice(self.all_rooms)
      self.room_contents[room]["objects"].append(obj)

  def generate_notebook(self):
    """Generates the content for notebook.md"""
    suspects_list = "\n".join("- [ ] {}".format(suspect) for suspect in self.suspects)
    weapons_list = "\n".join("- [ ] {}".format(weapon) for weapon in self.weapons)
    
    return """# Detective's Notebook

## Suspects
{}

## Weapons
{}

## Notes
*Use this space to record your findings and deductions...*

Location of the crime is still unknown - the room must have been empty when it happened...
""".format(suspects_list, weapons_list)

  def remove_readonly(self, func, path, excinfo):
    """Error handler for Windows readonly files."""
    os.chmod(path, 0o777)
    func(path)

  def safe_remove_directory(self, path):
    """Safely removes a directory, handling Windows permission issues."""
    max_attempts = 3
    for attempt in range(max_attempts):
      try:
        if os.path.exists(path):
          # On Windows, we need to handle readonly files
          if sys.platform == 'win32':
            shutil.rmtree(path, onerror=self.remove_readonly)
          else:
            shutil.rmtree(path)
        return True
      except PermissionError as e:
        if attempt < max_attempts - 1:
          print("Waiting for file access... (attempt {}/{})".format(attempt + 1, max_attempts))
          time.sleep(1)
        else:
          print("\nError: Cannot delete the 'game' folder.")
          print("Please close any programs that might be using files in the 'game' folder")
          print("(like File Explorer, text editors, or Thonny's file browser).")
          print("\nThen run this script again.")
          return False
      except Exception as e:
        print("Error removing directory: {}".format(e))
        return False
    return False

  def create_game_directories(self, base_path="game"):
    base_dir = Path(base_path)

    # Try to remove existing game directory
    if base_dir.exists():
      print("Removing old game directory...")
      if not self.safe_remove_directory(str(base_dir)):
        sys.exit(1)

    print("Creating new game directory...")
    base_dir.mkdir()

    # Create notebook.md
    with open(str(base_dir / "notebook.md"), "w", encoding='utf-8') as f:
      f.write(self.generate_notebook())

    def create_directories(current_path, structure):
      for name, substructure in structure.items():
        new_path = current_path / name

        try:
          new_path.mkdir(exist_ok=True)
        except Exception as e:
          print("Warning: Could not create directory {}: {}".format(new_path, e))
          continue

        # Get relative path for content lookup
        rel_path = str(new_path.relative_to(base_dir))

        # Get and create room contents
        contents = self.room_contents.get(rel_path, {"people": [], "objects": []})

        try:
          # Create persons.txt
          with open(str(new_path / "persons.txt"), "w", encoding='utf-8') as f:
            f.write("\n".join(contents["people"]))

          # Create objects.txt
          with open(str(new_path / "objects.txt"), "w", encoding='utf-8') as f:
            f.write("\n".join(contents["objects"]))

        except Exception as e:
          print("Error creating files in {}: {}".format(new_path, e))

        # Process subdirectories
        if substructure:
          create_directories(new_path, substructure)

    create_directories(base_dir, structure)

  def create_accuse_script(self):
    """Generates the 'accuse.py' script for checking the solution."""
    import hashlib
    
    def get_hash(s):
        return hashlib.md5(s.lower().strip().encode()).hexdigest()

    suspect_hash = get_hash(self.guilty_suspect)
    weapon_hash = get_hash(self.murder_weapon)
    location_hash = get_hash(self.murder_location)
    location_name_hash = get_hash(self.murder_location.split('/')[-1])

    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import hashlib

def get_hash(s):
    return hashlib.md5(s.lower().strip().encode()).hexdigest()

EXPECTED_SUSPECT = "{}"
EXPECTED_WEAPON = "{}"
EXPECTED_LOCATION_HASHES = ["{}", "{}"]

def print_usage():
    print("Usage: python accuse.py \\"<Suspect Name>\\" \\"<Weapon Name>\\" \\"<Room Name>\\"")
    print("Example: python accuse.py \\"The Gardener\\" \\"Garden Shears\\" \\"Garden\\"")
    print("Don't forget the quotes if the name has spaces!")

if len(sys.argv) != 4:
    print("❌ Error: You need to provide exactly 3 arguments.")
    print_usage()
    sys.exit(1)

suspect = sys.argv[1]
weapon = sys.argv[2]
location = sys.argv[3]

suspect_match = get_hash(suspect) == EXPECTED_SUSPECT
weapon_match = get_hash(weapon) == EXPECTED_WEAPON
location_match = get_hash(location) in EXPECTED_LOCATION_HASHES

if suspect_match and weapon_match and location_match:
    print("\\n🎉 CONGRATULATIONS DETECTIVE! 🎉")
    print("You have correctly identified the killer, the weapon, and the location!")
    print("It was {{}} with the {{}} in the {{}}.".format(suspect, weapon, location))
    print("The town is safe once again thanks to your command line skills.")
    sys.exit(0)
else:
    print("\\nYour accusation is incorrect:")
    print("Suspect:  {{}}".format('✅ Correct' if suspect_match else '❌ Incorrect'))
    print("Weapon:   {{}}".format('✅ Correct' if weapon_match else '❌ Incorrect'))
    print("Location: {{}}".format('✅ Correct' if location_match else '❌ Incorrect'))
    print("\\nKeep investigating!")
    sys.exit(1)
'''.format(suspect_hash, weapon_hash, location_hash, location_name_hash)
    
    accuse_path = Path("game/accuse.py")
    with open(str(accuse_path), "w", encoding='utf-8') as f:
        f.write(script_content)

  def check_lateral_path(self, current_segments, next_segments):
    if len(current_segments) != len(next_segments):
        return False
        
    parent_segments = current_segments[:-1]
    next_parent_segments = next_segments[:-1]
    
    return (parent_segments == next_parent_segments and 
            current_segments[-1] != next_segments[-1])

  def create_lateral_clue(self, current_room, next_room):
    next_location = next_room.split('/')[-1]
    lateral_path_dialogue_variations = [
        "You hear sound coming from the nearby {next_location}.",
        "A staff member mentions checking the {next_location}.",
        "Through the window, you can see the lights are on in the {next_location}.",
        "The janitor suggests taking a look in the {next_location}.",
        "Recent activity has been reported in the {next_location} area.",
        "You overhear someone mentioning suspicious noises from the {next_location}.",
        "You get the feeling you should check the {next_location}.",
        "Security cameras caught movement near the {next_location} entrance.",
        "A cleaning schedule shows the {next_location} was cleaned after this spot.",
        "Local gossip suggests something unusual in the {next_location}."
    ]
    chosen_dialogue = random.choice(lateral_path_dialogue_variations)
    
    clue_text = """Investigation Update:

{}

Hint: To reach this location, you'll need to move back and down to the next location: 'cd "../{}"'
""".format(chosen_dialogue.format(next_location=next_location), next_location)
    
    current_path = Path("game") / Path(current_room)
    with open(str(current_path / "clue.txt"), "w", encoding='utf-8') as f:
        f.write(clue_text)
    
  def create_upward_clue(self, current_room, next_room):
    next_location = next_room.split('/')[0]
    next_location_specific = next_room.split('/')[-1]

    upward_dialogue_variations = [
        "Something tells me we should go back and check somewhere else in the {next_location}.",
        "A police report mentions returning to the {next_location} for another look.",
        "Your intuition suggests backtracking to the {next_location} and looking for something else.",
        "Maybe we should check back in the {next_location}.",
        "An old note suggests reconsidering the {next_location}.",
        "The evidence points back to the {next_location}.",
        "We should double-check something back in the {next_location}.",
        "New information suggests returning to the {next_location}.",
        "Perhaps we missed a detail in the {next_location}.",
        "The investigation leads back to the {next_location}."
    ]
    
    updown_dialogue_variations = [
        "Check the {next_location_specific} in the {next_location}.",
        "Go to the {next_location_specific} in the {next_location}.",
        "Go back and check the {next_location_specific} in the {next_location}.",
    ]

    if next_location != next_location_specific:
      chosen_dialogue = random.choice(updown_dialogue_variations)
    else:
      chosen_dialogue = random.choice(upward_dialogue_variations)
    
    clue_text = """New Clue:

{}

Hint: You'll need to go back several directories to reach this location.
Remember that you can use multiple '../' to go up multiple levels:
- 'cd ..'    goes up one level
- 'cd ../..' goes up two levels
- and so on...

""".format(chosen_dialogue.format(next_location=next_location, next_location_specific=next_location_specific))
    
    current_path = Path("game") / Path(current_room)
    with open(str(current_path / "clue.txt"), "w", encoding='utf-8') as f:
        f.write(clue_text)
    
  def generate_final_location_variations(self):
    """Creates dramatic dialogue templates for the final revelation."""
    dialogue_variations = [
        "The evidence is clear - this is where the crime took place! The room's undisturbed state tells the whole story.",
        "At last! This untouched crime scene reveals the truth. No one has been here since the incident.",
        "Your detective instincts were right - this empty room holds the answers. The pristine state of things confirms this is where it happened.",
        "The undisturbed dust patterns confirm it - you've found the crime scene! The emptiness of the room speaks volumes.",
        "Here it is - the untouched crime scene! The stillness of this room suggests no one has entered since the incident.",
        "You can feel it - this is where it happened. The undisturbed state of the room confirms your suspicions.",
        "The perfect preservation of this room tells you everything - this is definitely the crime scene!",
        "Your investigation has led you to the truth - this empty room is where it all happened!",
        "The pristine condition of this room confirms your theory - you've found the crime scene!",
        "Success! This untouched room is exactly what you've been looking for - the scene of the crime!"
    ]
    return dialogue_variations

  def add_murder_location_to_path(self, important_rooms):
    """Adds the murder location to our sequence of important rooms."""
    updated_rooms = important_rooms + [self.murder_location]
    
    dialogue_options = self.generate_final_location_variations()
    chosen_dialogue = random.choice(dialogue_options)
    
    final_clue = """Investigation Conclusion:

{}

Your careful detective work has paid off. The empty state of this room matches 
witness accounts - no one was around when the crime occurred. This must be 
where the murderer carried out their plan!

Make sure to document this discovery in your notebook.md file along with your 
other findings about the weapon and suspect.""".format(chosen_dialogue)

    murder_path = Path("game") / Path(self.murder_location)
    with open(str(murder_path / "clue.txt"), "w", encoding='utf-8') as f:
        f.write(final_clue)
    
    return updated_rooms

  def create_breadcrumbs(self):
    important_rooms = []

    for room_path, contents in self.room_contents.items():
      has_suspect = any(person in self.suspects for person in contents["people"])
      has_weapon = any(obj in self.weapons for obj in contents["objects"])

      if has_suspect or has_weapon:
        important_rooms.append(room_path)
    
    important_rooms.sort()
    important_rooms = self.add_murder_location_to_path(important_rooms)

    dialogue_variations = [
      "I overheard {person} mentioning something strange they noticed near the {location}.",
      "{person} came running to the police station, insisting they saw suspicious activity around the {location}.",
      "According to {person}, there were unusual sounds coming from the {location} last night.",
      "During the morning roll call, {person} reported odd footprints leading to the {location}.",
      "The night watchman spoke with {person}, who noticed an unfamiliar figure lurking near the {location}.",
      "{person} left an anonymous tip about unusual activity at the {location}.",
      "Earlier today, {person} reported seeing an unexpected light in the {location}.",
      "A note from {person} mentions witnessing something concerning near the {location}.",
      "While making their rounds, {person} noticed the {location} door was slightly ajar.",
      "Local residents say {person} was the last one to report activity near the {location}."
    ]

    if not important_rooms:
      return

    first_destination = important_rooms[0].split('/')[-1]
    observer = random.choice(self.all_people)
    chosen_dialogue = random.choice(dialogue_variations)

    clue_text = chosen_dialogue.format(person=observer, location=first_destination)

    full_clue = """Detective's Initial Report:

{}

This seems like a good place to start our investigation. Remember to:
- Use 'cd' to move between locations
- Use 'ls' to list the contents of each location
- Use 'cat' to read any text files you find
""".format(clue_text)

    base_dir = Path("game")
    with open(str(base_dir / "clue.txt"), "w", encoding='utf-8') as f:
      f.write(full_clue)

    next_location_dialogue_variations = [
      "You notice fresh footprints leading towards the {next_location}.",
      "A trail of scattered papers points deeper into the {next_location}.",
      "Through the window, you spot movement in the direction of the {next_location}.",
      "The floorboards creak, suggesting someone recently walked towards the {next_location}.",
      "A local resident mentions seeing a shadowy figure entering the {next_location}.",
      "You find a dropped keychain with a tag labeled '{next_location}'.",
      "The dust on the floor shows a clear path heading to the {next_location}.",
      "A security guard mentions hearing noises coming from the {next_location}.",
      "Recent scratches on the floor lead towards the {next_location}.",
      "A hastily written note mentions checking the {next_location} next."
    ]

    for i in range(len(important_rooms) - 1):
        current_room = important_rooms[i]
        next_room = important_rooms[i + 1]
        
        current_segments = current_room.split('/')
        next_segments = next_room.split('/')
        
        is_subdirectory = (
            len(next_segments) > len(current_segments) and
            all(current_segments[j] == next_segments[j] 
                for j in range(len(current_segments)))
        )
        
        if is_subdirectory:
            next_location = next_segments[len(current_segments)]
            chosen_dialogue = random.choice(next_location_dialogue_variations)
            
            clue_text = """Investigation Update:

{}

Remember: Use 'cd "{}"' to follow this lead.
""".format(chosen_dialogue.format(next_location=next_location), next_location)
            
            current_path = Path("game") / Path(current_room)
            with open(str(current_path / "clue.txt"), "w", encoding='utf-8') as f:
                f.write(clue_text)
            
        elif self.check_lateral_path(current_segments, next_segments):
            self.create_lateral_clue(current_room, next_room)
        else:
          self.create_upward_clue(current_room, next_room)

    return important_rooms

if __name__ == "__main__":
  try:
    print("=== Mystery Game Generator ===")
    print("Generating your mystery...")
    game = MysteryGame()
    game.generate_mystery(3, 3)
    game.create_game_directories()
    game.create_breadcrumbs()
    game.create_accuse_script()
    print("\n✅ Your mystery game has been generated!")
    print("\nTo start playing:")
    print("1. Open a terminal/command prompt")
    print("2. Navigate to this folder")
    print("3. Type: cd game")
    print("4. Type: cat clue.txt")
    print("\nGood luck, Detective!")
  except KeyboardInterrupt:
    print("\n\nGame generation cancelled.")
    sys.exit(0)
  except Exception as e:
    print("\n❌ Error generating game: {}".format(e))
    import traceback
    traceback.print_exc()
    print("\nIf you see a PermissionError, please:")
    print("- Close Thonny's file browser")
    print("- Close File Explorer if it's open in the 'game' folder")
    print("- Try running the script again")
    sys.exit(1)