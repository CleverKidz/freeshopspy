import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote

# Page Configuration
st.set_page_config(
    page_title="FreeShopSpy - Shopify Analytics Tool",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    div.stButton > button:first-child {
        background-color: #2b6cb0;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛍️ FreeShopSpy")
st.subheader("The 100% Free Shopify & Dropshipping Research Tool")
st.write("Analyze competitors, find what they are testing, and spy on their ads.")

# User Input
target_url = st.text_input("Enter Shopify Store URL (e.g., https://colourpop.com):", "")

if target_url:
    # Clean URL helper
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "https://" + target_url
    target_url = target_url.rstrip('/')

    st.info(f"Analyzing: **{target_url}**...")

    try:
        # Fetching products.json
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        json_url = f"{target_url}/products.json?limit=100"
        response = requests.get(json_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])

            if len(products) > 0:
                st.success("Successfully connected to the Shopify store!")
                
                # --- DATA PROCESSING ---
                df_list = []
                for p in products:
                    # Get prices from variants
                    prices = [float(v['price']) for v in p['variants'] if 'price' in v]
                    avg_price = sum(prices)/len(prices) if prices else 0
                    
                    df_list.append({
                        "Title": p['title'],
                        "Category": p.get('product_type', 'N/A'),
                        "Price ($)": round(avg_price, 2),
                        "Created At": p['created_at'][:10] if 'created_at' in p else "N/A",
                        "Updated At": p['updated_at'][:10] if 'updated_at' in p else "N/A",
                        "Handle": p['handle'],
                        "Image": p['images'][0]['src'] if p.get('images') else None
                    })
                
                df = pd.DataFrame(df_list)

                # --- METRICS PANEL ---
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="Products Analyzed (Max 100)", value=len(df))
                with col2:
                    st.metric(label="Average Product Price", value=f"${round(df['Price ($)'].mean(), 2)}")
                with col3:
                    st.metric(label="Latest Product Uploaded", value=df['Created At'].iloc[0])

                # --- ACTIONS & BYPASS LINKS ---
                st.markdown("### ⚡ Quick Spy Actions")
                c1, c2 = st.columns(2)
                with c1:
                    best_seller_url = f"{target_url}/collections/all?sort_by=best-selling"
                    st.link_button("🔥 Open Competitor's Best Sellers", best_seller_url)
                with c2:
                    # Look up store on Meta Ad Library
                    domain_name = target_url.replace("https://", "").replace("http://", "").replace("www.", "")
                    meta_ad_url = f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all&q={domain_name}&search_type=keyword"
                    st.link_button("📢 View Active Facebook Ads", meta_ad_url)

                # --- PRODUCT TABLE & RESEARCH ---
                st.markdown("### 📦 Product Catalog (Newest First)")
                st.write("These are the products the store is currently running or testing:")

                # Render Table with Image Previews
                for index, row in df.iterrows():
                    with st.container():
                        p_col1, p_col2, p_col3 = st.columns([1, 3, 2])
                        with p_col1:
                            if row['Image']:
                                st.image(row['Image'], width=100)
                            else:
                                st.write("No Image")
                        with p_col2:
                            st.markdown(f"**{row['Title']}**")
                            st.write(f"Price: **${row['Price ($)']}** | Category: {row['Category']}")
                            st.write(f"Added on: {row['Created At']}")
                        with p_col3:
                            # Generate sourcing/spying links
                            encoded_title = quote(row['Title'])
                            ali_url = f"https://www.aliexpress.com/wholesale?SearchText={encoded_title}"
                            tiktok_url = f"https://www.tiktok.com/search?q={encoded_title}"
                            
                            st.link_button(f"🔍 Find on AliExpress", ali_url)
                            st.link_button(f"🎵 Search TikTok Ads", tiktok_url)
                        st.markdown("---")

            else:
                st.warning("Connected, but no products were found. The store might have hidden its product list.")
        else:
            st.error("Could not read data from this store. This might not be a Shopify store, or they have blocked access.")
    except Exception as e:
        st.error(f"Error accessing the store: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>FreeShopSpy - Built for the Dropshipping Community</p>", unsafe_allow_html=True)
