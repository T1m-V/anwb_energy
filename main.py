from bs4 import BeautifulSoup
from selenium import webdriver

from func_file_ut import save_file

url = "https://energie.anwb.nl/actuele-tarieven"
print("URL : %s" % url)

driver = webdriver.Chrome()
driver.get(url)

html = driver.page_source
soup = BeautifulSoup(html)

print(soup)
save_file("html.txt", soup.prettify())
