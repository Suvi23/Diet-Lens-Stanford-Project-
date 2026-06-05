# verdict_checker.py
# D:\DietLens2026\verdict_checker.py
#
# This file does ONE job:
# Take the ingredient list extracted by AI
# and check it against forbidden ingredient lists
# Python decides the verdict - NOT the AI
# This guarantees 100% consistent results every time


# ── FORBIDDEN INGREDIENT LISTS ───────────────────────────────────────
# Each condition has a list of forbidden keywords
# If ANY keyword is found in the ingredient list → FAIL

CONDITION_RULES = {

    "Diabetic": {
        "label": "Diabetic",
        "forbidden": [
            "sugar", "added sugar", "total sugar", "cane sugar",
            "brown sugar", "raw sugar", "powdered sugar",
            "corn syrup", "high fructose corn syrup", "hfcs",
            "maltodextrin", "dextrose", "fructose", "glucose",
            "sucrose", "barley malt", "malt syrup",
            "honey", "agave", "molasses", "maple syrup",
            "fruit juice concentrate", "invert sugar",
            "turbinado", "treacle", "golden syrup",
            "rice syrup", "coconut sugar", "date sugar"
        ]
    },

    "Gluten Free": {
        "label": "Gluten Free",
        "forbidden": [
            "wheat", "wheat flour", "wheat starch",
            "whole wheat", "wheat bran", "wheat germ",
            "barley", "barley malt", "barley flour",
            "rye", "rye flour",
            "malt", "malt extract", "malt vinegar", "malt flavoring",
            "brewer's yeast", "brewers yeast",
            "semolina", "spelt", "kamut", "triticale",
            "durum", "einkorn", "emmer", "farro"
        ]
    },

    "Nut Allergy": {
        "label": "Nut Allergy",
        "forbidden": [
            "peanut", "peanuts", "peanut oil", "peanut butter",
            "peanut flour", "groundnut", "groundnuts",
            "almond", "almonds", "almond flour", "almond oil",
            "almond extract", "almond milk",
            "cashew", "cashews", "cashew oil",
            "walnut","chopped walnuts", "walnuts", "walnut oil",
            "pecan", "pecans",
            "pistachio", "pistachios",
            "macadamia", "macadamia nut",
            "hazelnut", "hazelnuts", "hazelnut oil",
            "brazil nut", "brazil nuts",
            "pine nut", "pine nuts", "pinon",
            "nut oil", "nut extract", "mixed nuts",
            "tree nut", "tree nuts", "nut butter"
        ]
    },

    "Dairy Free": {
        "label": "Dairy Free",
        "forbidden": [
            "milk", "whole milk", "skim milk", "low fat milk",
            "milk solids", "milk powder", "dried milk",
            "butter", "butter oil", "butterfat",
            "cream", "heavy cream", "sour cream",
            "half and half", "buttermilk",
            "cheese", "cheddar", "mozzarella", "parmesan",
            "whey", "whey protein", "whey powder",
            "casein", "caseinate", "sodium caseinate",
            "lactose", "lactalbumin", "lactoglobulin",
            "ghee", "curd", "lassi", "yogurt",
            "ice cream", "milk fat", "dairy"
        ]
    },

    "Vegan": {
        "label": "Vegan",
        "forbidden": [
            # Dairy
            "milk", "butter", "cream", "cheese",
            "whey", "casein", "lactose", "ghee", "dairy",
            # Eggs - NOT vegan
            "egg", "eggs", "whole egg", "egg white",
            "egg yolk", "egg powder", "dried egg",
            "egg solids", "albumen", "ovalbumin", "lysozyme",
            # Honey and bee products
            "honey", "beeswax", "royal jelly", "propolis",
            # Gelatin and collagen
            "gelatin", "gelatine", "collagen",
            # Dyes and shellac
            "carmine", "cochineal", "e120", "shellac",
            # Animal fats
            "lard", "tallow", "suet", "lanolin",
            # Meat and seafood
            "chicken", "beef", "pork", "lamb", "turkey",
            "fish", "salmon", "tuna", "anchovies",
            "shrimp", "oyster", "meat", "bone broth"
        ]
    },

    "Vegetarian": {
        "label": "Vegetarian",
        "forbidden": [
            # ── EGGS - NOT vegetarian ──────────────────────────────
            # This is the main fix for your egg problem
            "egg", "eggs", "whole egg", "egg white",
            "egg yolk", "egg powder", "dried egg",
            "egg solids", "albumen", "ovalbumin",
            "lysozyme", "mayonnaise",

            # ── MEAT AND POULTRY ───────────────────────────────────
            "beef", "chicken", "pork", "lamb",
            "turkey", "duck", "goose", "veal",
            "meat", "meat extract", "meat powder",
            "chicken broth", "beef broth", "bone broth",
            "bacon", "ham", "sausage",
            "lard", "tallow", "suet",
            "chicken fat", "beef fat", "pork fat",

            # ── SEAFOOD ────────────────────────────────────────────
            "fish", "salmon", "tuna", "cod", "tilapia",
            "shrimp", "prawn", "crab", "lobster",
            "oyster", "squid", "octopus", "clam",
            "anchovies", "sardine", "mackerel",
            "fish sauce", "fish oil", "fish extract",
            "oyster sauce", "shrimp paste","scallop", "mussel", "fillet", "fillets","haddock", "pollock","anchovy","trout", "halibut", "snapper","sea bass", "bass", "catfish","fish fillet", "fish fillets",

            # ── ANIMAL DERIVATIVES ─────────────────────────────────
            "gelatin", "gelatine", "collagen",
            "carmine", "cochineal", "e120",
            "shellac", "isinglass", "rennet",
            "animal fat", "fish sauce", "fish oil", 
            "fish extract","oyster sauce", "shrimp paste",
            "seafood","animal shortening"
        ]
    },

    "No HFCS": {
        "label": "No HFCS",
        "forbidden": [
            "high fructose corn syrup", "hfcs",
            "corn syrup high fructose",
            "fructose corn syrup",
            "high-fructose corn syrup"
        ]
    },

    "Low Sodium": {
        "label": "Low Sodium",
        # Low Sodium is special - handled separately by amount check
        # not by keyword matching
        "forbidden": [],
        "special": "sodium_check"
    },

}


