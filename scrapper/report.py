import datetime
from compare_results import compare_results_by_broken_index

RESTAURANT_CLIENTS_PER_DAY = 1785
DISERT_ORDER_PERSENT = 0.5
ICE_CREAM_ORDER_PERSENT = 0.6
ICE_CREAM_PRICE = 1.6
ICE_CREAM_REVENUE_PER_DAY = (
    RESTAURANT_CLIENTS_PER_DAY *
    DISERT_ORDER_PERSENT *
    ICE_CREAM_ORDER_PERSENT *
    ICE_CREAM_PRICE
)


def make_report(new_data: tuple,
                old_data: tuple) -> dict:
    """
    Makes report by compare new and old data,
    evaluate revenue and broken ice cream machines

    Args:
        new_data (tuple): new data
        old_data (tuple): old data

    Returns:
        dict: report
    """
    broken_machines = sum(map(lambda row: row['is_broken'],
                              new_data))
    fixes, breakdowns = compare_results_by_broken_index(new_data, old_data)
    report = {
        "datetime": datetime.datetime.now(),
        "broken_machines": broken_machines,
        "clients_count_per_day": RESTAURANT_CLIENTS_PER_DAY,
        "currency": "USD",
        "ice_cream_revenue_per_day": ICE_CREAM_REVENUE_PER_DAY,
        "overall_losses": broken_machines * ICE_CREAM_REVENUE_PER_DAY,
        "machine_fixed": len(fixes),
        "machine_breakdown": len(breakdowns),
    }
    return report, (fixes, breakdowns)
