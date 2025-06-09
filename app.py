"""This is the main module of the application"""
import os
import argparse
from presentation_layer.location_view import store_selection
from presentation_layer.product_view import add_product_view, get_products_view, search_product_view, update_product_view
from presentation_layer.sale_view import add_sale_to_db, cancel_sale_from_db, get_sales_from_db
from presentation_layer.stock_view import add_stock_view, get_stock_view, request_add_stock_view, get_all_stock_requests_view, fulfill_stock_request_view
from presentation_layer.report_view import print_sales_report_csv, print_store_dashboard

from service_layer.database import init_db
from service_layer.location_repository import get_location_by_name


ACTIONS = {
    "1": ("Voir la liste des produits", get_products_view),
    "2": ("Ajouter un produit", add_product_view),
    "3": ("Chercher un produit", search_product_view),
    "4": ("Enregistrer une vente", add_sale_to_db),
    "5": ("Voir la liste des ventes", get_sales_from_db),
    "6": ("Faire un retour", cancel_sale_from_db),
    "7": ("Add stock", add_stock_view),
    "8": ("Voir stock", get_stock_view),
    "9": ("Modifier un produit", update_product_view),
    "10": ("Demande de reapprovisionnement", request_add_stock_view),
    "11": ("Voir les requetes de reapprovisionnement", get_all_stock_requests_view),
    "12": ("Approuver les requetes de reapprovisionnement", fulfill_stock_request_view),
    "13": ("Voir stock centre logistique", get_stock_view),
    "14": ("Generer un rapport des ventes", print_sales_report_csv),
    "15": ("Tableau de bord des performances", print_store_dashboard),
    "Q": ("Quitter", None),
}

ROLE_PERMISSIONS = {
    "Maison mère": list(ACTIONS.keys()),
    "Centre Logistique": ["1", "2", "3", "7", "8", "11", "12", "Q"],
    "Magasin": ["1", "3", "4", "5", "6", "8", "10", "13", "Q"],
}

# pylint: disable=too-many-branches
def run_cli():
    """Main method of the console app."""
    init_db()

    role = os.getenv("ROLE")
    location_name = os.getenv("LOCATION")
    location = None

    if role and location_name:
        location = get_location_by_name(location_name)
        if not location:
            print(f"Emplacement '{location_name}' introuvable. Passage à la sélection manuelle.")
    else:
        print("🔎 Aucune variable ROLE/LOCATION détectée. Passage à la sélection manuelle.")

    if not location:
        location = store_selection()
        if "maison mère" in location.name.lower():
            role = "Maison mère"
        elif "centre logistique" in location.name.lower():
            role = "Centre Logistique"
        elif "magasin" in location.name.lower():
            role = "Magasin"
        else:
            print("Emplacement inconnu. Aucun rôle attribué.")
            return

    allowed_actions = ROLE_PERMISSIONS.get(role)
    if not allowed_actions:
        print(f"Rôle '{role}' non reconnu.")
        return

    print(f"Bienvenue ({role}) dans {location.name}")

    is_done = False
    while not is_done:
        print("\n=== Menu ===")
        for key in allowed_actions:
            print(f"{key}: {ACTIONS[key][0]}")

        choix = input("Choix : ").strip().upper()

        if choix not in allowed_actions:
            print("Choix invalide ou non autorisé.")
            continue

        if choix == "Q":
            print("Au revoir!")
            is_done = True
        else:
            _, action_fn = ACTIONS[choix]
            if choix in ["4", "5", "6", "7", "8", "10"]:
                action_fn(location)
            elif choix == "13":
                action_fn(get_location_by_name("Centre Logistique"))
            else:
                action_fn()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose mode: CLI or API")
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Select the mode to run: cli or api"
    )

    args = parser.parse_args()

    if args.mode == "cli":
        run_cli()
    elif args.mode == "api":
        run_cli()
