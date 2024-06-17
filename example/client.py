import requests, json, os

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_help(self):
        endpoint = "/help"
        response = requests.get(self.base_url + endpoint)
        return response.json()

    def get_config(self):
        endpoint = "/config"
        response = requests.get(self.base_url + endpoint)
        return response.json()

    def configure_simulation(self, sim_id, config_data):
        endpoint = f"/simulation/{sim_id}/configure"
        response = requests.put(self.base_url + endpoint, json=config_data)
        return response.json()

    def run_simulation(self, sim_id):
        endpoint = f"/simulation/{sim_id}/run"
        response = requests.put(self.base_url + endpoint)
        return response.json()

    def shutdown_server(self):
        endpoint = "/shutdown"
        response = requests.put(self.base_url + endpoint)
        return response.json()

if __name__ == "__main__":
    port = input("Please enter the port number: ")
    base_url = f"http://localhost:{port}"
    client = APIClient(base_url)

    while True:
        print("\nSelect an endpoint to interact with:")
        print("1. GET /help")
        print("2. GET /config")
        print("3. PUT /simulation/{sim_id}/configure")
        print("4. PUT /simulation/{sim_id}/run")
        print("5. PUT /shutdown")
        print("6. Exit")

        choice = input("Enter the number of your choice: ")

        match choice:
            case "1":
                print("Help Endpoint Response:")
                response = client.get_help()
                print(json.dumps(response, indent=4))

            case "2":
                print("Config Endpoint Response:")
                response = client.get_config()
                print(json.dumps(response, indent=4))

            case "3":
                sim_id = input("Enter simulation ID: ")
                json_path = input("Enter the path to the JSON configuration file: ")

                if os.path.exists(json_path):
                    with open(json_path, 'r') as file:
                        config_data = json.load(file)
                    print("Configure Simulation Response:")
                    response = client.configure_simulation(sim_id, config_data)
                    print(json.dumps(response, indent=4))
                else:
                    print(f"File not found: {json_path}")

            case "4":
                sim_id = input("Enter simulation ID: ")
                print("Run Simulation Response:")
                response = client.run_simulation(sim_id)
                print(json.dumps(response, indent=4))

            case "5":
                print("Shutdown Server Response:")
                response = client.shutdown_server()
                print(json.dumps(response, indent=4))

            case "6":
                print("Exiting program.")
                break

            case _:
                print("Invalid choice, please try again.")
