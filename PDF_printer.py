import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

FILES_TO_SCAN = ["RIP_daemon.py"]  # List of files to include
DIRECTORIES_TO_SCAN = ["cosc364-assignment-1"]  # List of directories to include

# PDF setup
pdf_filename = "project_code.pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
margin = inch * 0.5
line_height = 10
max_lines_per_page = int((height - 2 * margin) / line_height)
font_name = "Courier"
font_size = 8

c.setFont(font_name, font_size)


def add_title(title):
    global y
    if y < margin + line_height:
        c.showPage()
        c.setFont(font_name, font_size)
        y = height - margin
    c.setFillColor(colors.darkblue)
    c.setFont("Courier-Bold", 12)
    c.drawString(margin, y, title)
    c.setFont(font_name, font_size)
    c.setFillColor(colors.black)
    y -= line_height


def write_code(filepath):
    global y
    c.showPage()
    c.setFont(font_name, font_size)
    y = height - margin
    if "init" in filepath:
        return
    add_title(f"File: {filepath}")
    with open(filepath, "r") as f:
        for line in f:
            line = line.rstrip()
            if y < margin + line_height:
                c.showPage()
                c.setFont(font_name, font_size)
                y = height - margin
            c.drawString(margin, y, line[:150])  # limit line width
            y -= line_height


def scan_directory(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for file in sorted(files):
            if file.endswith(".py"):
                write_code(os.path.join(root, file))


# Start writing PDF
y = height - margin

# Write individual files
for file in FILES_TO_SCAN:
    if os.path.exists(file):
        write_code(file)

# Write whole directories
for directory in DIRECTORIES_TO_SCAN:
    scan_directory(directory)

# Save the PDF
c.save()
print(f"PDF saved as {pdf_filename}")