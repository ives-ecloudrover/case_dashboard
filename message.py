import pandas as pd
import numpy as np
data=pd.read_csv("./case_list.csv")
#print(data)
col_1=data["instance_id"]
data=np.array(col_1)
print(data)