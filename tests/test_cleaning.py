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


def test_official_combined_permit_schema():
    geos = ["Toronto, Ontario", "Hamilton, Ontario", "Kitchener-Cambridge-Waterloo, Ontario", "London, Ontario", "Windsor, Ontario"]
    raw = pd.DataFrame({
        "REF_DATE": ["2018-01"] * 5,
        "GEO": geos,
        "DGUID": [f"D{i}" for i in range(5)],
        "Type of building": ["Total residential"] * 5,
        "Type of work": ["Types of work, total"] * 5,
        "Variables": ["Value of permits"] * 5,
        "Seasonal adjustment, value type": ["Seasonally adjusted, current"] * 5,
        "UOM": ["Dollars"] * 5,
        "SCALAR_FACTOR": ["thousands"] * 5,
        "VALUE": [100, 200, 300, 400, 500],
        "STATUS": [""] * 5,
    })
    cfg = _cfg()
    cfg["filters"]["building_permits"]["seasonal_adjustment_value_type"] = {
        "current": {"exact_candidates": ["Seasonally adjusted, current"], "required_tokens": ["seasonally", "adjusted", "current"], "forbidden_tokens": ["unadjusted", "constant"]}
    }
    cfg["filters"]["building_permits"]["type_of_structure"]["exact_candidates"].insert(0, "Total residential")
    cfg["filters"]["building_permits"]["variable"] = {"exact_candidates": ["Value of permits"], "required_tokens": ["value", "permit"], "forbidden_tokens": ["number"]}
    clean, report = clean_building_permits(cfg, df=raw)
    assert len(clean) == 5
    assert report["source_schema"] == "combined seasonal adjustment/value type"


def test_unemployment_uses_estimates_not_standard_errors():
    raw = pd.DataFrame({
        "REF_DATE": ["2018-01", "2018-01"],
        "GEO": ["Ontario", "Ontario"],
        "Labour force characteristics": ["Unemployment rate"] * 2,
        "Data type": ["Seasonally adjusted"] * 2,
        "Gender": ["Total, gender"] * 2,
        "Age group": ["15 years and over"] * 2,
        "Statistics": ["Estimate", "Standard error of estimate"],
        "VALUE": [6.0, 0.2],
    })
    cfg = _cfg()
    cfg["filters"]["unemployment"]["statistics_exact_candidates"] = ["Estimate"]
    clean, report = clean_unemployment(cfg, df=raw)
    assert list(clean["ontario_unemployment_rate"]) == [6.0]
    assert report["chosen_labels"]["statistics"] == "Estimate"
