import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(
    page_title="EcoRoot AI",
    page_icon="🌱",
    layout="wide"
)

if "lang" not in st.session_state:
    st.session_state.lang = "English"

with st.sidebar:
    st.markdown("### Language / ভাষা")
    st.session_state.lang = st.radio(
        "Select Language",
        ["English", "বাংলা"],
        index=0 if st.session_state.lang == "English" else 1,
        label_visibility="collapsed"
    )

UI = {
    "English": {
        "title": "🌱 Biofertilizer & Crop Compatibility Engine",
        "sub": "Deterministic Soil & Safety Screening + Gemini AI Formulation",
        "s1": "1. Crops & Bio-Waste Inputs",
        "target_cat": "Crop Category",
        "target_crops": "Select Target Crop(s) (Pick 2+ to check companion planting)",
        "scrap_cat": "Farm Residue Category (Optional)",
        "scrap_crops": "Select Crop Residue",
        "kitchen_mat": "Kitchen & Garden Waste",
        "other_in": "Other waste items (e.g., banana peel, cooked chicken bones, tea leaves)",
        "s2": "2. Deterministic Safety Guardrails",
        "safe_err": "BIOHAZARD BLOCKED ({items}): Raw animal waste, dairy, oils, and synthetics breed pathogens. Remove to continue.",
        "bone_warn": "Thermal Pre-Processing Needed: Cooked bones detected. Do not steep in water. Boil off oil/salt -> char at high heat -> crush to powder.",
        "s3": "3. Multi-Crop Compatibility Engine",
        "no_crop": "Please select at least one target crop above.",
        "conflict_hdr": "Crop Compatibility Conflict",
        "rescue_msg": "Rescue Plan: Use root partitioning (separate grow-bags/beds) and spot-feeding.",
        "ph_disjoint": "pH Mismatch! Selected crops have non-overlapping pH needs ({low:.1f} vs {high:.1f}). Plant in separate containers.",
        "s4": "4. Soil pH Calibration",
        "soil_mode": "Calibration Method",
        "modes": [
            "Known Soil pH (Lab/Meter)",
            "Vinegar & Baking Soda Fizz Test",
            "Unknown Soil (Safe-Mode: pH 6.5 + 1:10 Dilution)"
        ],
        "ph_num": "Soil pH Value",
        "vinegar_q": "1. Does soil fizz with Vinegar?",
        "soda_q": "2. Does soil fizz with Baking Soda + Water?",
        "yes_no": ["No", "Yes"],
        "triage_alk": "Result: Alkaline Soil (~pH 7.8). Formulation will add mild organic acidifiers.",
        "triage_acid": "Result: Acidic Soil (~pH 5.2). Formulation will buffer excess acidity.",
        "triage_neut": "Result: Neutral Soil (~pH 6.5).",
        "safemode_info": "Safe-Mode Active: Assuming pH 6.5 with mandatory 1:10 dilution buffer.",
        "ph_warn_low": "Soil pH ({ph}) is too acidic for target window ({low:.1f}–{high:.1f}).",
        "ph_warn_high": "Soil pH ({ph}) is too alkaline for target window ({low:.1f}–{high:.1f}).",
        "s5": "5. Visual Action Card",
        "gen_btn": "Generate Biofertilizer Protocol",
        "no_scrap": "Select or type at least one waste material in Step 1.",
        "spinner": "Generating custom agronomy protocol via Gemini AI...",
        "badge_safe": "VERIFIED SAFE & COMPATIBLE",
        "badge_rescue": "RESCUE MODE (PARTITIONING + 1:10 BUFFER)"
    },
    "বাংলা": {
        "title": "🌱 সমন্বিত জৈব সার ও ফসল সামঞ্জস্যতা ইঞ্জিন",
        "sub": "নিরাপত্তা যাচাই + Gemini AI কৃষিবিদ ফর্মুলেশন",
        "s1": "১. ফসল ও জৈব-বর্জ্য ইনপুট",
        "target_cat": "ফসলের বিভাগ",
        "target_crops": "লক্ষ্য ফসল নির্বাচন করুন (সহ-চাষ যাচাই করতে একাধিক বাছুন)",
        "scrap_cat": "ফসলের বর্জ্যের বিভাগ (ঐচ্ছিক)",
        "scrap_crops": "বর্জ্য হিসেবে ব্যবহৃত ফসল",
        "kitchen_mat": "রান্নাঘর ও বাগানের উপাদান",
        "other_in": "অন্য কোনো বর্জ্য (যেমন: কলার খোসা, রান্না করা মুরগির হাড়)",
        "s2": "২. জৈব-নিরাপত্তা যাচাই",
        "safe_err": "জৈব-ঝুঁকি শনাক্ত ({items}): কাঁচা মাংস, দুগ্ধজাত পদার্থ, তেল বা প্লাস্টিক রোগজীবাণু ছড়ায়। এটি সরান।",
        "bone_warn": "তাপীয় প্রক্রিয়াকরণ প্রয়োজন: রান্না করা হাড় সরাসরি জলে পচাবেন না। ১০ মিনিট ফুটিয়ে তেল/মশলা দূর করুন -> আগুনে পুড়িয়ে ভস্ম/গুঁড়ো করুন।",
        "s3": "৩. মাল্টি-ক্রপ সামঞ্জস্যতা ও pH",
        "no_crop": "অনুগ্রহ করে ধাপ ১-এ অন্তত একটি ফসল নির্বাচন করুন।",
        "conflict_hdr": "ফসলের মধ্যে বিরোধপূর্ণ সম্পর্ক শনাক্ত!",
        "rescue_msg": "বিকল্প কৌশল: আলাদা বেড বা গ্রো-ব্যাগ ব্যবহার করুন এবং আলাদাভাবে সার দিন।",
        "ph_disjoint": "অসামঞ্জস্যপূর্ণ মাটির pH! ফসলগুলোর pH চাহিদা মেলে না ({low:.1f} বনাম {high:.1f})। আলাদা পাত্রে চাষ করুন।",
        "s4": "৪. মাটির pH নির্ণয়",
        "soil_mode": "pH নির্ধারণের পদ্ধতি",
        "modes": [
            "পরীক্ষিত মাটির pH (জানা মান)",
            "ভিনেগার ও বেকিং সোডা পরীক্ষা",
            "অজানা মাটি (সেফ-মোড: pH 6.5 + ১:১০ বাফার)"
        ],
        "ph_num": "মাটির pH লিখুন",
        "vinegar_q": "১. মাটিতে ভিনেগার দিলে কি বুদবুদ ওঠে?",
        "soda_q": "২. মাটিতে বেকিং সোডা ও জল দিলে কি বুদবুদ ওঠে?",
        "yes_no": ["না (No)", "হ্যাঁ (Yes)"],
        "triage_alk": "ফলাফল: ক্ষারীয় মাটি (~pH 7.8)।",
        "triage_acid": "ফলাফল: অম্লীয় মাটি (~pH 5.2)।",
        "triage_neut": "ফলাফল: নিরপেক্ষ মাটি (~pH 6.5)।",
        "safemode_info": "সেফ-মোড সক্রিয়: pH 6.5 এবং ১:১০ জলের অনুপাত নির্ধারণ করা হয়েছে।",
        "ph_warn_low": "মাটির pH ({ph}) নির্ধারিত সীমার ({low:.1f}–{high:.1f}) চেয়ে কম।",
        "ph_warn_high": "মাটির pH ({ph}) নির্ধারিত সীমার ({low:.1f}–{high:.1f}) চেয়ে বেশি।",
        "s5": "৫. অ্যাকশন কার্ড",
        "gen_btn": "রেসিপি তৈরি করুন",
        "no_scrap": "রেসিপি তৈরির আগে অন্তত একটি বর্জ্য উপাদান নির্বাচন করুন।",
        "spinner": "Gemini AI-এর মাধ্যমে রেসিপি তৈরি হচ্ছে...",
        "badge_safe": "নিরাপদ এবং সামঞ্জস্যপূর্ণ",
        "badge_rescue": "রেসকিউ মোড (পার্টিশনিং + ১:১০ বাফার আবশ্যক)"
    }
}