# ── MAIN VERDICT FUNCTION ────────────────────────────────────────────

def check_verdict(ai_response_text, user_conditions, sodium_amount=None):
    """
    Takes the AI extracted ingredient text and user conditions.
    Python checks each condition and returns a guaranteed verdict.

    Parameters:
        ai_response_text : str  - full AI response text
        user_conditions  : list - conditions user selected
        sodium_amount    : int  - optional, sodium in mg if known

    Returns:
        dict with full verdict details
    """

    if not user_conditions:
        return {
            "conditions_checked": [],
            "failures": [],
            "overall": "NO_CONDITIONS",
            "verdict_text": build_no_conditions_verdict()
        }

    # Convert AI response to lowercase for matching
    # This makes matching case-insensitive
    text_lower = ai_response_text.lower()

    conditions_checked = []
    any_failure = False

    for condition in user_conditions:

        if condition not in CONDITION_RULES:
            continue

        rule = CONDITION_RULES[condition]

        # ── Special handling for Low Sodium ─────────────────────
        if rule.get("special") == "sodium_check":
            result = check_sodium(text_lower, sodium_amount)
            conditions_checked.append(result)
            if result["status"] == "FAIL":
                any_failure = True
            continue

        # ── Standard keyword matching for other conditions ───────
        result = check_condition_keywords(
            condition_name=condition,
            label=rule["label"],
            forbidden_list=rule["forbidden"],
            text_lower=text_lower
        )
        conditions_checked.append(result)
        if result["status"] == "FAIL":
            any_failure = True

    # ── Build the final verdict text ─────────────────────────────
    verdict_text = build_verdict_text(conditions_checked, any_failure)

    return {
        "conditions_checked": conditions_checked,
        "any_failure": any_failure,
        "verdict_text": verdict_text
    }


