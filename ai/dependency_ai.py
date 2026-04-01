def infer_dependencies(name: str, description: str):
    desc = description.lower()
    dependencies = set()

    # -----------------------------
    # AUTH / USER
    # -----------------------------
    if any(w in desc for w in ["user", "profile", "account", "login", "authentication", "identity", "kyc", "verification"]):
        dependencies.add("AuthService")

    # -----------------------------
    # PAYMENT / FINANCE
    # -----------------------------
    if any(w in desc for w in ["payment", "billing", "transaction", "finance", "emi", "loan"]):
        dependencies.update(["AuthService", "PaymentService"])

    # -----------------------------
    # ORDER / ECOMMERCE
    # -----------------------------
    if any(w in desc for w in ["order", "checkout", "cart"]):
        dependencies.update(["UserService", "PaymentService", "InventoryService"])

    # -----------------------------
    # PRODUCT / INVENTORY
    # -----------------------------
    if any(w in desc for w in ["product", "inventory", "warehouse", "stock"]):
        dependencies.add("ProductService")

    # -----------------------------
    # SHIPPING
    # -----------------------------
    if any(w in desc for w in ["delivery", "shipping", "logistics", "tracking"]):
        dependencies.update(["OrderService", "UserService"])

    # -----------------------------
    # NOTIFICATIONS
    # -----------------------------
    if any(w in desc for w in ["notification", "email", "sms", "alert"]):
        dependencies.add("UserService")

    # -----------------------------
    # MONITORING
    # -----------------------------
    if any(w in desc for w in ["monitor", "analytics", "metrics", "logging"]):
        dependencies.add("LoggingService")

    # -----------------------------
    # AI / RECOMMENDATION
    # -----------------------------
    if any(w in desc for w in ["recommend", "ai", "ml", "prediction"]):
        dependencies.update(["UserService", "ProductService"])

    # -----------------------------
    # SECURITY / FRAUD
    # -----------------------------
    if any(w in desc for w in ["fraud", "risk", "security"]):
        dependencies.update(["UserService", "TransactionService"])

    # -----------------------------
    # MEDIA
    # -----------------------------
    if any(w in desc for w in ["media", "video", "image", "upload", "file"]):
        dependencies.add("CDNService")

    # -----------------------------
    # CLEANUP
    # -----------------------------

    # remove self dependency
    if name in dependencies:
        dependencies.remove(name)

    # remove invalid services
    VALID_SERVICES = [
        "AuthService", "UserService", "ProductService", "InventoryService",
        "PaymentService", "OrderService", "LoggingService", "CDNService",
        "TransactionService"
    ]

    dependencies = {d for d in dependencies if d in VALID_SERVICES}

    # fallback
    if not dependencies:
        dependencies.add("LoggingService")

    # limit size (important)
    dependencies = list(dependencies)[:3]

    return dependencies