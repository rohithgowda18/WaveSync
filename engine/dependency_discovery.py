import os
import re

# You can later fetch this dynamically from DB
SERVICE_NAMES = [
    "AuthService", "UserService", "PaymentService",
    "OrderService", "InventoryService", "NotificationService",
    "ProductService", "CartService", "ShippingService"
]

def normalize_service_name(name: str):
    parts = name.split("-")
    return "".join(part.capitalize() for part in parts)


def extract_dependencies_from_text(text: str):
    dependencies = set()

    # Detect URLs like http://auth-service
    urls = re.findall(r"http://([a-zA-Z\-]+)", text)

    for url in urls:
        service_name = normalize_service_name(url)
        dependencies.add(service_name)

    # Strict matching for known services (NO partial match)
    for service in SERVICE_NAMES:
        pattern = r"\b" + re.escape(service.lower()) + r"\b"
        if re.search(pattern, text.lower()):
            dependencies.add(service)

    return list(dependencies)


def scan_directory(path: str):
    results = {}

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except:
                    continue

                deps = extract_dependencies_from_text(content)

                service_name = file.replace(".py", "").title().replace("_", "")
                results[service_name] = deps

    return results