def check_condition_keywords(condition_name, label, forbidden_list, text_lower):
    """
    Robust ingredient checking.
    Vegetarian is handled fully and independently.
    """

    import re

    found_ingredients = []

    # ─────────────────────────────────────────────
    # Extract ONLY INGREDIENTS FOUND section
    # ─────────────────────────────────────────────

    ingredient_section = ""

    if "ingredients found:" in text_lower:
        start = text_lower.find("ingredients found:")
        ingredient_section = text_lower[start:]

        stop_keywords = [
            "allergen check:",
            "fats and oils:",
            "food additives:",
            "harmful preservatives:",
            "artificial colours:",
            "warnings:",
            "fda compliance:"
        ]

        for stop_word in stop_keywords:
            stop_index = ingredient_section.find(stop_word)
            if stop_index != -1:
                ingredient_section = ingredient_section[:stop_index]
                break
    else:
        ingredient_section = text_lower

    lines = ingredient_section.split("\n")

    # ─────────────────────────────────────────────
    # ✅ COMPLETE VEGETARIAN LOGIC (FINAL VERSION)
    # ─────────────────────────────────────────────

    if condition_name == "Vegetarian":

        animal_keywords = [

            # ✅ Eggs (CRITICAL FIX)
            "egg", "eggs", "whole egg", "egg white",
            "egg yolk", "egg powder", "egg solids",
            "albumen", "ovalbumin",

            # ✅ Fish & Seafood
            "fish", "fillet", "fillets",
            "haddock", "cod", "salmon", "tuna",
            "mackerel", "sardine", "anchovy",
            "shrimp", "prawn", "crab", "lobster",
            "oyster", "squid", "octopus", "clam",

            # ✅ Meat & Poultry
            "chicken", "beef", "pork", "lamb",
            "turkey", "duck", "goose",
            "meat", "bacon", "ham", "sausage",

            # ✅ Animal derivatives
            "gelatin", "gelatine", "collagen",
            "animal fat", "animal shortening"
        ]

        for line in lines:

            line_clean = line.strip()

            if not line_clean:
                continue

            for keyword in animal_keywords:

                pattern = r"\b" + re.escape(keyword) + r"\b"

                if re.search(pattern, line_clean):

                    return {
                        "condition": label,
                        "status": "FAIL",
                        "found": [keyword],
                        "message": f"Found: {keyword}"
                    }

        return {
            "condition": label,
            "status": "PASS",
            "found": [],
            "message": "No animal-derived ingredients detected"
        }
             # ─────────────────────────────────────────────
       # ✅ COMPLETE VEGAN LOGIC (ROBUST VERSION)
       # ─────────────────────────────────────────────

    if condition_name == "Vegan":

        vegan_forbidden_keywords = [

            # 🥛 Dairy
            "milk", "butter", "cream", "cheese",
            "whey", "casein", "lactose", "ghee",
            "yogurt", "yoghurt", "curd",
            "milk powder", "milk solids",

            # 🥚 Eggs
            "egg", "eggs", "whole egg", "egg white",
            "egg yolk", "egg powder", "egg solids",
            "albumen", "ovalbumin", "lysozyme",

            # 🍯 Honey & bee products
            "honey", "beeswax", "royal jelly",
            "propolis",

            # 🐟 Fish & Seafood
            "fish", "fillet", "fillets",
            "haddock", "cod", "salmon", "tuna",
            "shrimp", "prawn", "crab", "lobster",
            "oyster", "squid", "octopus", "clam",
            "fish sauce", "fish oil",

            # 🍖 Meat & Poultry
            "chicken", "beef", "pork", "lamb",
            "turkey", "duck", "goose",
            "meat", "bacon", "ham", "sausage",

            # 🧪 Animal-derived additives
            "gelatin", "gelatine", "collagen",
            "carmine", "cochineal", "e120",
            "shellac", "e904", "lanolin",
            "lard", "tallow", "suet",
            "animal fat", "animal shortening"
        ]

        for line in lines:

            line_clean = line.strip()

            if not line_clean:
                continue

            for keyword in vegan_forbidden_keywords:

                pattern = r"\b" + re.escape(keyword) + r"\b"

                if re.search(pattern, line_clean):

                    return {
                        "condition": label,
                        "status": "FAIL",
                        "found": [keyword],
                        "message": f"Found: {keyword}"
                    }

        return {
            "condition": label,
            "status": "PASS",
            "found": [],
            "message": "No animal-derived ingredients detected"
        }

    # ─────────────────────────────────────────────
    # ✅ NORMAL MATCHING FOR OTHER CONDITIONS
    # ─────────────────────────────────────────────

    for line in lines:

        line_clean = line.strip()

        if not line_clean:
            continue

        for keyword in forbidden_list:

            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

            if re.search(pattern, line_clean):
                if line_clean not in found_ingredients:
                    found_ingredients.append(line_clean)
                break

    if found_ingredients:
        return {
            "condition": label,
            "status": "FAIL",
            "found": found_ingredients,
            "message": f"Found: {', '.join(found_ingredients)}"
        }

    return {
        "condition": label,
        "status": "PASS",
        "found": [],
        "message": "No forbidden ingredients detected"
    }

