import urllib.request
import gzip

def getFTP(link):
    name = link.split('/')
    # Local path where you want to save the downloaded file
    local_filename = r"C:\Users\deela\Downloads\\" + name[-1]

    # Download the file from the FTP server
    urllib.request.urlretrieve(link, local_filename)

    print(f"File '{local_filename}' downloaded successfully.")

def getGRIB(link, title = None):
    if title == None:
        name = link.split('/')
        # Local path where you want to save the downloaded file
        local_filename = r"C:\Users\deela\Downloads\\" + name[-1]
    else:
        local_filename = r"C:\Users\deela\Downloads\\" + title
        
    # Download the file from the FTP server
    urllib.request.urlretrieve(link, local_filename)

    print(f"File '{local_filename}' downloaded successfully.")

    return local_filename

def getGZ(file, newFile = None):
    if newFile is None:
        newFile = file[:-3]
        
    with gzip.open(file, 'rb') as f:
        with open(newFile, 'wb') as nf:
            # print(f'File {file} opened successfully.')
            nf.write(f.read())
    
    return newFile
    
#getFTP('ftp://ftp.ifremer.fr/ifremer/argo/dac/coriolis/6902919/profiles/R6902919_183.nc')

