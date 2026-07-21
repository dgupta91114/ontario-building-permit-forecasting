import pandas as pd

from capstone.cleaning import clean_building_permits, clean_unemployment


def _cfg():
    return {
        "project": {
            "start_date": "2018-01-01",
            "end_date": "2018-03-01",
            "selected_cmas": {
                "Toronto": {"patterns": ["toronto"]},
                "Hamilton": {"patterns": ["hamilton"]},
                "Kitchener-Cambridge-Waterloo": {"patterns": ["kitchener", "cambridge", "waterloo"]},
                "London": {"patterns": ["london"]},
                "Windsor": {"patterns": ["windsor"]},
            },
        },
        "filters": {
            "building_permits": {
                "seasonal_adjustment": {"exact_candidates": ["Seasonally adjusted"], "required_tokens": ["seasonally", "adjusted"], "forbidden_tokens": ["unadjusted"]},
                "value_type": {"exact_candidates": ["Current dollars"], "required_tokens": ["current", "dollar"], "forbidden_tokens": ["constant"]},
                "type_of_structure": {"exact_candidates": ["Residential structures, total"], "required_tokens": ["residential", "total"], "forbidden_tokens": ["non-residential"]},
                "type_of_work": {"exact_candidates": ["Types of work, total"], "required_tokens": ["total"], "forbidden_tokens": []},
            },
            "unemployment": {
                "geography_exact_candidates": ["Ontario"],
                "labour_force_characteristic_exact_candidates": ["Unemployment rate"],
                "data_type_exact_candidates": ["Seasonally adjusted"],
                "gender_exact_candidates": ["Total, gender"],
                "age_group_exact_candidates": ["15 years and over"],
            },
        },
    }


def test_building_permit_filtering_returns_one_row_per_cma_month():
    geos = ["Toronto, Ontario", "Hamilton, Ontario", "Kitchener - Cambridge - Waterloo, Ontario", "London, Ontario", "Windsor, Ontario"]
    rows = []
    for date in ["2018-01", "2018-02", "2018-03"]:
        for i, geo in enumerate(geos):
            rows.append({
                "REF_DATE": date, "GEO": geo, "DGUID": f"D{i}",
                "Seasonal adjustment": "Seasonally adjusted", "Value type": "Current dollars",
                "Type of structure": "Residential structures, total", "Type of work": "Types of work, total",
                "VALUE": 100 + i, "STATUS": ""
            })
    raw = pd.DataFrame(rows)
    clean, report = clean_building_permits(_cfg(), df=raw)
    assert len(clean) == 15
    assert clean.duplicated(["cma", "ref_date"]).sum() == 0
    assert set(clean["cma"]) == set(_cfg()["project"]["selected_cmas"])


def test_unemployment_filtering():
    raw = pd.DataFrame({
        "REF_DATE": ["2018-01", "2018-02", "2018-03"],
        "GEO": ["Ontario"] * 3,
        "Labour force characteristics": ["Unemployment rate"] * 3,
        "Data type": ["Seasonally adjusted"] * 3,
        "Gender": ["Total, gender"] * 3,
        "Age group": ["15 years and over"] * 3,
        "VALUE": [6.0, 6.1, 6.2],
    })
    clean, _ = clean_unemployment(_cfg(), df=raw)
    assert list(clean["ontario_unemployment_rate"]) == [6.0, 6.1, 6.2]
