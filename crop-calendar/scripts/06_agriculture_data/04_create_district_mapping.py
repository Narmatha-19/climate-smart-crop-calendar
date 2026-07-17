import pandas as pd
import os

# ==========================================
# DISTRICT MAPPING
# ==========================================

mapping = {

    "Ariyalur":"Ariyalur",
    "Chengalpattu":"Kanchipuram",
    "Chennai":"Chennai",
    "Coimbatore":"Coimbatore",
    "Cuddalore":"Cuddalore",
    "Dharmapuri":"Dharmapuri",
    "Dindigul":"Dindigul",
    "Erode":"Erode",
    "Kallakurichi":"Villupuram",
    "Kancheepuram":"Kanchipuram",
    "Kanyakumari":"Kanniyakumari",
    "Karur":"Karur",
    "Krishnagiri":"Krishnagiri",
    "Madurai":"Madurai",
    "Mayiladuthurai":"Nagapattinam",
    "Nagapattinam":"Nagapattinam",
    "Namakkal":"Namakkal",
    "Nilgiris":"The Nilgiris",
    "Perambalur":"Perambalur",
    "Pudukkottai":"Pudukkottai",
    "Ramanathapuram":"Ramanathapuram",
    "Ranipet":"Vellore",
    "Salem":"Salem",
    "Sivagangai":"Sivaganga",
    "Tenkasi":"Tirunelveli",
    "Thanjavur":"Thanjavur",
    "Theni":"Theni",
    "Thoothukudi":"Thoothukudi",
    "Tiruchirappalli":"Tiruchirappalli",
    "Tirunelveli":"Tirunelveli",
    "Tirupathur":"Vellore",
    "Tiruppur":"Tiruppur",
    "Tiruvallur":"Thiruvallur",
    "Tiruvannamalai":"Tiruvannamalai",
    "Tiruvarur":"Thiruvarur",
    "Vellore":"Vellore",
    "Viluppuram":"Villupuram",
    "Virudhunagar":"Virudhunagar"
}

df = pd.DataFrame(

    mapping.items(),

    columns=[

        "Climate_District",

        "Agriculture_District"

    ]

)

OUTPUT = "../../dataset/final"

os.makedirs(OUTPUT,exist_ok=True)

file = os.path.join(

    OUTPUT,

    "district_mapping.csv"

)

df.to_csv(

    file,

    index=False

)

print("="*60)

print("DISTRICT MAPPING CREATED")

print("="*60)

print(df)

print("\nSaved :",file)