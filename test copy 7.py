from bs4 import BeautifulSoup
import urllib.request as urllib

link = 'https://www.ndbc.noaa.gov/radial_search.php?lat1=0&lon1=0&uom=E&dist=9999&ot=A&time=1'
file = urllib.urlopen(link).read().decode('utf-8')    
print(file)

soup = BeautifulSoup(link, 'html.parser')
lines = soup.get_text().split('\n')
print(lines)