t = UI[st.session_state.lang]

CROPS_DB = {
    "Cereals": {"Rice (Paddy)": (5.5, 6.5), "Wheat": (6.0, 7.0), "Maize": (5.8, 6.8), "Millets": (5.5, 7.0), "Barley": (6.0, 7.5)},
    "Pulses": {"Lentil (Masur)": (6.0, 7.0), "Chickpea (Gram)": (6.0, 7.5), "Mung Bean": (6.2, 7.2), "Urad (Maskalai)": (6.0, 7.0), "Pigeon Pea": (5.5, 7.0)},
    "Oilseeds": {"Mustard": (6.0, 7.5), "Groundnut": (5.8, 6.5), "Sesame": (5.5, 7.0), "Linseed": (6.0, 7.0)},
    "Fibre Crops": {"Jute": (6.0, 7.0), "Cotton": (5.8, 7.0), "Hemp": (6.0, 7.5)},
    "Vegetables": {
        "Potato": (5.0, 6.0), "Tomato": (6.0, 6.8), "Brinjal": (5.5, 6.5),
        "Bitter Gourd": (6.0, 6.7), "Bottle Gourd": (6.0, 7.0), "Radish": (6.0, 7.0),
        "Carrot": (6.0, 6.8), "Cauliflower": (6.0, 7.0), "Onion": (6.0, 7.0),
        "Cucumber": (5.8, 6.8), "Beans": (6.0, 6.8), "Cabbage": (6.2, 7.2)
    },
    "Fruits": {"Apple": (5.8, 6.8), "Banana": (5.5, 6.5), "Guava": (5.0, 7.0), "Mango": (5.5, 7.0), "Litchi": (5.5, 6.5), "Papaya": (6.0, 6.8)},
    "Plantation & Spices": {"Tea": (4.5, 5.5), "Sugarcane": (6.0, 7.5), "Ginger": (5.5, 6.5), "Turmeric": (5.5, 6.5), "Cardamom": (5.0, 6.0)},
    "Flowers": {
        "Rose": (6.0, 6.5), "Sunflower": (6.0, 7.5), "Marigold": (6.0, 7.0),
        "Madagascar Periwinkle": (5.5, 7.0), "Arabian Jasmine": (6.0, 7.5)
    },
    "House Plants": {
        "Snake Plant": (5.5, 7.5), "Money Plant": (6.0, 7.5), "Areca Palm": (6.0, 7.5),
        "Aloe Vera": (6.0, 8.0), "Peace Lily": (5.8, 6.5), "Spider Plant": (6.0, 7.2),
        "Monstera": (5.5, 7.0), "Ferns": (5.0, 6.5), "Rubber Plant": (5.5, 7.0),
        "Lucky Bamboo": (5.5, 6.5), "Fiddle Leaf Fig": (6.0, 7.0)
    }
}

