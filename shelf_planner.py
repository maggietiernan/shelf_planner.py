import streamlit as st
import pandas as pd
import numpy as np
import re
import time
import requests
import base64  # added for download link

# ---- Branding ----
col1, col2 = st.columns([1, 1])
with col1:
    st.image("logo.png", width=200)

st.markdown("""
    <div style="background-color:#f0f4f8;padding:20px;border-radius:10px;margin-top:10px;">
        <h1 style="color:#2c3e50;text-align:center;">📊 Smart Shelf Planner</h1>
        <p style="text-align:center;font-size:18px;">
            Organize your coolers or shelf space using real sales data.<br>
            Visually plan with logic — boost efficiency and sales.
        </p>
    </div>
    <hr>
""", unsafe_allow_html=True)

st.info("Upload your sales report(s) below to begin planning your shelf layout!")

if "start" not in st.session_state:
    st.session_state.start = False

if not st.session_state.start:
    if st.button("🚀 Get Started"):
        st.session_state.start = True
    st.stop()

uploaded_files = st.file_uploader("Upload your sales report(s) (Excel or CSV)", type=["xlsx", "csv"], accept_multiple_files=True)

# linking Github pictures to page
GITHUB_USERNAME = "maggietiernan"
REPO_NAME = "shelf_images"
BRANCH = "main"
FILLER_IMAGE = "filler.png"

#filtering products into categories
CATEGORY_FILTERS = {
    "Fridge – Alcoholic Beverages": [
        "C-NUTRLORANGE23", "C-BLSELTZBCHRY25", "C-MICHULTRA16OZ", "C-MICHULTRA25OZ",
        "C-BUD LIGHT 25OZ", "C-BUSCH LIGHT 25", "C-BUDWEISER 25OZ", "C-BUD LIGHT 16OZ",
        "C-BUDWEISER 16OZ", "C-BUSCHLIGHT16OZ", "C-SUMMERSHANDY16", "C-GOOSEBEERHUG16",
        "C-YUENGLING 16OZ", "C-KONAWAVE25OZ", "C-RHINETRUTH16OZ", "C-CUTWTRLIMEMARG",
        "C-NUTRLPINEAP23", "C-NUTRLWATRMLN23", "C-ANGRYORCHARD16", "C-GOLDENROADMAGC",
        "C-SKIMMER HALF16", "C-GAVEL BANGER", "C-SKIMMERS IT16", "C-GARAGE 16 OZ",
        "C-STELLA 16 OZ", "C-50WHARDLEM16OZ", "C-CORONA 16 OZ", "C-HAPTHURSTRAW16",
        "C-HOOPTEA 16 OZ", "C-LITTLEKING16", "C-MODELO 16 OZ", "C-NUTRLWTRMLN12",
        "C-LOSTIES 16OZ", "C-50WDOOM 16 OZ", "C-DEADRED16OZ", "C-CUTWTRMANGOMAR",
        "C-CUTWTRVDKAMAI", "C-50WEASTCOAST16", "C-HUDYDELIGHT16", "C-STELLA 25 OZ", 
        "C-CUTWATERLONGIS", "C-50WPEACH12OZ", "C-AMERICANLAGER", "C-50WPINE12OZ", 
        "C-50WESTCOAST", "C-50WESTSTAMBER", "C-GARAGELIME16", "C-NUTRLSTRAW12", 
        "C-PACIFICO 16 OZ", "C-NUTRLLIME12", "C-MADPSYCHO16", "C-CORONAPREM16OZ", 
        "C-KONAWAVE16OZ", "C-BLUEMOON 16OZ", "C-BRAXBLUE16"
    ],
    "Fridge – Non-Alcoholic Beverages": [
        "C-COKE", "C-COKE ZEROSUGAR", "C-POWERADE BLAST", "C-DIET COKE",
        "C-SPRITE", "C-PINK LEMONADE", "C-LEMONADE", "C-FANTA ORANGE",
        "C-CHERRY COKE", "C-FRUIT PUNCH", "C-SWEET TEA", "C-MONSTER ZERO",
        "C-POWERADE RED", "C-TUM-E BERRY", "C-TUM-E FRUIT PN", "C-MONSTERREGULAR",
        "C-PWRDEZEROFRUIT", "C-PWRDEZEROMXBRY", "C-VITAMINWTRLEMO", "C-VITAMINWTRACAI",
        "C-REDS WATER", "C-SMARTWTRLITER", "C-SMARTWATER", "C-DASANI 20 OZ", "C-RED CREME SODA", 
        "C-BA PEACHMANGO", "C-BA STRAWBANANA", "C-BA FRUIT PUNCH"
    ],
    "Shelf – Snacks/Other": [
        "C-COTTON CANDY", "C-NERDS RAINBOW",
        "C-SWEETARTS BOX", "C-SWEETARTSCHEWY", "C-WATERMELON SP", "C-SWEDISHASSORT",
        "C-AIRHEADS 6 BAR", "C-SOUR PATCH KID", "C-MIKE&IKE FRUIT", "C-PEANUTS",
        "C-GRIPPOSPLAIN", "C-GRIPPOSRCREAM", "C-GRIPPOCAROLINA",
        "C-GRIPPOSMAUI", "C-SKITTLESBOX", "C-BEER BAT", "C-KOOZIE 24 OZ", "C-KOOZIE 16 OZ", 
        "C-SWEETART ROPE", "C-M&M BOX", "C-TWIZZLERSTRW", "C-SWEETARTSCHROP", "C-NERDS CLUSTERS", 
        "C-SNICKERS", "C-SWEDISH FISH", "C-AIRHEADEXTREME", "C-NIBS CHERRY", "C-OREOS MINIS", 
        "C-TROLLISOURCRAW",  "C-TWIZCHERRY", "C-TWIZZLER GUM", "C-KIT KAT", "C-PEANUT M&M BOX", 
        "C-BLFORGUMYBEAR", "C-TROLLISCBURST", "C-LIFESAVE GUM", "C-BABYRUTH", "C-HERSHEY DARK", 
        "C-GRANDMACOOKIE", "C-BLFORGUMYWORMS", "C-LIFESAVE WB", "C-NERDGUMMYCLUST", 
        "C-NUTTER BUTTER", "C-SKIT GUM WB", "C-SKIT SOUR GUM","C-HOT TAMALES", "C-GRANDMA PB", 
        "C-HERSHEY ALMOND", "C-REESE'S STICK", "C-MENTOSMIXFRUIT", "C-CHIPSAHOYMINI", 
        "C-LIFESAVE HC", "C-LIFESAVER COLL", "C-RITZBITSCHEESE", "C-SWEETARTS CHEW", 
        "C-REESEFASTBREAK", "C-REESESPBBIGCUP", "C-SNICKERS PB", "C-MENTOSROLLMINT", "C-CASHEWS", 
        "C-ALMONDS", "C-MIXEDFRUITNUTS", "C-CHEETOS XVL", "C-CHEETOSFLAMINH", "C-RUFFLESCHEDDAR", 
        "C-DORITOS NACHO", "C-DORITOS COOL R", "C-LAYSBBQ", "C-PRETZELCRISPS", "C-PRETZELCRISPBF", 
        "C-SNYDER MINI FF", "C-PRETZELBUFF5OZ", "C-FOAM FINGER", "C-PLUSH ROSIE", "C-BALL REDS LOGO", 
        "C-MINIBATRED", "C-PLUSH GAPPER", "C-BALL 4 IN SOFT", "C-MINIBATNATURAL", "C-SUNSCREEN", 
        "C-TYLENOL EXTRA", "C-CLARITIN", "C-DAYQUIL"
    ]
}

