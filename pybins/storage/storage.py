class PackageStorage:
    def __init__(self):
        self.packages = {}
        self.builds = {}
        self.repositories = {}
        self.entry_scripts = {}
        self.next_package_id = 1
        self.next_build_id = 1

    def add_package(self, name, version, source_url):
        package_id = self.next_package_id
        package = {
            'id': package_id,
            'name': name,
            'version': version, 
            'source_url': source_url
            
        }
        self.packages[package_id] = package
        self.next_package_id += 1
        return package_id
    
    def get_packages(self):
        return list(self.packages.values())
    
    