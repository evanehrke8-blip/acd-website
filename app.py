

from flask import Flask, request, render_template
import urllib.parse
import os
from datetime import datetime

app = Flask(__name__)

def generate_ref():
    file = "ref.txt"

    if not os.path.exists(file):
        with open(file, "w") as f:
            f.write("1")

    with open(file, "r") as f:
        number = int(f.read())

    new_number = number + 1

    with open(file, "w") as f:
        f.write(str(new_number))

    year = datetime.now().year

    return f"Q-{year}-{str(number).zfill(4)}"

def save_lead(data):
    with open("leads.txt", "a") as f:
        f.write(data + "\n" + "-" * 40 + "\n")

@app.route("/", methods=["GET", "POST"])
def home():

    price_low = 0
    price_high = 0

    whatsapp = ""
    whatsapp_visit = ""

    breakdown_html = ""

    if request.method == "POST":

        products = request.form.getlist("product")
        colours = request.form.getlist("colour")
        widths = request.form.getlist("width")
        heights = request.form.getlist("height")
        qtys = request.form.getlist("qty")

        pricing = {
            "Single Hinge Door": (3200, 4200),
            "Double Hinge Door": (2600, 4000),
            "Sliding Door (Heavy Duty)": (2800, 3800),
            "Sliding Door (Light Duty)": (2200, 3000),
            "Pivot Door": (4000, 4600),
            "Folding Door (3 Leaf)": (2800, 3600),
            "Folding Door (5 Leaf)": (2800, 3800),
            "Folding Door (7 Leaf)": (2900, 3900),
            "Top Hung Window": (1600, 3000),
            "Side Hung Window": (1800, 2600),
            "Sliding Window": (1700, 2600),
            "Stacking Window": (3000, 4500),
            "Fixed Panel / Shopfront": (3000, 4500)
        }

        details = ""

        for i in range(len(products)):

            if widths[i] and heights[i]:

                w = float(widths[i]) / 1000
                h = float(heights[i]) / 1000
                q = int(qtys[i]) if qtys[i] else 1

                area = w * h * q

                min_rate, max_rate = pricing.get(
                    products[i],
                    (2000, 3000)
                )

                low = area * min_rate
                high = area * max_rate

                if colours[i] == "Natural":
                    low *= 1.15
                    high *= 1.15

                price_low += low
                price_high += high

                low_i = int(low)
                high_i = int(high)

                details += f"""• {products[i]} ({w:.2f}m × {h:.2f}m) x{q}
  R{low_i:,} – R{high_i:,}

"""

                breakdown_html += f"""
                <div class="breakdown-item">
                    <strong>{products[i]}</strong><br>
                    R{low_i:,} - R{high_i:,}
                </div>
                """

        price_low = int(price_low)
        price_high = int(price_high)

        ref = generate_ref()

        msg = f"""*ACD ESTIMATOR REQUEST*

Ref: {ref}

*Client Details*
Name: {request.form['name']}
Phone: {request.form['phone']}
Area: {request.form['area']}

*Project Items*
{details}

*Total Estimate*
R{price_low:,} – R{price_high:,}
"""

        visit_msg = f"""*SITE VISIT REQUEST*

Hi, I would like to book a site visit.

Ref: {ref}

Name: {request.form['name']}
Phone: {request.form['phone']}
Area: {request.form['area']}

Please advise your next available time.
"""

        whatsapp = (
            "https://wa.me/27791532379?text="
            + urllib.parse.quote(msg)
        )

        whatsapp_visit = (
            "https://wa.me/27791532379?text="
            + urllib.parse.quote(visit_msg)
        )

        save_lead(msg)

    return render_template(
        "home.html",
        price_low=price_low,
        price_high=price_high,
        whatsapp=whatsapp,
        whatsapp_visit=whatsapp_visit,
        breakdown=breakdown_html
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