CAT_BN = {
    "Cereals": "দানাশস্য",
    "Pulses": "ডাল জাতীয়",
    "Oilseeds": "তৈলবীজ",
    "Fibre Crops": "আঁশ জাতীয় ফসল",
    "Vegetables": "সবজি",
    "Fruits": "ফল",
    "Plantation & Spices": "বাগান ফসল ও মসলা",
    "Flowers": "ফুল",
    "House Plants": "ঘরের গাছপালা"
}

CROP_BN = {
    "Rice (Paddy)": "ধান", "Wheat": "গম", "Maize": "ভুট্টা", "Millets": "মিলেট", "Barley": "যব",
    "Lentil (Masur)": "মসুর ডাল", "Chickpea (Gram)": "ছোলা", "Mung Bean": "মুগ ডাল",
    "Urad (Maskalai)": "মাসকলাই ডাল", "Pigeon Pea": "অড়হর ডাল",
    "Mustard": "সরিষা", "Groundnut": "চিনাবাদাম", "Sesame": "তিল", "Linseed": "তিসি",
    "Jute": "পাট", "Cotton": "তুলা", "Hemp": "শণ",
    "Potato": "আলু", "Tomato": "টমেটো", "Brinjal": "বেগুন", "Bitter Gourd": "করলা",
    "Bottle Gourd": "লাউ", "Radish": "মূলা", "Carrot": "গাজর", "Cauliflower": "ফুলকপি",
    "Onion": "পেঁয়াজ", "Cucumber": "শসা", "Beans": "শিম", "Cabbage": "বাঁধাকপি",
    "Apple": "আপেল", "Banana": "কলা", "Guava": "পেয়ারা", "Mango": "আম", "Litchi": "লিচু", "Papaya": "পেঁপে",
    "Tea": "চা", "Sugarcane": "আখ", "Ginger": "আদা", "Turmeric": "হলুদ", "Cardamom": "এলাচ",
    "Rose": "গোলাপ", "Sunflower": "সূর্যমুখী", "Marigold": "গাঁদা",
    "Madagascar Periwinkle": "নয়নতারা", "Arabian Jasmine": "আরবী জুঁই",
    "Snake Plant": "স্নেক প্ল্যান্ট", "Money Plant": "মানি প্ল্যান্ট", "Areca Palm": "এরিকা পাম",
    "Aloe Vera": "ঘৃতকুমারী", "Peace Lily": "পিস লিলি", "Spider Plant": "স্পাইডার প্ল্যান্ট",
    "Monstera": "মনস্টেরা", "Ferns": "ফার্ন", "Rubber Plant": "রাবার প্ল্যান্ট",
    "Lucky Bamboo": "লাকি ব্যাম্বু", "Fiddle Leaf Fig": "ফিডল লিফ ফিগ"
}

