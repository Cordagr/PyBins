class PackageWheel:
    name = " ", 
    version = " ",
    wheel_path = " " ,
    author = " ",
    description = " ",
    url = " ",


    def __init__(self, name, version, wheel_path, author="", description="", url=""):
        self.name = name
        self.version = version
        self.wheel_path = wheel_path
        self.author = author
        self.description = description
        self.url = url

