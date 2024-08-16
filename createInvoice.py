import mysql.connector
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from collections import defaultdict

item_counts = defaultdict(int)
# Clean up Checkout List
with open('RequestedItems.txt', 'r') as file:
    for line in file:
        parts = line.split('-')
        if parts:
                name = parts[0].strip()
                item_counts[name] += 1

RequestedItems = [{"name": key, "quantity": count} for key, count in item_counts.items()]

RequestedItemsName = [item['name'] for item in RequestedItems]
WhereQuery = ', '.join(['%s'] * len(RequestedItemsName))

# Connect to MySQL Database
conn = mysql.connector.connect(
    host="localhost",
    user="Daniel_Kondor",
    password="ZaqXsw321451!",
    database="cxml_database"
)
cursor = conn.cursor()

# Query to retrieve data
query = (f"""SELECT SupplierID, SupplierPartID, SupplierPartAuxiliaryID, ManufacturerPartId, ManufacturerName, description, UnitPrice, Currency, UnitOfMeasure, Classification, LeadTime, EffectiveDate 
               FROM products
               WHERE SupplierPartID IN ({WhereQuery})""")

cursor.execute(query, tuple(RequestedItemsName))
rows = cursor.fetchall()

# Create the root cXML element
cxml = ET.Element("cXML", attrib={"version": "1.2.008", "xml:lang": "en-US"})

# Create the Header
header = ET.SubElement(cxml, "Header")
ET.SubElement(header, "From").text = "Wurth Canada Limited"
ET.SubElement(header, "To").text = "Every Construction Company Ever"
ET.SubElement(header, "Sender", attrib={"SharedSecret": "YourSharedSecret"}).text = "YourSenderID"

# Create the Request element
request = ET.SubElement(cxml, "Request")
catalog = ET.SubElement(request, "Catalog")

# Loop through database records and create cXML elements
lineNumber = 1
for row in rows:
    item_out = ET.SubElement(catalog, "ItemOut", attrib={"quantity": str(RequestedItems[lineNumber - 1]), "lineNumber": str(lineNumber)})
    item_id = ET.SubElement(item_out, "ItemID")
    lineNumber += 1
    
    # Map database fields to cXML elements
    ET.SubElement(item_id, "SupplierPartID").text = str(row[1])
    ET.SubElement(item_id, "SupplierPartAuxiliaryID").text = str(row[2])
    
    item_detail = ET.SubElement(item_out, "ItemDetail")
    ET.SubElement(item_detail, "UnitPrice").text = str(row[6])
    ET.SubElement(item_detail, "Currency").text = row[7]
    ET.SubElement(item_detail, "Description").text = row[5]
    ET.SubElement(item_detail, "UnitOfMeasure").text = row[8]
    ET.SubElement(item_detail, "Classification").text = row[9]
    ET.SubElement(item_detail, "ManufacturerPartID").text = str(row[3])
    ET.SubElement(item_detail, "ManufacturerName").text = row[4]

# Convert the ElementTree to a string
xml_str = ET.tostring(cxml, encoding='utf-8').decode('utf-8')

# Use minidom to pretty-print the XML
xml_pretty_str = minidom.parseString(xml_str).toprettyxml(indent="    ")

# Print or save the pretty-printed XML
print(xml_pretty_str)

# Optionally, save to a file
with open("output_03.xml", "w") as f:
    f.write(xml_pretty_str)

# Close the database connection
cursor.close()
conn.close()