KITCHEN_BN = {
    "Vegetable Scraps": "সবজির খোসা ও টুকরো",
    "Fruit Peels": "ফলের খোসা",
    "Dry Leaves": "শুকনো পাতা",
    "Used Tea/Coffee Grounds": "ব্যবহৃত চা/কফির গুঁড়া",
    "Crushed Eggshells": "গুঁড়া ডিমের খোসা"
}

def cat_display(name):
    return CAT_BN.get(name, name) if st.session_state.lang == "বাংলা" else name

def crop_display(name):
    return CROP_BN.get(name, name) if st.session_state.lang == "বাংলা" else name

def kitchen_display(name):
    return KITCHEN_BN.get(name, name) if st.session_state.lang == "বাংলা" else name

ALL_CROP_PH = {crop: ph for cat in CROPS_DB.values() for crop, ph in cat.items()}

INCOMPATIBLE_PAIRS = [
    (
        {"Tomato", "Potato"},
        "Both share late blight (Phytophthora infestans) and compete heavily for nightshade nutrients.",
        "উভয় ফসলে লেট ব্লাইট রোগের ঝুঁকি রয়েছে এবং নাইটশেড পরিবারের ফসল হিসেবে পুষ্টির জন্য প্রতিযোগিতা করতে পারে।"
    ),
    (
        {"Onion", "Beans"},
        "Onions release root exudates that inhibit nitrogen-fixing Rhizobium bacteria on bean roots.",
        "পেঁয়াজের শিকড় থেকে নিঃসৃত কিছু পদার্থ শিমের শিকড়ে নাইট্রোজেন স্থিরকারী Rhizobium ব্যাকটেরিয়ার কার্যকলাপে বাধা দিতে পারে।"
    ),
    (
        {"Tomato", "Cabbage"},
        "Heavy brassica nitrogen uptake stunts tomato fruiting and increases pest pressure.",
        "বাঁধাকপির বেশি নাইট্রোজেন গ্রহণ টমেটোর ফল উৎপাদনে প্রভাব ফেলতে পারে এবং পোকামাকড়ের চাপ বাড়াতে পারে।"
    ),
    (
        {"Maize", "Tomato"},
        "Severe canopy shading and shared Helicoverpa fruitworm/earworm pest pressure.",
        "ভুট্টার ঘন ছায়া টমেটোর বৃদ্ধিতে প্রভাব ফেলতে পারে এবং কিছু সাধারণ ক্ষতিকর পোকার চাপ বাড়াতে পারে।"
    )
]

# Hard blocks vs items needing heat treatment (like cooked bones)
HARD_HAZARDS = [
    "cooked food", "raw meat", "fish guts", "pork", "beef", "oil", "ghee", "butter",
    "plastic", "dairy", "milk", "cheese", "paneer", "curd", "glass",
    "metal", "battery", "paint", "chemical", "feces", "faeces", "pet waste",
    "রান্না করা খাবার", "কাঁচা মাংস", "শূকরের মাংস", "গরুর মাংস", "তেল", "ঘি", "মাখন",
    "প্লাস্টিক", "দুগ্ধজাত পণ্য", "দুধ", "পনির", "ছানা", "দই", "কাচ", "কাঁচ",
    "ধাতু", "ব্যাটারি", "রাসায়নিক", "মলমূত্র", "পোষা প্রাণীর বর্জ্য"
]
THERMAL_ITEMS = ["bone", "bones", "chicken", "mutton", "হাড়"]

