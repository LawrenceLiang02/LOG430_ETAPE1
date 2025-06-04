"""Stock service module for the business layer"""
from service_layer.product_repository import get_products
from service_layer.stock_repository import add_stock, get_stock, create_stock_request, get_all_stock_requests, fulfill_stock_request


def add_stock_view(location):
    """Adds stock to a location"""
    print("\n=== Ajouter un stock ===")
    products = get_products()
    if not products:
        print("Aucun produit trouvé.")
        return

    print("\n=== Produits disponibles ===")
    for product in products:
        print(f"[{product.id}] {product.name} - {product.price:.2f} $")

    selected_product = None
    while not selected_product:
        try:
            product_id = int(input("Entrez l'ID du produit à ajouter en stock : ").strip())
            selected_product = next((p for p in products if p.id == product_id), None)
            if not selected_product:
                print("Produit introuvable.")
        except ValueError:
            print("Veuillez entrer un ID valide.")

    while True:
        try:
            quantity = int(input("Entrez la quantité à ajouter : ").strip())
            if quantity < 0:
                raise ValueError
            break
        except ValueError:
            print("Veuillez entrer une quantité valide.")

    add_stock(selected_product.id, location, quantity)

def get_stock_view(location):
    """Get stock from db"""
    stock_list = get_stock(location)

    print(f"\nStock pour '{location.name}':")
    for stock in stock_list:
        print(f"ID: {stock.product.id} | Nom: {stock.product.name} | Quantity:{stock.quantity}")

def request_add_stock_view(location):
    """Request to add stock for a location"""
    print("\n=== Ajouter un stock ===")
    products = get_products()
    if not products:
        print("Aucun produit trouvé.")
        return

    print("\n=== Produits disponibles ===")
    for product in products:
        print(f"[{product.id}] {product.name} - {product.price:.2f} $")

    selected_product = None
    while not selected_product:
        try:
            product_id = int(input("Entrez l'ID du produit à ajouter en stock : ").strip())
            selected_product = next((p for p in products if p.id == product_id), None)
            if not selected_product:
                print("Produit introuvable.")
        except ValueError:
            print("Veuillez entrer un ID valide.")

    while True:
        try:
            quantity = int(input("Entrez la quantité à ajouter : ").strip())
            if quantity <= 0:
                raise ValueError
            break
        except ValueError:
            print("Veuillez entrer une quantité valide (entier positif).")

    success = create_stock_request(location.id, selected_product.id, quantity)
    if success:
        print(f"Demande de stock créée pour {selected_product.name} ({quantity} unités).")
    else:
        print("Échec lors de la création de la demande.")

def get_all_stock_requests_view():
    """Affiche toutes les demandes de stock pour toutes les locations"""
    print("\n=== Toutes les demandes de stock ===")

    requests = get_all_stock_requests()
    if not requests:
        print("Aucune demande de stock trouvée.")
        return

    for req in requests:
        print(
            f"ID: {req.id}, "
            f"Produit: {req.product.name}, "
            f"Quantité: {req.quantity}, "
            f"Lieu: {req.location.name}"
        )

def fulfill_stock_request_view():
    """Allow to fulfill stock request view"""
    print("\n=== Traitement d'une demande de stock ===")

    requests = get_all_stock_requests()
    if not requests:
        print("Aucune demande en attente.")
        return

    for req in requests:
        print(
            f"ID: {req.id}, "
            f"Produit: {req.product.name}, "
            f"Quantité: {req.quantity}, "
            f"Vers: {req.location.name}"
        )

    try:
        req_id = int(input("Entrez l'ID de la demande à traiter : ").strip())
    except ValueError:
        print("ID invalide.")
        return

    success, message = fulfill_stock_request(req_id)
    if success:
        print(f"{message}")
    else:
        print(f"{message}")