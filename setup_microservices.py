import os
import requests
import time

def main():
    folder_name = "microservices"
    os.makedirs(folder_name, exist_ok=True)
    
    services = []
    
    # Create 25 dummy microservice files
    for i in range(1, 26):
        service_name = f"service_{i}"
        services.append(service_name)
        
        file_path = os.path.join(folder_name, f"{service_name}.py")
        with open(file_path, "w") as f:
            f.write(f"# This is a mock implementation of {service_name}\n")
            f.write(f"def process_data():\n")
            f.write(f"    print('Running {service_name}')\n")
            
    print(f"Created {len(services)} mock microservice files in '{folder_name}' folder.")
    
    # Wait to ensure backend is ready if called immediately
    time.sleep(2)
    
    try:
        print("Uploading services to API...")
        upload_resp = requests.post("http://127.0.0.1:8000/upload", json={"services": services})
        print("Upload Response:", upload_resp.json())
        
        print("Starting migration pipeline...")
        start_resp = requests.post("http://127.0.0.1:8000/start")
        print("Start Response:", start_resp.json())
        
        print("Successfully started migration and uploaded services!")
    except Exception as e:
        print(f"Error accessing backend: {e}")
        print("Please make sure the backend is running.")

if __name__ == '__main__':
    main()