def matches_keyword(text, kw_list):
    found = []
    for kw in kw_list:
        pattern = rf"(?<!\w){re.escape(kw)}(?!\w)"
        if re.search(pattern, text):
            found.append(kw)
    return found

st.title(t["title"])
st.caption(t["sub"])
st.divider()

# Step 1: User Inputs
st.subheader(t["s1"])
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        selected_cats = st.multiselect(
            t["target_cat"],
            list(CROPS_DB.keys()),
            default=["Vegetables"],
            format_func=cat_display,
            key="target_cat"
        )
        available_target_crops = [c for cat in selected_cats for c in CROPS_DB[cat].keys()]
        target_crops = st.multiselect(
            t["target_crops"],
            available_target_crops,
            default=["Tomato"] if "Tomato" in available_target_crops else [],
            format_func=crop_display,
            key="target_crops"
        )

with col2:
    with st.container(border=True):
        residue_cats = [k for k in CROPS_DB.keys() if k not in ("Flowers", "House Plants")]
        scrap_cat = st.selectbox(
            t["scrap_cat"],
            residue_cats,
            index=4,
            format_func=cat_display
        )
        scrap_crops = st.multiselect(
            t["scrap_crops"],
            list(CROPS_DB[scrap_cat].keys()),
            format_func=crop_display
        )
        kitchen_materials = st.multiselect(
            t["kitchen_mat"],
            list(KITCHEN_BN.keys()),
            format_func=kitchen_display
        )
        other_material = st.text_input(t["other_in"])

all_scraps = scrap_crops + kitchen_materials
if other_material.strip():
    all_scraps.append(other_material.strip())

raw_input_str = " ".join(all_scraps).lower()

# Step 2: Safety Filter
flagged_hazards = []
for kw in HARD_HAZARDS:
    if kw in raw_input_str: 
        flagged_hazards.append(kw)

if flagged_hazards:
    st.subheader(t["s2"])
    st.error(t["safe_err"].format(items=", ".join(flagged_hazards).upper()))
    st.stop()

needs_thermal_prep = False
for item in THERMAL_ITEMS:
    if item in raw_input_str:
        needs_thermal_prep = True
        break

if needs_thermal_prep:
    st.warning(f"🔥 {t['bone_warn']}")

# Step 3: Companion & pH Overlap Math
rescue_required = False
if not target_crops:
    st.warning(t["no_crop"])
    st.stop()

selected_set = set(target_crops)
conflicts = [(pair, reason) for pair, reason in INCOMPATIBLE_PAIRS if pair.issubset(selected_set)]

lows = [ALL_CROP_PH[c][0] for c in target_crops]
highs = [ALL_CROP_PH[c][1] for c in target_crops]
intersect_low = max(lows)
intersect_high = min(highs)
ph_disjoint = intersect_low >= intersect_high

if conflicts or ph_disjoint:
    st.subheader(t["s3"])
    rescue_required = True
    if conflicts:
        st.error(t["conflict_hdr"])
        for pair, reason in conflicts:
            pair_label = " + ".join(crop_display(c) for c in pair)
            display_reason = (
                INCOMPATIBLE_REASONS_BN.get(frozenset(pair), reason)
                if st.session_state.lang == "বাংলা" else reason
            )
            st.markdown(f"- **{pair_label}:** {display_reason}")
        st.warning(t["rescue_msg"])
    if ph_disjoint:
        st.error(t["ph_disjoint"].format(low=intersect_low, high=intersect_high))

# Step 4: Soil Calibration
st.subheader(t["s4"])
with st.container(border=True):
    mode = st.radio(t["soil_mode"], t["modes"], horizontal=True)

    if mode == t["modes"][0]:
        soil_pH = st.number_input(t["ph_num"], min_value=3.0, max_value=10.0, value=6.5, step=0.1)
    elif mode == t["modes"][1]:
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            v_fizz = st.selectbox(t["vinegar_q"], t["yes_no"])
        with t_col2:
            s_fizz = st.selectbox(t["soda_q"], t["yes_no"])

        if v_fizz == t["yes_no"][1]:
            soil_pH = 7.8
            st.warning(t["triage_alk"])
        elif s_fizz == t["yes_no"][1]:
            soil_pH = 5.2
            st.warning(t["triage_acid"])
        else:
            soil_pH = 6.5
            st.caption(t["triage_neut"])
    else:
        soil_pH = 6.5
        st.caption(t["safemode_info"])

    if not ph_disjoint:
        if soil_pH < intersect_low:
            st.warning(t["ph_warn_low"].format(ph=soil_pH, low=intersect_low, high=intersect_high))
            rescue_required = True
        elif soil_pH > intersect_high:
            st.warning(t["ph_warn_high"].format(ph=soil_pH, low=intersect_low, high=intersect_high))
            rescue_required = True

