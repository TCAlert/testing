import urllib.request

def getFile(link):
    name = link.split('/')
    # Local path where you want to save the downloaded file
    local_filename = r"C:\Users\deela\Downloads\\" + name[-1]

    # Download the file from the FTP server
    urllib.request.urlretrieve(link, local_filename)

    print(f"File '{local_filename}' downloaded successfully.")

getFile('ftp://ftp.ifremer.fr/ifremer/argo/dac/coriolis/6902919/profiles/R6902919_183.nc')