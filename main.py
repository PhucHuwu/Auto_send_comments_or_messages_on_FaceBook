from itertools import cycle
import pandas as pd

df_list_via = pd.read_csv('via.csv')
df_list_via = df_list_via[~df_list_via["Status"].isin(["Checkpoint", "Invalid", "Wrong password"])]
list_via = df_list_via["Via"].dropna().tolist()

num_threads = 2

num_vias = len(list_via)
via_chunks = [[] for _ in range(num_threads)]
via_cycle = cycle(range(num_threads))

for i, via in enumerate(list_via):
    via_chunks[next(via_cycle)].append(via)

for i in via_chunks:
    print(i)