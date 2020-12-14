import pdftotext

with open("ME Sr R 2020 03 08.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)

for page in pdf:
    for line in page.split("\n"):
        print(line)