def check_sodium(text_lower, sodium_amount=None):
    """
    Special check for Low Sodium condition.
    Tries to extract sodium amount from text if not provided.
    """

    limit = 140  # mg per serving

    # If sodium amount was passed directly, use it
    if sodium_amount is not None:
        if sodium_amount > limit:
            return {
                "condition": "Low Sodium",
                "status": "FAIL",
                "found": [f"Sodium {sodium_amount}mg"],
                "message": f"Sodium is {sodium_amount}mg (exceeds {limit}mg limit)"
            }
        else:
            return {
                "condition": "Low Sodium",
                "status": "PASS",
                "found": [],
                "message": f"Sodium is {sodium_amount}mg (within {limit}mg limit)"
            }

    # Try to extract sodium number from AI text automatically
    import re

    # Look for patterns like "sodium: 160mg" or "sodium 160 mg"
    patterns = [
        r'sodium[:\s]+(\d+)\s*mg',
        r'sodium content[:\s]+(\d+)\s*mg',
        r'(\d+)\s*mg\s*sodium',
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            found_sodium = int(match.group(1))
            if found_sodium > limit:
                return {
                    "condition": "Low Sodium",
                    "status": "FAIL",
                    "found": [f"Sodium {found_sodium}mg"],
                    "message": (
                        f"Sodium is {found_sodium}mg "
                        f"(exceeds your {limit}mg limit)"
                    )
                }
            else:
                return {
                    "condition": "Low Sodium",
                    "status": "PASS",
                    "found": [],
                    "message": (
                        f"Sodium is {found_sodium}mg "
                        f"(within your {limit}mg limit)"
                    )
                }

    # Could not find sodium amount in text
    return {
        "condition": "Low Sodium",
        "status": "UNKNOWN",
        "found": [],
        "message": "Sodium amount not found on label"
    }


def build_verdict_text(conditions_checked, any_failure):
    """
    Build the formatted verdict text to display in the app.
    This is 100% Python - no AI involved.
    """

    lines = []

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("           YOUR PERSONAL VERDICT")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("CONDITIONS CHECKED:")
    lines.append("─" * 40)

    failed_conditions = []
    passed_conditions = []

    for result in conditions_checked:
        condition = result["condition"]
        status = result["status"]
        message = result["message"]

        if status == "FAIL":
            lines.append(f"  ❌ {condition}: FAIL")
            lines.append(f"     → {message}")
            failed_conditions.append(condition)

        elif status == "PASS":
            lines.append(f"  ✅ {condition}: PASS")
            lines.append(f"     → {message}")
            passed_conditions.append(condition)

        elif status == "UNKNOWN":
            lines.append(f"  ⚠️  {condition}: UNKNOWN")
            lines.append(f"     → {message}")

        lines.append("")

    # ── Reason section ───────────────────────────────────────────
    lines.append("─" * 40)
    lines.append("REASON:")

    if failed_conditions:
        for result in conditions_checked:
            if result["status"] == "FAIL":
                for ingredient in result["found"]:
                    ingredient_clean = (
                    ingredient
                    .replace("-", "")
                    .replace("•", "")
                    .strip()
                    )
                    lines.append(
                      f"  • {ingredient_clean} violates "
                      f"{result['condition']} condition"
                    )
    else:
        lines.append("  All your conditions passed.")

    lines.append("")

    # ── Final verdict ────────────────────────────────────────────
    lines.append("─" * 40)
    lines.append("FINAL VERDICT:")
    lines.append("")

    if any_failure:
        lines.append("  ❌ NOT SAFE FOR YOU")
        lines.append("")
        lines.append(
            f"  This product is NOT safe because it violates "
            f"your {', '.join(failed_conditions)} condition(s)."
        )
    else:
        lines.append("  ✅ SAFE FOR YOU")
        lines.append("")
        lines.append(
            "  This product appears safe based on "
            "your selected conditions."
        )

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


def build_no_conditions_verdict():
    """Verdict text when no conditions are selected"""
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "           YOUR PERSONAL VERDICT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "  No dietary conditions selected.\n\n"
        "  Please select at least one condition\n"
        "  on the left panel to get a personal verdict.\n\n"
        "  Check the FDA COMPLIANCE section above\n"
        "  for general nutritional information.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )