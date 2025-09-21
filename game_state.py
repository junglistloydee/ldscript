import json

class GameState:
    """
    Represents the complete, mutable state of the game world.
    This object can be serialized and sent over the network to synchronize clients.
    """
    def __init__(self):
        self.variables = {}
        self.quests = {}
        self.skills = []
        self.inventory = []  # Changed from dict to list of item dicts
        self.entities = {}
        self.items = {}  # Central repository for item definitions

    def to_json(self):
        """Serializes the game state to a JSON string."""
        return json.dumps({
            'variables': self.variables,
            'quests': self.quests,
            'skills': self.skills,
            'inventory': self.inventory,
            'entities': self.entities,
            'items': self.items,
        }, indent=4)

    def from_json(self, json_string):
        """Deserializes a JSON string to update the game state."""
        data = json.loads(json_string)
        self.variables = data.get('variables', {})
        self.quests = data.get('quests', {})
        self.skills = data.get('skills', [])
        self.inventory = data.get('inventory', [])
        self.entities = data.get('entities', {})
        self.items = data.get('items', {})
