from app.firebase_setup import db
from app.models.product import Product

class ProductRepository:
    def __init__(self):
        self.collection_name = "products"

    def add_product(self, product: Product):
        if not db:
            print("DB não inicializado")
            return None

        doc_ref = db.collection(self.collection_name).document()
        product.id = doc_ref.id
        doc_ref.set(product.to_dict())
        return product.id

    def get_product(self, product_id):
        if not db:
            return None

        doc = db.collection(self.collection_name).document(product_id).get()
        if not doc.exists:
            return None
        return Product.from_dict(doc.to_dict(), doc.id)

    def get_all_products(self, user_id):
        if not db:
            return []

        try:
            query = db.collection(self.collection_name).where("user_id", "==", user_id)
            return [Product.from_dict(doc.to_dict(), doc.id) for doc in query.stream()]
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []

    def update_product(self, product_id, fields):
        if not db:
            return False

        db.collection(self.collection_name).document(product_id).update(fields)
        return True

    def delete_product(self, product_id):
        if not db:
            return False

        db.collection(self.collection_name).document(product_id).delete()
        return True