# ensure pictures are the fully updated version
def get_image_url(product_name):
    timestamp = str(int(time.time()))
    safe_name = re.sub(r'\W+', '_', product_name) + ".png"
    url = f"https://cdn.jsdelivr.net/gh/{GITHUB_USERNAME}/{REPO_NAME}@{BRANCH}/{safe_name}?nocache={timestamp}"
    try:
        response = requests.head(url)
        if response.status_code == 200:
            return url
        else:
            fallback_url = f"https://cdn.jsdelivr.net/gh/{GITHUB_USERNAME}/{REPO_NAME}@{BRANCH}/{FILLER_IMAGE}?nocache={timestamp}"
            return fallback_url
    except:
        return f"https://cdn.jsdelivr.net/gh/{GITHUB_USERNAME}/{REPO_NAME}@{BRANCH}/{FILLER_IMAGE}?nocache={timestamp}"


# We will create this dict after loading df
# turning html tag to image and label
product_to_url = {}

def image_only_tag(product_name):
    url = product_to_url.get(product_name, get_image_url(product_name))
    return f'<img src="{url}" width="60" height="60" style="object-fit:contain;">'

def image_tag_with_label(product_name):
    url = product_to_url.get(product_name, get_image_url(product_name))
    return f'<img src="{url}" width="60" height="60" style="object-fit:contain;"><br><small>{product_name}</small>'

# --- Main logic ---

