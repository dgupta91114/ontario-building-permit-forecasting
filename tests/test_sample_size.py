from capstone.sample_size import calculate_sample_sizes


def test_sample_sizes_match_synopsis_assumptions():
    table = calculate_sample_sizes().set_index("research_question")
    assert table.loc["RQ1", "minimum_n"] == 85
    assert table.loc["RQ2", "minimum_n"] == 118
    assert table.loc["RQ3", "minimum_n"] == 67
    assert table.loc["RQ4", "minimum_n"] == 196
