import pandas as pd
import numpy as np
from local_extreme import LocalExtreme, extreme_sanity_checks

class ATRDirectionalChange:
    def __init__(self, atr_lookback: int):
        self._up_move = True
        self._pend_max = np.nan # Note: type == np.float?
        self._pend_min = np.nan # Note: type == np.float?
        self._pend_max_i = 0
        self._pend_min_i = 0

        self._atr_lb = atr_lookback
        self._atr_sum = np.nan
        self.extremes = []

    # Note: What does _create_ext do?
    def _create_ext(self, ext_type: str, ext_i: int, conf_i: int, time_index: pd.DatetimeIndex, high: np.array, low: np.array, close: np.array):
        if ext_type == 'high':
            ext_type = 1
            arr = high
        else:
            ext_type = -1
            arr = low

        ext = LocalExtreme(ext_type=ext_type, index=ext_i, price=arr[ext_i], timestamp=time_index[ext_i], conf_index=conf_i, conf_price=arr[conf_i], conf_timestamp=time_index[conf_i])

        self.extremes.append(ext)

    def update(self, i: int, time_index: pd.DatetimeIndex, high: np.array, low: np.array, close: np.array):
        # Compute ATR
        if i < self._atr_lb:
            return
        elif i == self._atr_lb:
            h_window = high[i - self._atr_lb + 1: i+1]
            l_window = low[i - self._atr_lb + 1: i+1]
            c_window = close[i - self._atr_lb: i]

            tr1 = h_window - l_window
            tr2 = h_window - c_window
            tr3 = l_window - c_window

            self._atr_sum = np.sum(np.max(np.stack([tr1, tr2, tr3]), axis=0))
        else:
            tr_val_curr = max(
                high[i] - low[i],
                abs(high[i] - close[i-1]),
                abs(low[i] - close[i-1])
            )

            rm_i = i - self._atr_lb

            tr_val_remove = max(
                high[rm_i] - low[rm_i],
                abs(high[rm_i] - close[rm_i-1]),
                abs(low[rm_i] - close[rm_i-1])
            )

            self._atr_sum += tr_val_curr
            self._atr_sum -= tr_val_remove

            atr = self._atr_sum / self._atr_lb
            self._curr_atr = atr

            # Note: initailization for parameters
            if np.isnan(self._pend_max):
                self._pend_max = high[i]
                self._pend_min = low[i]
                self._pend_max_i = self._pend_min_i = i

            if self._up_move:
                if high[i] > self._pend_max:
                    self._pend_max = high[i]
                    self._pend_max_i = i
                elif low[i] < self._pend_max - atr:
                    self._create_ext(ext_type='high', ext_i=self._pend_max_i, conf_i=i, time_index=time_index, high=high, low=low, close=close)

                    self._up_move = False
                    self._pend_min = low[i]
                    self._pend_min_i = i
            else:
                if low[i] < self._pend_min:
                    self._pend_min = low[i]
                    self._pend_min_i = i
                elif high[i] > self._pend_min + atr:
                    self._create_ext(ext_type='low', ext_i=self._pend_min_i, conf_i=i, time_index=time_index, high=high, low=low, close=close)

                    self._up_move = True
                    self._pend_max = high[i]
                    self._pend_max_i = i