from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

YEAR = 2026
HOTEL_DEFAULT = 80


def get_price(value):
    """Преобразование строки цены в число."""
    if not value:
        return None

    value = str(value).strip()

    if value.upper() == "X":
        return None

    if "-" in value:
        low, high = map(float, value.split("-"))
        return (low + high) / 2

    return float(value)


def find_options(city_name, to_data, from_data, hotel_price=HOTEL_DEFAULT):
    options = []

    for day_out, price_out_str in to_data.items():
        for day_back, price_back_str in from_data.items():

            price_out = get_price(price_out_str)
            price_back = get_price(price_back_str)

            if price_out is None or price_back is None:
                continue

            # Вылет: 31 июля или 1–7 августа
            if day_out == 31:
                out_date = datetime(YEAR, 7, 31)
            else:
                out_date = datetime(YEAR, 8, day_out)

            # Возврат: август
            back_date = datetime(YEAR, 8, day_back)

            days = (back_date - out_date).days

            # Отсеиваем некорректные даты
            if days < 0:
                continue

            # По условию 5–10 дней
            if 5 <= days <= 10:

                flight_total = (price_out + price_back) * 2

                # Ночей обычно на одну меньше чем дней поездки
                hotel_cost = max(0, days - 1) * hotel_price

                total = flight_total + hotel_cost

                options.append({
                    "city": city_name,
                    "out": out_date.strftime("%Y-%m-%d"),
                    "back": back_date.strftime("%Y-%m-%d"),
                    "days": days,
                    "flight_total": round(flight_total, 2),
                    "hotel_cost": round(hotel_cost, 2),
                    "total": round(total, 2)
                })

    return options


cities = [
    {
        "name": "Barcelona",
        "to": {
            31: "30",
            1: "78",
            2: "50",
            3: "40",
            4: "22",
            5: "22-41",
            6: "34",
            7: "21"
        },
        "from": {
            7: "35",
            8: "96",
            9: "63",
            10: "39",
            11: "33",
            12: "29",
            13: "23",
            14: "40"
        },
        "hotel": 80
    },
    {
        "name": "Valencia",
        "to": {
            31: "41",
            1: "91",
            2: "64",
            3: "X",
            4: "51",
            5: "24",
            6: "X",
            7: "52"
        },
        "from": {
            7: "74",
            8: "83",
            9: "68",
            10: "X",
            11: "76",
            12: "74",
            13: "X",
            14: "167"
        },
        "hotel": 80
    }
]


def print_top_options(options, limit=10):
    print(f"\nTOP {min(limit, len(options))} OPTIONS:\n")

    for i, opt in enumerate(options[:limit], start=1):
        print(f"{i}. {opt['city']}")
        print(f"   Out:      {opt['out']}")
        print(f"   Back:     {opt['back']}")
        print(f"   Days:     {opt['days']}")
        print(f"   Flights:  €{opt['flight_total']:.2f}")
        print(f"   Hotel:    €{opt['hotel_cost']:.2f}")
        print(f"   TOTAL:    €{opt['total']:.2f}")
        print("-" * 40)


def get_color(value, median):
    diff_percent = ((value - median) / median) * 100

    if diff_percent <= -20:
        return "#2ca02c"      # green
    elif diff_percent <= -5:
        return "#bcbd22"      # olive
    elif diff_percent <= 15:
        return "#ff7f0e"      # orange
    return "#d62728"          # red


def show_charts(top_options, show_pie=True, show_scatter=False):
    if not top_options:
        return

    totals = [opt["total"] for opt in top_options]
    days = [opt["days"] for opt in top_options]

    median = np.median(totals)
    colors = [get_color(v, median) for v in totals]

    if show_pie:
        labels = [
            f"{opt['city']} €{opt['total']:.0f}"
            for opt in top_options
        ]

        plt.figure(figsize=(10, 8))
        plt.pie(
            totals,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90
        )
        plt.title("Trip Cost Distribution")
        plt.tight_layout()
        plt.show()

    if show_scatter:
        plt.figure(figsize=(8, 6))

        sizes = [max(50, 500000 / (v ** 2)) for v in totals]

        plt.scatter(
            days,
            totals,
            c=colors,
            s=sizes,
            alpha=0.8
        )

        for i, opt in enumerate(top_options):
            plt.annotate(
                opt["city"],
                (days[i], totals[i]),
                xytext=(5, 5),
                textcoords="offset points"
            )

        plt.xlabel("Trip Length (days)")
        plt.ylabel("Total Cost (€)")
        plt.title("Trip Value Analysis")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":

    all_options = []

    for city in cities:
        all_options.extend(
            find_options(
                city["name"],
                city["to"],
                city["from"],
                city["hotel"]
            )
        )

    all_options.sort(key=lambda x: x["total"])

    print_top_options(all_options)

    SHOW_PIE = True
    SHOW_SCATTER = False

    show_charts(
        all_options[:10],
        show_pie=SHOW_PIE,
        show_scatter=SHOW_SCATTER
    )