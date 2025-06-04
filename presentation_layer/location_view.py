"""Location service module for the business layer"""
from service_layer.location_repository import get_all_locations


def store_selection():
    """Shows a list of store and returns the selected store."""
    locations = get_all_locations()
    if not locations:
        print("Aucun magasin trouvé.")
        return None

    print("=== Veuillez choisir votre magasin ===")
    for i, loc in enumerate(locations, 1):
        print(f"{i}. {loc.name}")

    while True:
        choix = input("Choix: ").strip()
        if choix.isdigit():
            idx = int(choix) - 1
            if 0 <= idx < len(locations):
                return locations[idx]
        print("Choix invalide. Veuillez réessayer.")
