
def amazon_formatter(df):
    df = manufacturer_to_brand(df)
    # drop the col "location" from df
    try:
        df = df.drop(columns = ["location"])
    except Exception as e:
        print(e)
    
    """
    # split the review_title column by "stars" and keep everything after first stars
    try:
        df["review_title"] = df["review_title"].str.split("stars", n = 1, expand = True)[1]
    except Exception as e:
        print(e)
        
    
    # remove leading and trailing whitespace from review_title
    df["review_title"] = df["review_title"].str.strip()
    """
    
    df = add_key_col(df)
    return df


def bestbuy_formatter(df):
    df = manufacturer_to_brand(df)
    # drop the col "owned_for_x_when_reviewed" from df
    try:
        df = df.drop(columns = ["owned_for_x_when_reviewed"])
    except Exception as e:
        print(e)
    
    df = add_key_col(df)
    return df


def costco_formatter(df):
    df = manufacturer_to_brand(df)
    # in the col verified_purchase_badge, replace "Verified Purchaser" with "Verified Purchase"
    df["verified_purchase_badge"] = df["verified_purchase_badge"].str.replace("Verified Purchaser", "Verified Purchase") 
    df = add_key_col(df)
    return df


def homedepot_formatter(df):
    df = manufacturer_to_brand(df)
    df["Model No."] = df["Model No."].str.replace("Model# ", "")
    for index, row in df.iterrows():
        try:
            if row["recommended"] == "Recommended":
                df.at[index, "recommended"] = "yes"
        except Exception as e:
            print(e)
            if row["review_recommended"] == "Recommended":
                df.at[index, "review_recommended"] = "yes"
    
    try:
        df = df.rename(columns = {"review_recommended": "recommended"})
    except Exception as e:
        print(e)         
    # rename the Price $ to Price
    df = df.rename(columns = {"Price $": "Price"})
    df = add_key_col(df)
    return df
    
    
def lowes_formatter(df):
    df = manufacturer_to_brand(df)
    for index, row in df.iterrows():
        try:
            df.at[index, "original_review_syndication"] = str(row["original_review_syndication"]).split(" | ")[0]
        except Exception as e:
            print(e)
    df = add_key_col(df)
    return df
        

def walmart_formatter(df):
    df = manufacturer_to_brand(df)
    
    # replace nan with ""
    df["verified_purchase_badge"] = df["verified_purchase_badge"].fillna("")
    
    #convert column to str
    df["verified_purchase_badge"] = df["verified_purchase_badge"].astype(str)
    df["verified_purchase_badge"] = df["verified_purchase_badge"].str.replace("Verified Purchaser", "Verified Purchase")
    
    
    df = add_key_col(df)
    return df
    
    
def homedepot_ca_formatter(df):
    df = manufacturer_to_brand(df)
    
    # in the col verified_purchase_badge, replace "Verified Purchaser" with "Verified Purchase"
    df["verified_purchase_badge"] = df["verified_purchase_badge"].str.replace("Verified Purchaser", "Verified Purchase")
    
    # replace the recommended with yes and no
    for index, row in df.iterrows():
        if row["recommended"] == "I do not recommend this product.":
            df.at[index, "recommended"] = "no"
        if row["recommended"] == "I recommend this product.":
            df.at[index, "recommended"] = "yes"
    df = add_key_col(df)
    return df


def lowes_ca_formatter(df):
    df = manufacturer_to_brand(df)
    
    # get rid of "MFR#: " in Model No.
    df["Model No."] = df["Model No."].str.replace("MFR#: ", "")
    
    # get rid of "Item#: " in sku
    df["sku"] = df["sku"].str.replace("Item#: ", "")
    
    for index, row in df.iterrows():
        if "Recommends this product" in str(row["recommended"]):
            if " Yes " in row["recommended"]:
                df.at[index, "recommended"] = "yes"
            if " No " in row["recommended"]:
                df.at[index, "recommended"] = "no"
        else:
            df.at[index, "recommended"] = ""
            
    df = add_key_col(df)
    return df
    
    
def walmart_ca_formatter(df):
    df = manufacturer_to_brand(df)
    
    df["verified_purchase_badge"] = df["verified_purchase_badge"].str.replace("Verified Purchaser", "Verified Purchase")
    
    df = add_key_col(df)
    return df
    
    
def homehardware_ca_formatter(df):
    df = manufacturer_to_brand(df)
    
    # drop the cols "city", "quality", "value", "durability", "level_of_experience"
    df = df.drop(columns = ["city", "quality", "value", "durability", "level_of_experience"])
    
    df = add_key_col(df)
    return df
    
    
def rona_ca_formatter(df):
    df = manufacturer_to_brand(df)
    
    # drop the cols "city", "quality", "value", "level_of_experience"
    df = df.drop(columns = ["city", "quality", "value", "level_of_experience"])
    df = add_key_col(df)
    return df


def canadian_tire_ca_formatter(df):
    df = manufacturer_to_brand(df)
    
    # in the col "sku", replace instances of "#" with ""
    df["sku"] = df["sku"].str.replace("#", "")
    
    # in the col "verified_purchase_badge", replace "Verified Purchaser" with "Verified Purchase"
    df["verified_purchase_badge"] = df["verified_purchase_badge"].str.replace("Verified Purchaser", "Verified Purchase")
    
    # in the col "verified_purchase_badge", delete any text that does not say "Verified Purchase"
    for index, row in df.iterrows():
        if row["verified_purchase_badge"] != "Verified Purchase":
            df.at[index, "verified_purchase_badge"] = ""
        if row["recommended"] == "I do not recommend this product.":
            df.at[index, "recommended"] = "no"
        if row["recommended"] == "I recommend this product.":
            df.at[index, "recommended"] = "yes"
    
    df = add_key_col(df)
    return df


def manufacturer_to_brand(df):
    try:
        df = df.rename(columns={"Manufacturer": "Brand"})
    except Exception as e:
        print(e)
    
    return df

def add_key_col(df):
    key_list = []
    for index, row in df.iterrows():
        #print(row)
        # get the month_year of row[review_date]
        month_year = str(row["review_date"].month) + "_" + str(row["review_date"].year)
        
        #change back to manufacturer
        brand_formated = str(row["Brand"])
        try:
            if brand_formated != "":
                brand_formated = brand_formated.lower().strip()
        except Exception as e:
            print(e)
            
        title_formated = str(row["review_title"])
        try:
            if title_formated != "":
                title_formated = title_formated.lower().strip()
                title_formated = title_formated.replace(" ", "").replace("\n", "").replace("\t", "")
        except Exception as e:
            print(e)
            
        review_text_formated = str(row["review_text"])
        try:
            if review_text_formated != "":
                review_text_formated = review_text_formated.lower().strip()
                # remove all whitespace
                review_text_formated = review_text_formated.replace(" ", "").replace("\n", "").replace("\t", "")
        except Exception as e:
            print(e)
            
            
        key = sha256((str(brand_formated) + str(month_year) + str(row["star_rating"]) + str(title_formated) + str(review_text_formated)).encode("utf-8"))
        key_list.append(key)
    
    df.insert(loc=0, column="Key", value=key_list)
    return df

import hashlib
def sha256(s):
    m = hashlib.sha256()
    m.update(s)
    return m.hexdigest()