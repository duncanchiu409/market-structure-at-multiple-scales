import pandas as pd
from dataclasses import dataclass


@dataclass
class LocalExtreme:
    ext_type: int
    index: int
    price: float
    timestamp: pd.Timestamp

    # Note: What is the difference between conf_index and index?
    conf_index: int
    conf_price: float
    conf_timestamp: pd.Timestamp

# Note: What is ext_df?
def extreme_sanity_checks(ext_df):
    if len(ext_df) < 2:
        return
    
    assert len(ext_df[ext_df['ext_type'] == ext_df['ext_type'].shift()]) == 0

    assert ext_df['index'].diff().min() >= 0

    ext_df['last'] = ext_df['price'].shift()

    high_exts = ext_df[ext_df['ext_type'] == 1]
    assert len(high_exts[high_exts['price'] <= high_exts['last']]) == 0

    low_exts = ext_df[ext_df['ext_type'] == -1]
    assert len(low_exts[low_exts['price'] >= low_exts['last']]) == 0