#uploading file(s) and set up logic
if uploaded_files:
    combined_df = pd.DataFrame()
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".csv"):
            preview = pd.read_csv(uploaded_file, header=None, nrows=200)
        else:
            preview = pd.read_excel(uploaded_file, sheet_name=0, header=None, nrows=200)

        header_row = None
        for i in range(len(preview)):
            row = preview.iloc[i].astype(str).str.lower()
            if any(x in row.values for x in ["name", "description"]) and any(x in row.values for x in ["quantity sold", "sold units"]):
                header_row = i
                break

        if header_row is None:
            st.error("Header row with required fields not found.")
            st.stop()

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, header=header_row)
        else:
            df = pd.read_excel(uploaded_file, sheet_name=0, header=header_row)

        df.columns = df.columns.str.strip()
        name_col = next((col for col in df.columns if col.lower() in ["name", "description"]), None)
        quantity_col = next((col for col in df.columns if col.lower() in ["quantity sold", "sold units"]), None)

        if name_col is None or quantity_col is None:
            st.error(f"Missing required columns in {uploaded_file.name}.")
            st.stop()

        df = df.rename(columns={name_col: "Product Name", quantity_col: "Units Sold"})
        df = df[df["Product Name"].astype(str).str.startswith("C-")]
        df = df.dropna(subset=["Product Name", "Units Sold"])
        df["Units Sold"] = pd.to_numeric(df["Units Sold"], errors='coerce')
        df = df.dropna(subset=["Units Sold"])
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Now we have combined_df with all data
    # Group by product name and sum units sold
    df = combined_df.groupby("Product Name", as_index=False).agg({"Units Sold": "sum"})

    # Check for the cache busted URL column
    # We look for a column with a name close to 'Image URL CacheBusted' ignoring case and spaces
    url_col_candidates = [col for col in combined_df.columns if re.sub(r'\W+', '', col).lower() == 'imageurlcachebusted']
    if url_col_candidates:
        url_col = url_col_candidates[0]
        # Create mapping from Product Name to cache busted URL, first get from combined_df (before groupby)
        # But combined_df is already grouped - so get from original data:
        # We use combined_df before groupby if possible, else use combined_df itself
        # Safer: Use combined_df before grouping: actually we stored it in combined_df, so we can:
        product_to_url_map_df = combined_df.drop_duplicates(subset=["Product Name"])
        product_to_url = dict(zip(product_to_url_map_df["Product Name"], product_to_url_map_df[url_col]))
    else:
        # If no column found, generate dynamically
        product_to_url = {name: get_image_url(name) for name in df["Product Name"]}

    display_type = st.sidebar.selectbox("Display Type", list(CATEGORY_FILTERS.keys()))
    filtered_df = df[df["Product Name"].apply(lambda name: any(name.startswith(prefix) for prefix in CATEGORY_FILTERS[display_type]))]

    # --- Manual product addition: initialize session_state list if missing ---
    if "manual_products" not in st.session_state:
        st.session_state.manual_products = []

    # Sidebar inputs below fridge/shelf inputs
    if "Fridge" in display_type:
        num_fridges = st.sidebar.number_input("Fridge Doors", min_value=1, value=6)
        rows_per_fridge = st.sidebar.number_input("Rows per Door", min_value=1, value=5)
        slots_per_row = st.sidebar.number_input("Slots per Row", min_value=1, value=6)
    else:
        num_fridges = st.sidebar.number_input("Number of Shelves", min_value=1, value=5)
        rows_per_fridge = st.sidebar.number_input("Vertical Levels", min_value=1, value=4)
        slots_per_row = st.sidebar.number_input("Slots per Shelf", min_value=1, value=6)

    # Manual product input UI
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ➕ Add New Product")
    new_product_name = st.sidebar.text_input("Product Name (must start with 'C-')", key="new_product_name")
    new_units_sold = st.sidebar.number_input("Units Sold", min_value=0, value=0, step=1, key="new_units_sold")

    if st.sidebar.button("Add Product"):
        if not new_product_name.startswith("C-"):
            st.sidebar.error("Product Name must start with 'C-'")
        elif any(p["Product Name"] == new_product_name for p in st.session_state.manual_products) or new_product_name in df["Product Name"].values:
            st.sidebar.error("Product already exists.")
        else:
            try:
                st.session_state.manual_products.append({"Product Name": new_product_name, "Units Sold": new_units_sold})
                st.sidebar.success(f"Added {new_product_name} with {new_units_sold} units sold")
                # Clear inputs by resetting keys
                st.session_state.new_product_name = ""
                st.session_state.new_units_sold = 0
                st.experimental_rerun()
            except Exception as e:
                st.sidebar.error(f"Error adding product: {e}")

    # Combine manual products with filtered products
    manual_df = pd.DataFrame(st.session_state.manual_products)
    if not manual_df.empty:
        filtered_df = pd.concat([filtered_df, manual_df], ignore_index=True)

    all_products = filtered_df["Product Name"].tolist()
    selected_products = st.multiselect("Select products:", all_products, default=all_products)
    df = filtered_df[filtered_df["Product Name"].isin(selected_products)]

    if df.empty:
        st.warning("No products selected.")
        st.stop()

    df = df.sort_values("Units Sold", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1

    total_slots = num_fridges * rows_per_fridge * slots_per_row
    total_units = df["Units Sold"].sum() if df["Units Sold"].sum() > 0 else 1  # avoid division by zero
    df["Weight"] = df["Units Sold"] / total_units
    df["Slots"] = (df["Weight"] * total_slots).round().astype(int)
    df.loc[df["Slots"] < 1, "Slots"] = 1

    max_slots_per_product = 2 * rows_per_fridge * slots_per_row
    df["Slots"] = df["Slots"].clip(upper=max_slots_per_product)

    while df["Slots"].sum() < total_slots:
        for i in df.index:
            if df["Slots"].sum() < total_slots and df.at[i, "Slots"] < max_slots_per_product:
                df.at[i, "Slots"] += 1

    while df["Slots"].sum() > total_slots:
        for i in df.index:
            if df["Slots"].sum() > total_slots and df.at[i, "Slots"] > 1:
                df.at[i, "Slots"] -= 1

    layout_grid = np.full((num_fridges, rows_per_fridge, slots_per_row), "(Empty)", dtype=object)

    #shelf logic
    center_fridge = num_fridges // 2
    center_row = rows_per_fridge // 2
    fridge_order = sorted(range(num_fridges), key=lambda x: abs(x - center_fridge))
    row_order = [center_row]
    for offset in range(1, rows_per_fridge):
        if center_row - offset >= 0:
            row_order.append(center_row - offset)
        if center_row + offset < rows_per_fridge:
            row_order.append(center_row + offset)

    slot_positions = []
    for f in fridge_order:
        for r in row_order:
            for s in range(slots_per_row):
                slot_positions.append((f, r, s))

    slot_index = 0
    for _, row in df.iterrows():
        product = row["Product Name"]
        slots_needed = row["Slots"]
        for _ in range(slots_needed):
            if slot_index >= len(slot_positions):
                break
            f, r, s = slot_positions[slot_index]
            layout_grid[f, r, s] = product
            slot_index += 1

    st.subheader("Shelf Layout Suggestion (Visual)")
    td_style = "padding:5px;text-align:center;width:70px;height:70px;border:1px solid #ddd;vertical-align:middle;"

    #shelf/fridge display
    for f in range(num_fridges):
        if display_type == "Shelf – Snacks/Other":
            st.markdown(f"### 🍿 Snack Rack {f + 1}")
        else:
            st.markdown(f"### 🧊 Fridge Door {f + 1}")
        html = '<table style="border-collapse: collapse;">'
        for r in range(rows_per_fridge):
            html += '<tr>'
            for s in range(slots_per_row):
                product = layout_grid[f, r, s]
                html += f'<td style="{td_style}">{image_tag_with_label(product)}</td>'
            html += '</tr>'
        html += '</table>'
        st.markdown(html, unsafe_allow_html=True)

    st.subheader("Quick Visual Overview")
    thumb_html = '<div style="display:flex;gap:2px;flex-wrap:nowrap;overflow-x:auto;">'
    for f in range(num_fridges):
        thumb_html += '<div style="display:inline-block;border:1px solid #ccc;padding:2px;">'
        thumb_html += '<table style="border-spacing:0;border-top:2px solid #aaa;">'
        for r in range(rows_per_fridge):
            thumb_html += '<tr style="border-bottom:2px solid #aaa;">'
            for s in range(slots_per_row):
                product = layout_grid[f, r, s]
                thumb_html += f'<td style="padding:2px;text-align:center;">{image_only_tag(product)}</td>'
            thumb_html += '</tr>'
        thumb_html += '</table></div>'
    thumb_html += '</div>'
    st.markdown(thumb_html, unsafe_allow_html=True)

    # download button for Quick Visual Overview
    def get_download_link(html_str, filename="quick_visual_overview.html"):
        b64 = base64.b64encode(html_str.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}">📥 Download Quick Visual Overview (HTML)</a>'
        return href

    st.markdown(get_download_link(thumb_html), unsafe_allow_html=True)

    st.subheader("Product Rankings & Slot Allocation")
    st.dataframe(df[["Product Name", "Units Sold", "Rank", "Slots"]])

else:
    st.info("Please upload at least one sales report to continue.")