# Step 5: Recipe Generation
st.subheader(t["s5"])

def get_api_key():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    try:
        return st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        return ""

@st.cache_data(ttl=3600, show_spinner=False)
def _call_gemini_cached(api_key, prompt_text):
    client = genai.Client(api_key=api_key, http_options={"timeout": 45000})
    models = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]

    for m in models:
        try:
            res = client.models.generate_content(
                model=m,
                contents=prompt_text
            )
            if res and res.text:
                return res.text, f"Gemini AI ({m})"
        except Exception:
            continue

    raise RuntimeError("All Gemini models unreachable")

def generate_recipe(api_key, prompt_text):
    try:
        return _call_gemini_cached(api_key, prompt_text)
    except Exception:
        return "", "Local Rules Fallback"

if st.button(t["gen_btn"], type="primary", use_container_width=True):
    if not all_scraps:
        st.warning(t["no_scrap"])
    else:
        api_key = get_api_key()
        is_bn = st.session_state.lang == "বাংলা"
        out_lang = "Bengali (বাংলা)" if is_bn else "English"
        rescue_note = (
            "Include root partitioning and spot-feeding instructions."
            if rescue_required else "Crops are compatible for shared bed application."
        )
        prep_method = (
            "User included cooked bones. Formulate a dry bone-char/ash protocol (boil off oil/spices -> roast/char -> crush to powder) instead of liquid steeping."
            if needs_thermal_prep else
            "Formulate an aerobic liquid steeping or composting protocol with 1:10 dilution."
        )

        prompt = f"""
        Act as an organic agronomist. Reply strictly in {out_lang}.
        Create a safe home biofertilizer guide for:
        - Crops: {', '.join(target_crops)} (Target pH: {intersect_low:.1f}-{intersect_high:.1f})
        - Current Soil pH: {soil_pH}
        - Waste Inputs: {', '.join(all_scraps)}
        - Method Note: {prep_method}
        - Co-planting Note: {rescue_note}

        Use 3 short sections with bullet points:
        ### 1. Clean (Prep & Sorting)
        ### 2. Prepare (Formulation & pH Adjustment for pH {soil_pH})
        ### 3. Feed (Dosage, Dilution & Schedule)
        """

        with st.spinner(t["spinner"]):
            recipe_text, source_label = ("", "Local Rules Fallback")
            if api_key:
                recipe_text, source_label = generate_recipe(api_key, prompt)

            if not recipe_text:
                scraps_str = ", ".join(kitchen_display(s) if s in KITCHEN_BN else crop_display(s) for s in all_scraps)
                crops_str = ", ".join(crop_display(c) for c in target_crops)

                if is_bn:
                    rescue_bn = (
                        "আলাদা পাত্রে বা গ্রো-ব্যাগে চাষ করুন এবং প্রতিটি গাছের গোড়ায় আলাদাভাবে সার দিন।"
                        if rescue_required else "ফসলগুলো একই বেডে সহ-চাষের জন্য উপযুক্ত।"
                    )
                    if needs_thermal_prep:
                        recipe_text = f"""
### ১. পরিষ্কার ও প্রস্তুতি (Clean)
- **{scraps_str}** সাধারণ জলে ১০–১৫ মিনিট ফুটিয়ে তেল, লবণ ও মশলা দূর করুন, তারপর রোদে ভালো করে শুকিয়ে নিন।

### ২. প্রস্তুত প্রণালী ও pH সমন্বয় (Prepare — pH {soil_pH})
- শুকনো হাড়গুলো উচ্চ তাপে (২২০°C তাপমাত্রায় ৪৫ মিনিট বা কয়লার আগুনে) পুড়িয়ে ভঙ্গুর করে নিন যাতে ভেতরের চর্বি নষ্ট হয়ে যায়।
- হামানদিস্তায় পিষে মিহি ক্যালসিয়াম-ফসফরাস গুঁড়ো তৈরি করুন। (মাটির pH {soil_pH} এর জন্য: {"প্রয়োগের আগে ১:৫ অনুপাতে ভিনেগারে ৭ দিন ভিজিয়ে রাখুন" if soil_pH > 7.2 else "সরাসরি মাটির উপরিভাগে মেশান"})।

### ৩. প্রয়োগ বিধি ও মাত্রা (Feed)
- **{crops_str}** গাছের জন্য প্রতি ৩০ দিন অন্তর **প্রতি গাছে ১ টেবিল চামচ** হাড়ের গুঁড়ো মাটির উপরিভাগে মিশিয়ে জল দিন। {rescue_bn}
                        """
                    else:
                        ph_tip_bn = (
                            "অম্লতা কমাতে প্রতি লিটারে ১ টেবিল চামচ গুঁড়ো ডিমের খোসা মেশান।"
                            if soil_pH < 6.0 else
                            "ক্ষারত্ব কমাতে সামান্য লেবুর খোসা বা চায়ের লিকার মেশান।"
                            if soil_pH > 7.2 else
                            "সাধারণ বায়ুচলাচলযুক্ত জল ব্যবহার করুন।"
                        )
                        recipe_text = f"""
### ১. পরিষ্কার ও বাছাই (Clean)
- **{scraps_str}** ভালোভাবে ধুয়ে লবণ বা ময়লা দূর করুন এবং ২ সেমি-এর ছোট টুকরো করে কেটে নিন।

### ২. প্রস্তুত প্রণালী ও pH সমন্বয় (Prepare — pH {soil_pH})
- ১:৩ অনুপাতে জলে ভিজিয়ে ঢাকনাযুক্ত পাত্রে ৫–৭ দিন রাখুন এবং প্রতিদিন একবার নাড়ুন। {ph_tip_bn}

### ৩. প্রয়োগ বিধি ও ১:১০ অনুপাত (Feed)
- ১ ভাগ তরল সারের সাথে ১০ ভাগ জল মেশান। **{crops_str}** গাছের গোড়ায় প্রতি ১০–১৪ দিন অন্তর ২৫০–৫০০ মিলি করে প্রয়োগ করুন। {rescue_bn}
                        """
                else:
                    if needs_thermal_prep:
                        recipe_text = f"""
### 1. Clean (Degreasing)
- Boil **{scraps_str}** in plain water for 10–15 minutes to remove cooking oil, salt, and spices, then sun-dry.

### 2. Prepare (Thermal Bone Char)
- Roast dried bones at high heat (220°C for 45 mins or over coals) until brittle to remove marrow fat.
- Crush into fine calcium-phosphorus powder. (For soil pH {soil_pH}, {"soak in 1:5 vinegar for 7 days first" if soil_pH > 7.2 else "apply directly to buffer soil"}).

### 3. Feed (Application)
- Mix **1 tbsp per plant** into topsoil every 30 days for **{crops_str}**. {rescue_note}
                        """
                    else:
                        ph_tip = (
                            "Add 1 tbsp crushed eggshells per liter to buffer acidity."
                            if soil_pH < 6.0 else
                            "Add citrus/tea steep to gently lower alkalinity."
                            if soil_pH > 7.2 else
                            "Use neutral aerated water."
                        )
                        recipe_text = f"""
### 1. Clean (Sorting & Prep)
- Rinse **{scraps_str}** to remove salt or residue and chop into <2 cm pieces.

### 2. Prepare (Aerobic Steep & pH {soil_pH})
- Steep in water (1:3 ratio) in a breathable bucket for 5–7 days, stirring daily. {ph_tip}

### 3. Feed (1:10 Dilution)
- Dilute 1 part liquid with 10 parts water. Apply 250–500 mL per plant every 10–14 days for **{crops_str}**. {rescue_note}
                        """

            with st.container(border=True):
                if rescue_required:
                    st.warning(f"**{t['badge_rescue']}**")
                else:
                    st.success(f"**{t['badge_safe']}**")
                st.caption(f"Engine: {source_label}")
                st.divider()
                st.markdown(recipe_text)