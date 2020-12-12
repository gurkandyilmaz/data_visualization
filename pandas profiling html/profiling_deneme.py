import pandas as pd
import numpy as np
from pandas_profiling import ProfileReport
# import pandas_profiling

print("pandas version:", pd.__version__)

df = pd.DataFrame(np.random.rand(100,3), columns=["a","b","c"])
profile = ProfileReport(df, title="Deneme")